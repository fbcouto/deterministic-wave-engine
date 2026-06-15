use wgpu::util::DeviceExt;

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
struct Vortex {
    pos: [f32; 2],
    vel: [f32; 2],
    spin: f32,
    energy: f32,
}

async fn run() {
    let instance = wgpu::Instance::default();
    let adapter = instance
       .request_adapter(&wgpu::RequestAdapterOptions::default())
       .await
       .expect("Failed to find a suitable graphic adapter.");
    let (device, queue) = adapter
       .request_device(&wgpu::DeviceDescriptor::default(), None)
       .await
       .expect("Failed to create the logical device.");

    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("Hong-Ou-Mandel Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("hong_ou_mandel.wgsl").into()),
    });

    let compute_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
        label: Some("DWE-HOM Pipeline"),
        layout: None,
        module: &shader,
        entry_point: "main",
    });

    // Vector to store the historical states of all simulation steps
    let mut all_history = Vec::new();

    // Initial boundary conditions for the 4 theoretical scattering matrices
    let scenarios = vec![
        (1, "HOM Bunching (State 1 - Synchronous Convergence)", vec![
            Vortex { pos: [512.0, 480.0], vel: [0.0, 1.0], spin: 1.0, energy: 1.0 },
            Vortex { pos: [480.0, 512.0], vel: [1.0, 0.0], spin: -1.0, energy: 1.0 },
        ]),
        (2, "HOM Bunching (State 2 - Inverted Symmetry)", vec![
            Vortex { pos: [480.0, 512.0], vel: [0.0, -1.0], spin: 1.0, energy: 1.0 },
            Vortex { pos: [512.0, 480.0], vel: [-1.0, 0.0], spin: -1.0, energy: 1.0 },
        ]),
        (3, "Classical Scattering TT (Asynchronous - Photon 2 Delay)", vec![
            Vortex { pos: [512.0, 480.0], vel: [0.0, 1.0], spin: 1.0, energy: 1.0 },
            Vortex { pos: [460.0, 512.0], vel: [1.0, 0.0], spin: -1.0, energy: 1.0 },
        ]),
        (4, "Classical Scattering RR (Asynchronous - Photon 1 Delay)", vec![
            Vortex { pos: [480.0, 532.0], vel: [0.0, -1.0], spin: 1.0, energy: 1.0 },
            Vortex { pos: [512.0, 480.0], vel: [-1.0, 0.0], spin: -1.0, energy: 1.0 },
        ]),
    ];

    for (scenario_id, name, initial_particles) in scenarios {
        println!("Computing Scenario {}: {}...", scenario_id, name);

        let particle_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Particle State Buffer"),
            contents: bytemuck::cast_slice(&initial_particles),
            usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_SRC,
        });

        // Initialize spatial tension grid (Vacuum Memory)
        let grid_size = 1024 * 1024;
        let initial_grid = vec![0.0f32; grid_size];
        let vacuum_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Spatial Tension Matrix Buffer"),
            contents: bytemuck::cast_slice(&initial_grid),
            usage: wgpu::BufferUsages::STORAGE,
        });

        let bind_group_layout = compute_pipeline.get_bind_group_layout(0);
        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("DWE Binding Group"),
            layout: &bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry { binding: 0, resource: particle_buffer.as_entire_binding() },
                wgpu::BindGroupEntry { binding: 1, resource: vacuum_buffer.as_entire_binding() },
            ],
        });

        let output_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Output Mapping Buffer"),
            size: (std::mem::size_of::<Vortex>() * initial_particles.len()) as u64,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let total_steps = 6000;
        for step in 0..=total_steps {
            let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
            {
                let mut cpass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor { label: None, timestamp_writes: None });
                cpass.set_pipeline(&compute_pipeline);
                cpass.set_bind_group(0, &bind_group, &[]);
                cpass.dispatch_workgroups(1, 1, 1);
            }
            queue.submit(Some(encoder.finish()));

            // Sample physical state every 50 iteration steps
            if step % 50 == 0 {
                let mut copy_encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
                copy_encoder.copy_buffer_to_buffer(&particle_buffer, 0, &output_buffer, 0, output_buffer.size());
                queue.submit(Some(copy_encoder.finish()));

                let buffer_slice = output_buffer.slice(..);
                let (sender, receiver) = futures_intrusive::channel::shared::oneshot_channel();
                buffer_slice.map_async(wgpu::MapMode::Read, move |v| sender.send(v).unwrap());
                device.poll(wgpu::Maintain::Wait);

                if let Some(Ok(())) = pollster::block_on(receiver.receive()) {
                    let data = buffer_slice.get_mapped_range();
                    let result: &[Vortex] = bytemuck::cast_slice(&data);
                    for (i, v) in result.iter().enumerate() {
                        all_history.push((scenario_id, step, i, v.pos[0], v.pos[1], v.vel[0], v.vel[1], v.spin, v.energy));
                    }
                    drop(data);
                    output_buffer.unmap();
                }
            }
        }
    }

    // Export cumulative simulation data to CSV
    let mut wtr = std::fs::File::create("output.csv").unwrap();
    use std::io::Write;
    writeln!(wtr, "scenario,step,id,pos_x,pos_y,vel_x,vel_y,spin,energy").unwrap();
    for record in all_history {
        writeln!(wtr, "{},{},{},{},{},{},{},{},{}", 
            record.0, record.1, record.2, record.3, record.4, record.5, record.6, record.7, record.8).unwrap();
    }
    println!("Physics simulation completed. All 4 scenarios successfully saved to output.csv");
}

fn main() {
    pollster::block_on(run());
}