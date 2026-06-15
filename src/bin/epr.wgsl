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

// Pure Geometric Polarizer (Structural Threshold Model)
fn apply_polarizer(p: Vortex, polarizer_angle: f32) -> f32 {
    let delta = p.pol_angle - polarizer_angle;
    
    // Geometric stress function: cos(2 * delta) due to 180-degree Malus symmetry
    let stress = cos(2.0 * delta); 

    // Direct collision between external grating geometry and hidden internal resilience
    if (stress >= p.transverse_phase) {
        return 1.0;  // Channel +1 (Transmitted)
    } else if (stress <= -p.transverse_phase) {
        return -1.0; // Channel -1 (Deflected)
    } else {
        return -2.0; // Channel -2 (Annihilated / Absorbed by the grid)
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
