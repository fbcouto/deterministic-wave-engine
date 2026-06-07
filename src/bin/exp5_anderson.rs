// src/bin/exp5_anderson.rs
use wgpu::util::DeviceExt;

#[repr(C)]
// Adding the necessary derives for bytemuck to work
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
struct Particle {
    position: [f32; 4],
    velocity: [f32; 4],
    orbital_energy: f32,
    helicity: f32,
    _padding: [f32; 2],
}

async fn run() {
    let instance = wgpu::Instance::default();
    let adapter = instance.request_adapter(&wgpu::RequestAdapterOptions::default()).await.unwrap();
    let (device, queue) = adapter.request_device(&wgpu::DeviceDescriptor::default(), None).await.unwrap();

    let mut input_particles = Vec::new();
    for i in 0..256 {
        let angle = (i as f32) * 2.0 * std::f32::consts::PI / 256.0;
        input_particles.push(Particle {
            position: [0.0, 0.0, 0.0, 1.0],
            velocity: [angle.cos() * 10.0, angle.sin() * 10.0, 0.0, 0.0],
            orbital_energy: 1.0,
            helicity: 1.0,
            _padding: [0.0; 2],
        });
    }

    let particle_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
        label: Some("Particle Buffer"),
        contents: bytemuck::cast_slice(&input_particles),
        usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_SRC,
    });

    let read_buffer = device.create_buffer(&wgpu::BufferDescriptor {
        label: Some("Read Buffer"),
        size: (input_particles.len() * std::mem::size_of::<Particle>()) as u64,
        usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::MAP_READ,
        mapped_at_creation: false,
    });

    let shader_source = include_str!("exp5_anderson.wgsl");
    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("Anderson Shader"),
        source: wgpu::ShaderSource::Wgsl(shader_source.into()),
    });

    let bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        label: Some("Bind Group Layout"),
        entries: &[wgpu::BindGroupLayoutEntry {
            binding: 0,
            visibility: wgpu::ShaderStages::COMPUTE,
            ty: wgpu::BindingType::Buffer {
                ty: wgpu::BufferBindingType::Storage { read_only: false },
                has_dynamic_offset: false,
                min_binding_size: None,
            },
            count: None,
        }],
    });

    let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
        label: Some("Bind Group"),
        layout: &bind_group_layout,
        entries: &[wgpu::BindGroupEntry {
            binding: 0,
            resource: particle_buffer.as_entire_binding(),
        }],
    });

    let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: None,
        bind_group_layouts: &[&bind_group_layout],
        push_constant_ranges: &[], // Fixed from &, to &[]
    });

    let compute_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
        label: None,
        layout: Some(&pipeline_layout),
        module: &shader,
        entry_point: "compute_anderson_localization", // Removed the Some()
        // compilation_options was removed to be compatible with your wgpu version
    });

    let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
    {
        let mut compute_pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor { label: None, timestamp_writes: None });
        compute_pass.set_pipeline(&compute_pipeline);
        compute_pass.set_bind_group(0, &bind_group, &[]);
        compute_pass.dispatch_workgroups(1, 1, 1);
    }

    encoder.copy_buffer_to_buffer(&particle_buffer, 0, &read_buffer, 0, (input_particles.len() * std::mem::size_of::<Particle>()) as u64);
    queue.submit(Some(encoder.finish()));

    let buffer_slice = read_buffer.slice(..);
    let (sender, receiver) = futures_intrusive::channel::shared::oneshot_channel();
    buffer_slice.map_async(wgpu::MapMode::Read, move |v| sender.send(v).unwrap());

    device.poll(wgpu::Maintain::Wait);
    if let Some(Ok(())) = receiver.receive().await {
        let data = buffer_slice.get_mapped_range();
        let result: &[Particle] = bytemuck::cast_slice(&data);
        
        // Fixed scalar velocity comparison by accessing the [0] index of the vector
        let localized = result.iter().filter(|p| p.velocity[0] == 0.0 && p.velocity[1] == 0.0).count();
        println!("[*] Experiment 5 completed. Particles in localized state: {} / 256", localized);
        use std::io::Write;
        let mut file = std::fs::File::create("analytics/result_exp5_anderson.csv").unwrap();
        writeln!(file, "id,pos_x,pos_y").unwrap();
        for (i, p) in result.iter().enumerate() {
            writeln!(file, "{},{},{}", i, p.position[0], p.position[1]).unwrap();
        }
    }
}

fn main() {
    pollster::block_on(run());
}