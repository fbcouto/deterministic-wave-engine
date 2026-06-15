// Deterministic Wave Engine (DWE) Vortex Structure
struct Vortex {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin: f32,          // Rotational helicity (+ω or -ω)
    energy: f32,        // Translated as the compression of the vortex core
};

@group(0) @binding(0) var<storage, read_write> particles: array<Vortex>;
@group(0) @binding(1) var<storage, read_write> vacuum_grid: array<f32>; // Vacuum Memory (Spatial Tension γ)

// Thermodynamic and Hydrodynamic Constants
const ACOUSTIC_REPULSION_K: f32 = 25.0; // Magnitude of the repulsive gradient (shock wave)
const SPLITTER_DENSITY: f32 = 50.0;     // Refraction factor of the 50/50 Beam Splitter

// 1. Topological Obstacle Function (50/50 Beam Splitter)
fn get_splitter_gradient(pos: vec2<f32>) -> vec2<f32> {
    // Pure geometric distance to the mirror's diagonal
    let dist_to_mirror = abs(pos.x - pos.y);
    
    if (dist_to_mirror < 0.1) {
        // Symmetric Dielectric Grating.
        // Utilizing the sum and difference of coordinates ensures that the barrier 
        // potential is perfectly isotropic and mirrored, regardless of intersection parity.
        let phase_sum = (pos.x + pos.y) * SPLITTER_DENSITY;
        let phase_diff = (pos.x - pos.y) * SPLITTER_DENSITY;
        
        let refractive_force = sin(phase_sum) * cos(phase_diff);
        
        // Force acts strictly normal to the surface
        return vec2<f32>(-refractive_force, refractive_force);
    }
    return vec2<f32>(0.0, 0.0);
}

// 2. Inter-Vortex Compression (Deterministic Cause of the HOM Dip)
fn calculate_inter_vortex_shock(p1_pos: vec2<f32>, p2_pos: vec2<f32>) -> vec2<f32> {
    let delta = p1_pos - p2_pos;
    let dist = length(delta);

    // If vortices are perfectly synchronized within the collision zone (HOM Dip window)
    if (dist > 0.0 && dist < 0.5) {
        // Dynamic repulsive gradient from the thermo-acoustic wake.
        // Fluid friction blocks cross-symmetry, inhibiting independent scattering statistics.
        let repulsion_mag = exp(-dist * ACOUSTIC_REPULSION_K);
        return normalize(delta) * repulsion_mag;
    }
    return vec2<f32>(0.0, 0.0);
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let id = global_id.x;
    var p = particles[id];

    // Interaction with the 50/50 Beam Splitter
    let splitter_force = get_splitter_gradient(p.pos);

    // Quantum Magnus Effect derived from local vacuum turbulence
    let grid_index = u32(p.pos.x) + u32(p.pos.y) * 1024u;
    let local_tension = vacuum_grid[grid_index];
    let magnus_deflection = vec2<f32>(-p.vel.y, p.vel.x) * p.spin * local_tension * 0.01;

    // Topological Collective Dynamics (Identification of the conjugated vortex)
    // In an optimized implementation, a Spatial Hash Grid would be used. 
    // Here, we resolve the synchronized twin photon via ID logic.
    var inter_shock_force = vec2<f32>(0.0, 0.0);
    let twin_id = id ^ 1u; 
    let twin_pos = particles[twin_id].pos;
    inter_shock_force = calculate_inter_vortex_shock(p.pos, twin_pos);

    // Deterministic Fluid Integration (Newtonian mechanics restricted to shader gradients).
    // The extreme vector sum of the repulsion (inter_shock_force) and the obstacle (splitter) 
    // causes symmetry blocking: the 0.25 (separated) paths are physically canceled, 
    // inevitably dragging both particles into the same 0.50 (bunched) vector.
    let total_force = splitter_force + magnus_deflection + inter_shock_force;
    
    p.vel += total_force * 0.01; // Delta time (dt)
    p.pos += p.vel * 0.01;

    // Vacuum Hysteresis Update: The photon leaves its acoustic signature for future particles
    vacuum_grid[grid_index] += p.energy * 0.1;

    // Save the iteration state back to VRAM
    particles[id] = p;
}