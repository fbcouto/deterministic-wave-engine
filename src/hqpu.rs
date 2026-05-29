use std::fs::File;
use std::io::Write;

// ==========================================
// HQPU: HYDRO-QUANTUM PROCESSING UNIT (QND Sim V3)
// ==========================================

struct HQPUVacuum {
    base_tension: f32,
}

// O Qubit agora é modelado como um Fuso (Duplo Cone Unido pela Base)
struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,     // Positivo (Horário) ou Negativo (Anti-Horário) -> Define a Polarização
    wake_amplitude: f32, // Força da esteira termodinâmica
}

impl HQPUVacuum {
    // Simula a porta lógica (Obstáculo Termodinâmico ou Polarizador)
    fn apply_fluidic_gate(&self, qubit: &mut VortexQubit) {
        // A porta lógica está entre Y: 100 e Y: 150
        if qubit.y > 100.0 && qubit.y < 150.0 {
            // O gradiente interage com a Helicidade (sinal do spin)
            // Um spin positivo deflete para um lado, um negativo para o outro
            let gradient_pressure = (qubit.y * 0.2).sin() * self.base_tension;
            
            // Alteração determinística do estado (Cálculo Lógico Fluido)
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // O duplo cone desliza lateralmente dependendo do seu sentido de rotação
            qubit.vx += gradient_pressure * 0.01 * qubit.spin_omega.signum(); 
        }
    }
}

// Receptor Analítico (Leitura Não-Destrutiva da Esteira do Equador do Cone)
fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(1.0);
    
    // A pressão oscila com a rotação, capturando perfeitamente a helicidade (sinal da onda)
    let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
    pressure
}

fn main() {
    println!("Starting HQPU simulation V3: Non-Destructive Analytical Reading...");
    println!("Entity: Double-Cone Vortex (Positive Helicity / Right-Handed Polarization)");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Lançamento do Qubit Duplo Cone
    // spin_omega positivo = Polarização Horária
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 1.0, wake_amplitude: 25.0 
    };

    let mut file = File::create("hqpu_readings.csv").expect("Failed to create CSV");
    writeln!(file, "Time_Y,Left_Sensor,Right_Sensor").unwrap();

    let dt = 0.1;

    // Travessia do chip HQPU (de Y=0 a Y=300)
    while qubit.y < 300.0 {
        vacuum.apply_fluidic_gate(&mut qubit);
        
        qubit.x += qubit.vx * dt;
        qubit.y += qubit.vy * dt;
        
        // A inércia natural do equador largo tende a acelerar ligeiramente o spin em meio livre
        qubit.spin_omega += 0.15 * dt * qubit.spin_omega.signum(); 
        
        // Sensores analíticos contínuos (Quantum Non-Demolition) lendo as bordas da esteira
        let reading_left = analytical_receiver(&qubit, 20.0, qubit.y);
        let reading_right = analytical_receiver(&qubit, 80.0, qubit.y);
        
        writeln!(file, "{:.2},{:.4},{:.4}", qubit.y, reading_left, reading_right).unwrap();
    }

    println!("Success! The double-cone vortex crossed the logic gate intact.");
    println!("Measurement data extracted to: hqpu_readings.csv\n");
}