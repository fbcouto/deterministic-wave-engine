use wgpu::util::DeviceExt;
use std::f32::consts::PI;
use std::fs::File;
use std::io::Write;

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
struct Vortex {
    pos: [f32; 2],
    vel: [f32; 2],
    spin: f32,
    energy: f32,
    pol_angle: f32,
    transverse_phase: f32,
    status: f32,
    padding: f32,
}

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
struct Config {
    alice_angle: f32,
    bob_angle: f32,
    viscosity: f32,
    memory_decay: f32,
}

struct Lcg { state: u32 }
impl Lcg {
    fn next_f32(&mut self) -> f32 {
        self.state = self.state.wrapping_mul(1664525).wrapping_add(1013904223);
        (self.state as f32) / (u32::MAX as f32)
    }
}

async fn run() {
    let instance = wgpu::Instance::default();
    let adapter = instance.request_adapter(&wgpu::RequestAdapterOptions::default()).await.unwrap();
    let (device, queue) = adapter.request_device(&wgpu::DeviceDescriptor::default(), None).await.unwrap();

    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("EPR Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("epr.wgsl").into()),
    });

    let compute_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
        label: Some("EPR Pipeline"),
        layout: None,
        module: &shader,
        entry_point: "main",
    });

    let bind_group_layout = compute_pipeline.get_bind_group_layout(0);

    let num_pairs = 100_000; 
    
    // --- NOVO GERADOR CONTÍNUO DE ÂNGULOS ---
    let step_degrees = 22.5; // Resolução de 2.5 graus (atinge 22.5, 45 e 67.5 perfeitamente)
    let max_degrees = 90.0;
    
    let mut angles = Vec::new();
    let mut current_deg = 0.0;
    while current_deg <= max_degrees {
        angles.push(current_deg * (PI / 180.0));
        current_deg += step_degrees;
    }
    
    let viscosities = [0.5];
    let grid_size = 1024 * 1024;

    // CSV FILE PREPARATION
    let mut file = File::create("epr_sweep_results.csv").expect("Failed to create CSV file");
    writeln!(file, "Alice_Angle,Bob_Angle,Correlation,Survivors,Absorbed").unwrap();

    for &visc in viscosities.iter() {
        println!("\n--- Pure Spectral Sweep (No Adjustments) | Viscosity: {} ---", visc);
        
        let (mut e_0_22, mut e_0_67, mut e_45_22, mut e_45_67) = (0.0, 0.0, 0.0, 0.0);

        for (i, &a) in angles.iter().enumerate() {
            for (j, &b) in angles.iter().enumerate() {
                
                let mut initial_particles = Vec::with_capacity(num_pairs * 2);
                let mut rng = Lcg { state: 42 + (i * 10 + j) as u32 };

                for p in 0..num_pairs {
                    let lambda_mae = rng.next_f32() * PI;
                    let phase_alice = rng.next_f32();
                    let y_pos = 100.0 + (p as f32 % 800.0);
                    
                    initial_particles.push(Vortex {
                        pos: [512.0, y_pos], vel: [-10.0, 0.0], spin: 1.0, energy: 1.0,
                        pol_angle: lambda_mae, transverse_phase: phase_alice, status: 0.0, padding: 0.0,
                    });
                    initial_particles.push(Vortex {
                        pos: [512.0, y_pos], vel: [10.0, 0.0], spin: -1.0, energy: 1.0,
                        pol_angle: lambda_mae + (PI / 2.0), transverse_phase: 1.0 - phase_alice, status: 0.0, padding: 0.0,
                    });
                }

                let initial_grid = vec![0.0f32; grid_size];
                let vacuum_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
                    label: Some("Vacuum Grid"),
                    contents: bytemuck::cast_slice(&initial_grid),
                    usage: wgpu::BufferUsages::STORAGE,
                });

                let particle_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
                    label: Some("Particle Buffer"),
                    contents: bytemuck::cast_slice(&initial_particles),
                    usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_SRC,
                });

                let config_data = Config { alice_angle: a, bob_angle: b, viscosity: visc, memory_decay: 0.9 };
                let config_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
                    label: Some("Config Buffer"),
                    contents: bytemuck::cast_slice(&[config_data]),
                    usage: wgpu::BufferUsages::UNIFORM,
                });

                let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
                    label: Some("EPR Group"),
                    layout: &bind_group_layout,
                    entries: &[
                        wgpu::BindGroupEntry { binding: 0, resource: particle_buffer.as_entire_binding() },
                        wgpu::BindGroupEntry { binding: 1, resource: config_buffer.as_entire_binding() },
                        wgpu::BindGroupEntry { binding: 2, resource: vacuum_buffer.as_entire_binding() },
                    ],
                });

                let output_buffer = device.create_buffer(&wgpu::BufferDescriptor {
                    label: Some("Output Buffer"),
                    size: (std::mem::size_of::<Vortex>() * initial_particles.len()) as u64,
                    usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
                    mapped_at_creation: false,
                });

                let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
                {
                    let mut cpass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor { label: None, timestamp_writes: None });
                    cpass.set_pipeline(&compute_pipeline);
                    cpass.set_bind_group(0, &bind_group, &[]);
                    
                    let total_particles = (num_pairs * 2) as u32;
                    let workgroups = (total_particles + 255) / 256;
                    for _ in 0..1000 { cpass.dispatch_workgroups(workgroups, 1, 1); }
                }
                encoder.copy_buffer_to_buffer(&particle_buffer, 0, &output_buffer, 0, output_buffer.size());
                queue.submit(Some(encoder.finish()));

                let buffer_slice = output_buffer.slice(..);
                let (sender, receiver) = futures_intrusive::channel::shared::oneshot_channel();
                buffer_slice.map_async(wgpu::MapMode::Read, move |v| sender.send(v).unwrap());
                device.poll(wgpu::Maintain::Wait);

                if let Some(Ok(())) = pollster::block_on(receiver.receive()) {
                    let data = buffer_slice.get_mapped_range();
                    let result: &[Vortex] = bytemuck::cast_slice(&data);
                    
                    let (mut n_pp, mut n_mm, mut n_pm, mut n_mp) = (0, 0, 0, 0);
                    let mut absorbed = 0;
                    
                    for p in 0..num_pairs {
                        let alice = result[p * 2]; let bob = result[p * 2 + 1];
                        
                        if alice.status == 0.0 || bob.status == 0.0 { continue; }
                        if alice.status == -2.0 || bob.status == -2.0{
                            absorbed += 1;
                            continue;
                        }
                        
                        if alice.status > 0.0 && bob.status > 0.0 { n_pp += 1; }
                        else if alice.status < 0.0 && bob.status < 0.0 { n_mm += 1; }
                        else if alice.status > 0.0 && bob.status < 0.0 { n_pm += 1; }
                        else { n_mp += 1; }
                    }
                    
                    let evaluated_total = (n_pp + n_mm + n_pm + n_mp) as f32;
                    let correlation = if evaluated_total > 0.0 {
                        ((n_pp + n_mm) as f32 - (n_pm + n_mp) as f32) / evaluated_total
                    } else { 0.0 };
                    
                    let deg_a = a * (180.0 / PI);
                    let deg_b = b * (180.0 / PI);
                    
                    // output to Terminal
                    println!("A:{:>5.1}° | B:{:>5.1}° | Corr: {:>7.4} | Survivors: {:>4} (Absorbed: {:>4})", 
                             deg_a, deg_b, correlation, evaluated_total, absorbed);

                    // write to CSV
                    writeln!(file, "{:.1},{:.1},{:.4},{},{}", deg_a, deg_b, correlation, evaluated_total as u32, absorbed).unwrap();

                    if (deg_a - 0.0).abs() < 0.1 && (deg_b - 22.5).abs() < 0.1 { e_0_22 = correlation; }
                    if (deg_a - 0.0).abs() < 0.1 && (deg_b - 67.5).abs() < 0.1 { e_0_67 = correlation; }
                    if (deg_a - 45.0).abs() < 0.1 && (deg_b - 22.5).abs() < 0.1 { e_45_22 = correlation; }
                    if (deg_a - 45.0).abs() < 0.1 && (deg_b - 67.5).abs() < 0.1 { e_45_67 = correlation; }
                }
                output_buffer.unmap();
            }
        }
        
        let s = (e_0_22 - e_0_67 + e_45_22 + e_45_67).abs();
        println!("\n>> CHSH Extract (0/45 vs 22.5/67.5): {:.4}", s);
    }
}

fn main() { pollster::block_on(run()); }