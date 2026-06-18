struct Vortex {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin: f32,
    energy: f32,
    pol_angle: f32,
    transverse_phase: f32,
    status: f32,
    padding: f32,
};

struct Config {
    alice_angle: f32,
    bob_angle: f32,
    viscosity: f32,
    memory_decay: f32,
};

@group(0) @binding(0) var<storage, read_write> particles: array<Vortex>;
@group(0) @binding(1) var<uniform> config: Config;
@group(0) @binding(2) var<storage, read_write> vacuum_grid: array<f32>;

// Substitua a função apply_polarizer no seu arquivo WGSL
fn apply_polarizer(p: Vortex, polarizer_angle: f32) -> f32 {
    let delta = p.pol_angle - polarizer_angle;
    
    // 1. Projeção da Amplitude Hidrodinâmica
    let amplitude_transmitida = cos(delta);
    let amplitude_refletida = sin(delta);
    
    // 2. Pressão Dinâmica (Energia proporcional ao quadrado da amplitude)
    // Isso revela a Lei de Malus de forma puramente estrutural/mecânica
    let energia_transmitida = amplitude_transmitida * amplitude_transmitida; // cos^2(delta)
    let energia_refletida = amplitude_refletida * amplitude_refletida;       // sin^2(delta)
    
    // 3. Dissipação Turbulenta (Energia perdida no impacto geométrico)
    // Este valor atua como o "ruído" que força a amostragem injusta (Fair Sampling)
    let perda_choque = 0.1342; 
    
    // 4. Decisão de Colapso Topológico
    // O vórtice é quantizado: ou ele sobrevive inteiro ou colapsa.
    if (energia_transmitida >= (p.transverse_phase + perda_choque)) {
        return 1.0;  // Flui pelas fendas do anteparo (Transmissão)
    } else if (energia_refletida >= ((1.0 - p.transverse_phase) + perda_choque)) {
        return -1.0; // Desliza pelo anteparo (Reflexão/Deflexão)
    } else {
        return -2.0; // Preso na geometria: o vórtice se desfaz e é absorvido
    }
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let id = global_id.x;
    var p = particles[id];

    if (p.pos.x < 50.0 || p.pos.x > 974.0 || p.status != 0.0) { return; }

    // 1. Strictly Local Vacuum Reading
    let grid_index = u32(p.pos.x) + u32(p.pos.y) * 1024u;
    let local_tension = vacuum_grid[grid_index];
    
    // 2. Classical Viscous Hydrodynamics
    let wave_density = abs(local_tension);
    let vacuum_friction = wave_density * config.viscosity;
    
    p.vel -= p.vel * vacuum_friction * 0.0001; 
    p.pol_angle += local_tension * 0.0; // Single vortex angular momentum conservation

    // 3. Space Kinematics
    p.pos += p.vel * 0.5;

    // 4. Local Back-Reaction (Vortex footprints on the grid)
    let new_grid_index = u32(p.pos.x) + u32(p.pos.y) * 1024u;
    let previous_tension = vacuum_grid[new_grid_index];
    vacuum_grid[new_grid_index] = (previous_tension * config.memory_decay) + (p.energy * p.spin);

    // 5. Physical Measurement Grating
    if (p.vel.x < 0.0 && p.pos.x <= 100.0) { 
        p.status = apply_polarizer(p, config.alice_angle); 
        p.pos.x = 40.0; 
    } else if (p.vel.x > 0.0 && p.pos.x >= 924.0) { 
        p.status = apply_polarizer(p, config.bob_angle); 
        p.pos.x = 984.0; 
    }

    particles[id] = p;
}
