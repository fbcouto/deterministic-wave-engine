use bytemuck::{Pod, Zeroable};
use std::fs::File;
use std::io::Write;
use std::time::Instant;
use wgpu::util::DeviceExt;
use wgpu::{BufferUsages, CommandEncoderDescriptor, ComputePassDescriptor, ComputePipelineDescriptor};


// O MOTOR: 50 Milhões de partículas
const TOTAL_PHOTONS: u32 = 50_000_000;

// Parâmetros CHSH clássicos
const ANGLES_ALICE: [f32; 2] = [0.0, 45.0]; // a, a' (em graus)
const ANGLES_BOB: [f32; 2] = [22.5, 67.5];  // b, b' (em graus)

#[repr(C)]
pub struct BellParticle {
    pub pos: [f32; 2],
    pub vel: [f32; 2],
    pub spin: f32,          // +1.0 ou -1.0 (Helicidade)
    pub is_measured: u32,   // 0 = não, 1 = sim
}

#[repr(C)]
pub struct BellUniforms {
    pub polarizer_angle_a: f32,
    pub polarizer_angle_b: f32,
    pub vacuum_mesh_tension: f32, // Representando \gamma_0
    pub time_step: f32,
}

#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
struct Params {
    with_deflection: u32,
    with_turbulence: u32,
    measurement_sensor: u32,
    total_photons: u32,
    screen_width: u32,
    center_x: f32,
    slits_distance: f32,
    slit_width: f32,
    base_tension: f32,
    pad1: u32,
    pad2: u32,
    pad3: u32,
}

#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
struct ExtractedBucket {
    uv: u32,
    green: u32,
    red: u32,
}

struct QuadrantProfile {
    name: &'static str,
    filename: &'static str,
    with_deflection: u32,
    with_turbulence: u32,
    measurement_sensor: u32,
}

use std::f32::consts::PI;

// 1. Definição explícita da estrutura Particle para o pacote de Airy
#[repr(C)]
pub struct Particle {
    pub pos: [f32; 2],
    pub vel: [f32; 2],
    pub spin: f32,
    pub mass: f32,
}

// 2. Função aproximada para a distribuição espacial do envelope de Airy
fn airy_distribution(x: f32) -> f32 {
    // Aproximação do lóbulo principal e cauda oscilatória
    if x < -2.0 {
        return f32::exp(x); // Decaimento exponencial rápido no lado "escuro"
    }
    f32::sin(PI * x) / (PI * x + 0.0001) // Aproximação simplificada do lóbulo para WebGPU
}

// 3. Gerador do pacote com a indexação de array corrigida (center)
pub fn spawn_airy_packet(num_particles: usize, center: [f32; 2], width: f32) -> Vec<Particle> {
    let mut packet = Vec::with_capacity(num_particles);
    for i in 0..num_particles {
        let normalized_x = (i as f32 / num_particles as f32) * width - (width / 2.0);
        let probability_density = airy_distribution(normalized_x);
        
        if rand::random::<f32>() < probability_density.abs() {
            packet.push(Particle {
                // CORRIGIDO: center é o componente X (f32) e center[1] é o componente Y (f32)
                pos: [center[0] + normalized_x, center[1]], 
                vel: [1.0, 0.0], // Movimento linear para a direita
                spin: 1.0,       // Conservação de helicidade do vórtice
                mass: 1.0, 
            });
        }
    }
    packet
}
fn main() {
    pollster::block_on(run());
}

