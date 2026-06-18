use bytemuck::{Pod, Zeroable};
use std::fs::File;
use std::io::Write;
use std::time::Instant;
use wgpu::util::DeviceExt;
use wgpu::{BufferUsages, CommandEncoderDescriptor, ComputePassDescriptor, ComputePipelineDescriptor};

const TOTAL_PHOTONS: u32 = 10_000;
const CHUNK_SIZE: u32 = 50_000; // Sends 50k at a time to let the GPU breathe

#[repr(C)]
#[derive(Copy, Clone, Debug, Pod, Zeroable)]
struct Params {
    with_turbulence: u32,
    measurement_sensor: u32,
    total_photons: u32,
    screen_width: u32,
    laser_a_x: f32,
    laser_b_x: f32,
    lasers_y: f32,
    screen_y: f32,
    base_tension: f32,
    decay_rate: f32,
    wavelength: f32,
    with_memory: u32,
    use_spin: u32,
    photon_offset: u32, // NEW: Batch control (replaced pad1)
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
    with_turbulence: u32,
    measurement_sensor: u32,
    with_memory: u32,
    use_spin: u32,
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
        label: Some("Compute Pipeline Pfleegor-Mandel"),
        layout: None,
        module: &shader,
        entry_point: "main",
    });

    let quadrant_matrix = [
        QuadrantProfile { 
            name: "A: Two Lasers (Classical Dispersion / No Memory)", 
            filename: "result_A_no_memory.csv", 
            with_turbulence: 0, measurement_sensor: 0, with_memory: 0, use_spin: 0 
        },
        QuadrantProfile { 
            name: "B: Fluid Reality (Emergent Fraunhofer via Memory)", 
            filename: "result_B_pfleegor_mandel.csv", 
            with_turbulence: 1, measurement_sensor: 0, with_memory: 1, use_spin: 0 
        },
        QuadrantProfile {
            name: "C: Quantum Magnus Effect (Fluid + Spin + Turbulence)",
            filename: "result_C_magnus_spin.csv",
            with_turbulence: 1, measurement_sensor: 0, with_memory: 1, use_spin: 1
        },
        QuadrantProfile {
            name: "D: Stern-Gerlach (Only 1 Laser + Spin)", // NEW EXPERIMENT
            filename: "result_D_single_laser.csv",
            with_turbulence: 1, measurement_sensor: 1, with_memory: 1, use_spin: 1
        },
    ];

    for profile in quadrant_matrix.iter() {
        println!(" -> Processing [{}]...", profile.name);
        let start = Instant::now();

        let params = Params {
            with_turbulence: profile.with_turbulence,
            measurement_sensor: profile.measurement_sensor,
            total_photons: TOTAL_PHOTONS,
            screen_width: 2000,
            laser_a_x: 900.0,       
            laser_b_x: 1100.0,      
            lasers_y: 100.0,        
            screen_y: 900.0,        
            base_tension: 150.0,    
            decay_rate: 0.0001,     
            wavelength: 18.0,       
            with_memory: profile.with_memory,
            use_spin: profile.use_spin,
            photon_offset: 0, // Starts at zero, the loop will handle it
            pad2: 0, 
            pad3: 0,
        };

        let params_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Params Buffer"),
            contents: bytemuck::bytes_of(&params),
            usage: BufferUsages::UNIFORM | BufferUsages::COPY_DST, // We need COPY_DST to update via batches
        });

        let screen_buffer_size = (2000 * std::mem::size_of::<ExtractedBucket>()) as u64;
        let screen_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Screen Buffer"),
            size: screen_buffer_size,
            usage: BufferUsages::STORAGE | BufferUsages::COPY_SRC | BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let wake_buffer_size = 16 + (256 * 16);
        let wake_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Wake Memory Buffer"),
            size: wake_buffer_size as u64,
            usage: BufferUsages::STORAGE | BufferUsages::COPY_DST,
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
            label: Some("Main Bind Group"),
            layout: &bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry { binding: 0, resource: screen_buffer.as_entire_binding() },
                wgpu::BindGroupEntry { binding: 1, resource: params_buffer.as_entire_binding() },
                wgpu::BindGroupEntry { binding: 2, resource: wake_buffer.as_entire_binding() },
            ],
        });

        // ----------- BATCH SYSTEM (ANTI-TDR) -----------
        let num_chunks = (TOTAL_PHOTONS + CHUNK_SIZE - 1) / CHUNK_SIZE;

        for chunk in 0..num_chunks {
            let offset = chunk * CHUNK_SIZE;
            let current_chunk_size = if offset + CHUNK_SIZE > TOTAL_PHOTONS {
                TOTAL_PHOTONS - offset
            } else {
                CHUNK_SIZE
            };

            // 1. Update the offset in the parameters buffer
            let mut chunk_params = params;
            chunk_params.photon_offset = offset;
            queue.write_buffer(&params_buffer, 0, bytemuck::bytes_of(&chunk_params));

            // 2. Dispatch the batch
            let mut encoder = device.create_command_encoder(&CommandEncoderDescriptor { label: None });
            {
                let mut cpass = encoder.begin_compute_pass(&ComputePassDescriptor { label: None, timestamp_writes: None });
                cpass.set_pipeline(&compute_pipeline);
                cpass.set_bind_group(0, &bind_group, &[]);
                
                let dispatch_x = (current_chunk_size + 255) / 256;
                cpass.dispatch_workgroups(dispatch_x, 1, 1);
            }
            queue.submit(Some(encoder.finish()));
            
            // 3. Wait for the GPU, preventing Windows timeout
            device.poll(wgpu::Maintain::Wait); 
        }

        // ----------- DOWNLOAD TO CPU -----------
        let mut copy_encoder = device.create_command_encoder(&CommandEncoderDescriptor { label: None });
        copy_encoder.copy_buffer_to_buffer(&screen_buffer, 0, &staging_buffer, 0, screen_buffer_size);
        queue.submit(Some(copy_encoder.finish()));

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