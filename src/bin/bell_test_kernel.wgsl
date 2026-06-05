struct Particle {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin: f32,
    is_measured: u32,
};

struct Uniforms {
    polarizer_a: f32, // Em radianos
    polarizer_b: f32, // Em radianos
    tension: f32,
    dt: f32,
};

@group(0) @binding(0) var<storage, read_write> particles: array<Particle>;
@group(0) @binding(1) var<uniform> params: Uniforms;

// Função para simular o eco não-Markoviano do vácuo
fn calculate_vacuum_echo(pos: vec2<f32>, polarizer_angle: f32, distance_to_sensor: f32) -> f32 {
    // A onda de proa reflete no sensor e cria um gradiente de pressão que induz torque
    let echo_strength = 1.0 / (distance_to_sensor + 0.001);
    let phase_difference = atan2(pos.y, pos.x) - polarizer_angle;
    
    // O torque estocástico local altera a probabilidade mecânica do eixo de giro
    return cos(phase_difference) * echo_strength * params.tension;
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let index = global_id.x;
    if (index >= arrayLength(&particles)) { return; }
    
    var p = particles[index];
    
    if (p.is_measured == 1u) { return; }

    // Determinar qual lado (Alice ou Bob)
    let is_alice_side = p.pos.x < 0.0;
    let pol_angle = select(params.polarizer_b, params.polarizer_a, is_alice_side);
    
    // Distância até o sensor de medição
    let sensor_x = select(100.0, -100.0, is_alice_side);
    let dist = abs(p.pos.x - sensor_x);
    
    // Aplicar a perturbação no Espin ANTES da colisão (Quebra da Independência de Medição)
    if (dist < 10.0) { // Zona de turbulência de contorno
        let torque = calculate_vacuum_echo(p.pos, pol_angle, dist);
        
        // Efeito Magnus Quântico atenuando/invertendo o spin de forma local
        p.spin = p.spin + (torque * params.dt);
        
        // Colapso local (medição mecânica)
        if (dist < 0.5) {
            p.spin = sign(p.spin); // Força para estado binário observável
            p.is_measured = 1u;
        }
    }
    
    // Integração Cinemática
    p.pos = p.pos + p.vel * params.dt;
    particles[index] = p;
}