async fn run() {
    let instance = wgpu::Instance::default();
    let adapter = instance.request_adapter(&wgpu::RequestAdapterOptions::default()).await.expect("Adapter not found");
    let (device, queue) = adapter.request_device(&wgpu::DeviceDescriptor::default(), None).await.expect("Failed to create device");

    let shader = device.create_shader_module(wgpu::include_wgsl!("fenda_shader.wgsl"));

    let compute_pipeline = device.create_compute_pipeline(&ComputePipelineDescriptor {
        label: Some("Compute Pipeline"),
        layout: None,
        module: &shader,
        entry_point: "main",
    });

    let quadrant_matrix = [
        QuadrantProfile { name: "A: Newtonian World", filename: "result_A_newton_gpu.csv", with_deflection: 0, with_turbulence: 0, measurement_sensor: 0 },
        QuadrantProfile { name: "B: Thermodynamic Dispersion", filename: "result_B_sand_gpu.csv", with_deflection: 1, with_turbulence: 0, measurement_sensor: 0 },
        QuadrantProfile { name: "C: Rigid Interference", filename: "result_C_comb_gpu.csv", with_deflection: 0, with_turbulence: 1, measurement_sensor: 0 },
        QuadrantProfile { name: "D: Fluid Reality (Feynman)", filename: "result_D_feynman_gpu.csv", with_deflection: 1, with_turbulence: 1, measurement_sensor: 0 },
        QuadrantProfile { name: "E: Classical Collapse", filename: "result_E_colapso.csv", with_deflection: 1, with_turbulence: 1, measurement_sensor: 1 },
    ];

    for profile in quadrant_matrix.iter() {
        println!(" -> Processing [{}]...", profile.name);
        let start = Instant::now();

        let params = Params {
            with_deflection: profile.with_deflection,
            with_turbulence: profile.with_turbulence,
            measurement_sensor: profile.measurement_sensor,
            total_photons: TOTAL_PHOTONS,
            screen_width: 2000,
            center_x: 1000.0,
            slits_distance: 120.0,
            slit_width: 5.0,
            base_tension: 5.0, 
            pad1: 0,
            pad2: 0,
            pad3: 0,
        };

        let params_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Params Buffer"),
            contents: bytemuck::bytes_of(&params),
            usage: BufferUsages::UNIFORM,
        });

        let screen_buffer_size = (2000 * std::mem::size_of::<ExtractedBucket>()) as u64;
        let screen_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Screen Buffer"),
            size: screen_buffer_size,
            usage: BufferUsages::STORAGE | BufferUsages::COPY_SRC | BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let staging_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Staging Buffer"),
            size: screen_buffer_size,
            usage: BufferUsages::MAP_READ | BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let bind_group_layout = compute_pipeline.get_bind_group_layout(0);
        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: None,
            layout: &bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry { binding: 0, resource: screen_buffer.as_entire_binding() },
                wgpu::BindGroupEntry { binding: 1, resource: params_buffer.as_entire_binding() },
            ],
        });

        let mut encoder = device.create_command_encoder(&CommandEncoderDescriptor { label: None });
        {
            let mut cpass = encoder.begin_compute_pass(&ComputePassDescriptor { label: None, timestamp_writes: None });
            cpass.set_pipeline(&compute_pipeline);
            cpass.set_bind_group(0, &bind_group, &[]);
            
            // ========================================================
            // ESTRATÉGIA DE DESPACHO 2D (Contorna o limite de 65.535)
            // ========================================================
            let max_groups_x = 65000;
            let total_groups = (TOTAL_PHOTONS + 255) / 256;
            
            let dispatch_x = total_groups.min(max_groups_x);
            let dispatch_y = (total_groups + max_groups_x - 1) / max_groups_x;

            cpass.dispatch_workgroups(dispatch_x, dispatch_y, 1);
        }
        
        encoder.copy_buffer_to_buffer(&screen_buffer, 0, &staging_buffer, 0, screen_buffer_size);
        queue.submit(Some(encoder.finish()));

        let (sender, receiver) = flume::bounded(1);
        staging_buffer.slice(..).map_async(wgpu::MapMode::Read, move |v| sender.send(v).unwrap());
        device.poll(wgpu::Maintain::Wait);

        if let Ok(Ok(())) = receiver.recv() {
            let data = staging_buffer.slice(..).get_mapped_range();
            let results: &[ExtractedBucket] = bytemuck::cast_slice(&data);

            let mut file = File::create(profile.filename).expect("Failed to create CSV");
            writeln!(file, "X,UV,Green,Red").unwrap();
            for (x, bucket) in results.iter().enumerate() {
                writeln!(file, "{},{},{},{}", x, bucket.uv, bucket.green, bucket.red).unwrap();
            }
            drop(data);
            staging_buffer.unmap();
        }
        println!("OK ({:.2?})", start.elapsed());
    }
}