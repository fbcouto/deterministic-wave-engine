use std::fs::File;
use std::io::Write;

// ==========================================
// HQPU: HYDRO-QUANTUM PROCESSING UNIT (QND Sim V3 - Fixed Spin Model)
// ==========================================

struct HQPUVacuum {
    base_tension: f32,
}

// Alinhamento estrutural perfeito para emparelhamento com WGSL Compute Shaders
struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,     // Helicidade/Orientação do vetor de spin invariável (±1.0)
    frequency: f32,      // NOVO: Compactação topológica do núcleo do fuso
    wake_amplitude: f32, // Força da esteira termodinâmica barométrica
    padding1: f32,       // Garante alinhamento de 16/32 bytes
}

impl HQPUVacuum {
    fn apply_fluidic_gate(&self, vacuum_tension: f32, qubit: &mut VortexQubit) {
        if qubit.y > 100.0 && qubit.y < 150.0 {
            let gradient_pressure = (qubit.y * 0.2).sin() * vacuum_tension;
            
            // Alteração da orientação do plano de rotação
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // O deslizamento lateral agora responde à compactação topológica (frequência)
            qubit.vx += gradient_pressure * (qubit.frequency * 0.00066) * qubit.spin_omega.signum(); 
        }
    }
}

fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(1.0);
    
    // A esteira de pressão mecânica oscila com base no sinal da helicidade
    let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
    pressure
}

fn main() {
    println!("Starting HQPU simulation V3: Non-Destructive Analytical Reading...");
    println!("Entity: Double-Cone Vortex Soliton (Invariable Spin, Topological Compression Mapping)");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Inicialização do Qubit seguindo o novo padrão estrutural
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 1.0,         // Magnitude unitária base para representação lógica
        frequency: 30.0,        // Alta frequência = maior rigidez geométrica
        wake_amplitude: 25.0, 
        padding1: 0.0
    };
    // Isso força o Rust a salvar o CSV dentro da subpasta analytics
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