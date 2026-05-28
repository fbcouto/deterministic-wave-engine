use std::fs::File;
use std::io::Write;

// ==========================================
// HQPU: HYDRO-QUANTUM PROCESSING UNIT (QND Sim)
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
    wake_amplitude: f32, // Strength of the thermodynamic wake left in the vacuum
}

impl HQPUVacuum {
    // Simulates the logic gate (Thermodynamic obstacle in the vacuum)
    fn apply_fluidic_gate(&self, qubit: &mut VortexQubit) {
        // The Logic Gate is positioned between Y: 100 and Y: 150
        if qubit.y > 100.0 && qubit.y < 150.0 {
            // Space becomes "dense" and alters the phase/spin
            let gradient_pressure = (qubit.y * 0.2).sin() * self.base_tension;
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // The vortex slides laterally across the gradient
            qubit.vx += gradient_pressure * 0.01; 
        }
    }
}

// Analytical Receiver (Reads lateral tension without intercepting the particle)
fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(1.0);
    
    // CORREÇÃO FÍSICA: O sensor lê a esteira contínua. A pressão decai naturalmente
    // com a distância, sem um corte artificial, mantendo a senoidal orgânica e fluida.
    let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
    pressure
}

fn main() {
    println!("Starting HQPU simulation: Non-Destructive Analytical Reading...");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Launch qubit at center (X=50), moving upwards (vy=2.0)
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 0.0, wake_amplitude: 25.0 // Aumentamos a amplitude para um gráfico mais claro
    };

    let mut file = File::create("hqpu_readings.csv").expect("Failed to create CSV");
    writeln!(file, "Time_Y,Left_Sensor,Right_Sensor").unwrap();

    let dt = 0.1;

    // Qubit crosses the HQPU chip (from Y=0 to Y=300)
    while qubit.y < 300.0 {
        vacuum.apply_fluidic_gate(&mut qubit);
        
        qubit.x += qubit.vx * dt;
        qubit.y += qubit.vy * dt;
        qubit.spin_omega += 0.15 * dt; 
        
        // Continuous Measurement by Analytical Sensors (x=20 and x=80)
        let reading_left = analytical_receiver(&qubit, 20.0, qubit.y);
        let reading_right = analytical_receiver(&qubit, 80.0, qubit.y);
        
        writeln!(file, "{:.2},{:.4},{:.4}", qubit.y, reading_left, reading_right).unwrap();
    }

    println!("Success! The particle crossed the logic gate intact.");
    println!("Measurement data extracted to: hqpu_readings.csv\n");
}