use bytemuck::{Pod, Zeroable};
use std::fs::File;
use std::io::Write;
use std::time::Instant;
use wgpu::util::DeviceExt;
use wgpu::{BufferUsages, CommandEncoderDescriptor, ComputePassDescriptor, ComputePipelineDescriptor};

const TOTAL_PHOTONS: u32 = 50_000_000;

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
    with_vortices: u32,   
    with_pilot_wave: u32, 
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
    with_vortices: u32,
    with_pilot_wave: u32,
    measurement_sensor: u32,
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
        QuadrantProfile { name: "A: Newtonian World", filename: "result_A_newton_gpu.csv", with_deflection: 0, with_turbulence: 0, with_vortices: 0, with_pilot_wave: 0, measurement_sensor: 0 },
        QuadrantProfile { name: "B: Thermodynamic Dispersion", filename: "result_B_sand_gpu.csv", with_deflection: 0, with_turbulence: 1, with_vortices: 0, with_pilot_wave: 0, measurement_sensor: 0 },
        QuadrantProfile { name: "C: Rigid Interference (Onda pura)", filename: "result_C_comb_gpu.csv", with_deflection: 1, with_turbulence: 0, with_vortices: 0, with_pilot_wave: 1, measurement_sensor: 0 },
        QuadrantProfile {
            name: "D: Fluid Reality (Full Feynman Pattern)",
            filename: "result_D_feynman_gpu.csv",
            with_deflection: 1,
            with_turbulence: 1, 
            measurement_sensor: 0,
            with_vortices: 1,
            with_pilot_wave: 1
        },
        // MODIFICAÇÃO CHAVE: with_turbulence ativado (1) para gerar a decoerência termodinâmica
        QuadrantProfile { 
            name: "E: Classical Collapse", 
            filename: "result_E_colapso.csv", 
            with_deflection: 1, 
            with_turbulence: 1, 
            with_vortices: 1, 
            with_pilot_wave: 1, 
            measurement_sensor: 1 
        },
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
            slits_distance: 100.0, 
            slit_width: 5.0,
            base_tension: 150.0,  
            with_vortices: profile.with_vortices,
            with_pilot_wave: profile.with_pilot_wave,
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