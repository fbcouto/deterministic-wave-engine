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
    spin_omega: f32,     // Rotação interna (Fase/Estado da Informação)
    wake_amplitude: f32, // Força da marola deixada no vácuo
}

impl HQPUVacuum {
    // Simula uma porta lógica (ex: Hadamard). 
    // É um obstáculo termodinâmico no vácuo, não um pulso de micro-ondas.
    fn apply_fluidic_gate(&self, qubit: &mut VortexQubit) {
        // A Porta está posicionada entre o Y: 100 e Y: 150 do chip
        if qubit.y > 100.0 && qubit.y < 150.0 {
            // O espaço fica "denso" e obriga o vórtice a mudar o seu eixo de rotação
            let gradient_pressure = (qubit.y * 0.2).sin() * self.base_tension;
            qubit.spin_omega += gradient_pressure * 0.05;
            
            // O vórtice "escorrega" levemente para o lado devido ao gradiente
            qubit.vx += gradient_pressure * 0.02;
        }
    }
}

// O Receptor Analítico (Lê a Tensão sem interceptar a partícula)
fn analytical_receiver(qubit: &VortexQubit, sensor_x: f32, sensor_y: f32) -> f32 {
    let dx = qubit.x - sensor_x;
    let dy = qubit.y - sensor_y;
    let distance = (dx * dx + dy * dy).sqrt().max(0.1);
    
    // O sensor só capta a marola se estiver próximo o suficiente (zona de deflexão)
    if distance < 40.0 {
        // A pressão lida cai com a distância, e pulsa de acordo com o spin_omega
        let pressure = (qubit.wake_amplitude / distance) * qubit.spin_omega.sin();
        return pressure;
    }
    0.0
}

fn main() {
    println!("Iniciando simulação do HQPU: Leitura Analítica Não-Destrutiva...");

    let vacuum = HQPUVacuum { base_tension: 5.0 };
    
    // Lança um qubit no centro do canal (X=50), subindo (vy=2.0)
    let mut qubit = VortexQubit { 
        x: 50.0, y: 0.0, vx: 0.0, vy: 2.0, 
        spin_omega: 0.0, wake_amplitude: 15.0 
    };

    let mut file = File::create("hqpu_readings.csv").expect("Falha ao criar CSV");
    writeln!(file, "Tempo_Y,Sensor_Esquerdo,Sensor_Direito").unwrap();

    let dt = 0.1;

    // O Qubit cruza o chip HQPU (de Y=0 até Y=300)
    while qubit.y < 300.0 {
        // 1. Aplica a topologia do chip (Portas Lógicas hidrodinâmicas)
        vacuum.apply_fluidic_gate(&mut qubit);
        
        // 2. A Evolução do Qubit no espaço
        qubit.x += qubit.vx * dt;
        qubit.y += qubit.vy * dt;
        qubit.spin_omega += 0.15 * dt; // A rotação natural da partícula
        
        // 3. Medição Contínua pelos Sensores Paralelos (em x=20 e x=80)
        let reading_left = analytical_receiver(&qubit, 20.0, qubit.y);
        let reading_right = analytical_receiver(&qubit, 80.0, qubit.y);
        
        writeln!(file, "{:.2},{:.4},{:.4}", qubit.y, reading_left, reading_right).unwrap();
    }

    println!("Sucesso! A partícula cruzou a porta lógica intacta.");
    println!("Dados da medição extraídos para: hqpu_readings.csv\n");
}