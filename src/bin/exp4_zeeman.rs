// src/bin/exp4_zeeman.rs
use wgpu::util::DeviceExt;

#[repr(C)]
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

    // Inicializa órbitas circulares com helicidades opostas (+1 e -1) 
    let mut input_particles = Vec::new();
    for i in 0..256 {
        let helicity = if i % 2 == 0 { 1.0 } else { -1.0 };
        input_particles.push(Particle {
            position: [1.0, 0.0, 0.0, 1.0],
            velocity: [0.0, 5.0 * helicity, 0.0, 0.0],
            orbital_energy: 100.0,
            helicity,
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

    let shader_source = include_str!("exp4_zeeman.wgsl");
    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("Zeeman Shader"),
        source: wgpu::ShaderSource::Wgsl(shader_source.into()),
    });

    let bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        label: None,
        entries: &[
            wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::COMPUTE,
                ty: wgpu::BindingType::Buffer {
                    ty: wgpu::BufferBindingType::Storage { read_only: false },
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            }
        ],
    });

    let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
        label: None,
        layout: &bind_group_layout,
        entries: &[
            wgpu::BindGroupEntry {
                binding: 0,
                resource: particle_buffer.as_entire_binding(),
            }
        ],
    });

    let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: None,
        bind_group_layouts: &[&bind_group_layout],
        push_constant_ranges: &[],
    });

    let compute_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
        label: None,
        layout: Some(&pipeline_layout),
        module: &shader,
        entry_point: "compute_zeeman_splitting",
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
        
        let mut prograde_energy = 0.0;
        let mut retrograde_energy = 0.0;
        for p in result.iter() {
            if p.helicity > 0.0 {
                prograde_energy += p.orbital_energy;
            } else {
                retrograde_energy += p.orbital_energy;
            }
        }
        println!("[*] Experimento 4 concluído. Separação de Níveis de Energia (Zeeman):");
        println!("  -> Energia Média Prógrada (Spin +1): {:.2}", prograde_energy / 128.0);
        println!("  -> Energia Média Retrógrada (Spin -1): {:.2}", retrograde_energy / 128.0);
        use std::io::Write;
        let mut file = std::fs::File::create("analytics/result_exp4_zeeman.csv").unwrap();
        writeln!(file, "id,helicity,orbital_energy").unwrap();
        for (i, p) in result.iter().enumerate() {
            writeln!(file, "{},{},{}", i, p.helicity, p.orbital_energy).unwrap();
        }
    }
}

fn main() {
    pollster::block_on(run());
}