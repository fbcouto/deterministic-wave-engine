struct Particle {
    position: vec4<f32>,
    velocity: vec4<f32>,
    orbital_energy: f32,
    helicity: f32,
    _padding: vec2<f32>,
}

struct VacuumMesh {
    acoustic_echo: f32,
    _padding: vec3<f32>,
}

@group(0) @binding(0)
var<storage, read_write> particles: array<Particle>;

@group(0) @binding(1)
var<storage, read_write> vacuum_mesh: array<VacuumMesh>;

// Função de pseudo-aleatoriedade para o lift estocástico
fn random_float(seed: u32) -> f32 {
    return fract(sin(f32(seed) * 12.9898) * 43758.5453);
}

// Emulação do vácuo base (gamma zero)
fn read_vacuum_tension(pos: vec4<f32>) -> f32 {
    return 1500.0;
}

@compute @workgroup_size(256)
fn compute_tunneling(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let id = global_id.x;
    var vortex = particles[id];
    
    // Gradiente da Barreira de Potencial
    let barrier_start = 50.0;
    let barrier_end = 55.0;
    let energy_wall = 1500.0; 
    let dt = 0.1;
    
    // Simula a evolução e os sucessivos "bouncings" (colisões) ao longo do tempo
    for (var step: u32 = 0u; step < 1000u; step++) {
        
        // Empuxo contínuo mais forte para manter a partícula colidindo repetidamente
        if (vortex.position.x < barrier_start) {
            vortex.velocity.x += 5.0 * dt; 
        }
        
        // Cinemática de avanço
        vortex.position.x += vortex.velocity.x * dt;
        
        if (vortex.position.x >= barrier_start && vortex.position.x <= barrier_end) {
            // CALIBRAÇÃO: Acúmulo de energia acústica retroativa muito maior por impacto
            // Simulando a alta incompressibilidade do vácuo rebatendo a onda
            vacuum_mesh[id].acoustic_echo += abs(vortex.velocity.x) * 15.0;
            
            // Empuxo caótico via Efeito Magnus e Tensão Fluídica
            let stochastic_lift = (vacuum_mesh[id].acoustic_echo / energy_wall) * random_float(id + step);
            
            if (stochastic_lift > 0.95) {
                // Tunelamento Mecânico Bem-sucedido
                vortex.position.x = barrier_end + 1.0; 
                vortex.velocity.x = 10.0; // Mantém uma velocidade residual após o tunelamento
                break; // Atingiu o objetivo, partícula ejetada do bolsão!
            } else {
                // Reflexão Fluídica Clássica (Bouncing phase)
                vortex.position.x = barrier_start - 0.1; 
                // CALIBRAÇÃO: Perde apenas 5% da velocidade ao recuar para suportar múltiplas colisões
                vortex.velocity.x = -abs(vortex.velocity.x) * 0.95; 
            }
        }
        
        // Parada de segurança
        if (vortex.position.x > 80.0) {
            break;
        }
    }
    
    particles[id] = vortex;
}