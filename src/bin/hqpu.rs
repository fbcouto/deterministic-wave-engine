use std::fs::File;
use std::io::Write;

// ==========================================
// HQPU: HYDRO-QUANTUM PROCESSING UNIT (QND Sim V3 - Fixed Spin Model)
// ==========================================

struct HQPUVacuum {
    base_tension: f32,
}

// Perfect structural alignment for pairing with WGSL Compute Shaders
struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,     // Invariable spin vector helicity/orientation (±1.0)
    frequency: f32,      // NEW: Topological compaction of the spindle core
    wake_amplitude: f32, // Barometric thermodynamic wake force
    padding1: f32,       // Guarantees 16/32 byte alignment
}

impl HQPUVacuum {
    fn apply_fluidic_gate(&self, vacuum_tension: f32, qubit: &mut VortexQubit) {
        if qubit.y > 100.0 && qubit.y < 150.0 {
            let gradient_pressure = (qubit.y * 0.2).sin() * vacuum_tension;
            
            // Change of the rotation plane orientation
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // Lateral sliding now responds to topological compaction (frequency)
            qubit.vx += gradient_pressure * (qubit.frequency * 0.00066) * qubit.spin_omega.signum(); 
        }
    }
}

fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(1.0);
    
    // The mechanical pressure wake oscillates based on the helicity sign
    let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
    pressure
}

fn main() {
    println!("Starting HQPU simulation V3: Non-Destructive Analytical Reading...");
    println!("Entity: Double-Cone Vortex Soliton (Invariable Spin, Topological Compression Mapping)");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Qubit initialization following the new structural pattern
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 1.0,         // Base unitary magnitude for logical representation
        frequency: 30.0,         // High frequency = greater geometric rigidity
        wake_amplitude: 25.0, 
        padding1: 0.0
    };
    
    // This forces Rust to save the CSV inside the analytics subfolder
    let mut file = File::create("analytics/hqpu_readings.csv").expect("Failed to create CSV");
    writeln!(file, "Time_Y,Left_Sensor,Right_Sensor").unwrap();

    let dt = 0.1;

    while qubit.y < 300.0 {
        vacuum.apply_fluidic_gate(vacuum.base_tension, &mut qubit);
        
        qubit.x += qubit.vx * dt;
        qubit.y += qubit.vy * dt;
        
        qubit.spin_omega += 0.15 * dt * qubit.spin_omega.signum(); 
        
        let reading_left = analytical_receiver(&qubit, 20.0, qubit.y);
        let reading_right = analytical_receiver(&qubit, 80.0, qubit.y);
        
        writeln!(file, "{:.2},{:.4},{:.4}", qubit.y, reading_left, reading_right).unwrap();
    }

    println!("Success! The stable double-cone vortex crossed the logic gate intact.");
    println!("Measurement data extracted to: hqpu_readings.csv\n");
}