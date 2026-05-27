use std::fs::File;
use std::io::Write;

// ==========================================
// HQPU: HYDRO-QUANTUM PROCESSING UNIT
// ==========================================

struct HQPUVacuum {
    base_tension: f32,
}

struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,     // Internal rotation (Phase/Information State)
    wake_amplitude: f32, // Strength of the wake left in the vacuum
}

impl HQPUVacuum {
    // Simulates a logic gate (e.g., Hadamard). 
    // It is a thermodynamic obstacle in the vacuum, not a microwave pulse.
    fn apply_fluidic_gate(&self, qubit: &mut VortexQubit) {
        // The Gate is positioned between Y: 100 and Y: 150 on the chip
        if qubit.y > 100.0 && qubit.y < 150.0 {
            // The space becomes "dense" and forces the vortex to change its axis of rotation
            let gradient_pressure = (qubit.y * 0.2).sin() * self.base_tension;
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // The vortex "slips" slightly to the side due to the gradient
            qubit.vx += gradient_pressure * 0.02;
        }
    }
}

// The Analytical Receiver (Reads the Tension without intercepting the particle)
fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(0.1);
    
    // The sensor only captures the wake if it is close enough (deflection zone)
    if distance < 40.0 {
        // The read pressure drops with distance, and pulses according to spin_omega
        let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
        return pressure;
    }
    0.0
}

fn main() {
    println!("Starting HQPU simulation: Non-Destructive Analytical Reading...");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Launches a qubit in the center of the channel (X=50), moving upwards (vy=2.0)
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 0.0, wake_amplitude: 15.0 
    };

    let mut file = File::create("hqpu_readings.csv").expect("Failed to create CSV");
    writeln!(file, "Time_Y,Left_Sensor,Right_Sensor").unwrap();

    let dt = 0.1;

    // The Qubit crosses the HQPU chip (from Y=0 to Y=300)
    while qubit.y < 300.0 {
        // 1. Applies the chip's topology (Hydrodynamic Logic Gates)
        vacuum.apply_fluidic_gate(&mut qubit);
        
        // 2. The Evolution of the Qubit in space
        qubit.x += qubit.vx * dt;
        qubit.y += qubit.vy * dt;
        qubit.spin_omega += 0.15 * dt; // The natural rotation of the particle
        
        // 3. Continuous Measurement by Parallel Sensors (at x=20 and x=80)
        let reading_left = analytical_receiver(&qubit, 20.0, qubit.y);
        let reading_right = analytical_receiver(&qubit, 80.0, qubit.y);
        
        writeln!(file, "{:.2},{:.4},{:.4}", qubit.y, reading_left, reading_right).unwrap();
    }

    println!("Success! The particle crossed the logic gate intact.");
    println!("Measurement data extracted to: hqpu_readings.csv\n");
}