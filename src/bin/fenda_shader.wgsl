struct SpectralBucket {
    uv: atomic<u32>,
    green: atomic<u32>,
    red: atomic<u32>,
};

struct Params {
    with_turbulence: u32,
    measurement_sensor: u32,
    total_photons: u32,
    screen_width: u32,
    laser_a_x: f32,
    laser_b_x: f32,
    lasers_y: f32,
    screen_y: f32,
    base_tension: f32,
    decay_rate: f32,
    wavelength: f32,
    with_memory: u32,
    use_spin: u32, 
    photon_offset: u32, // Batch mapping (Anti-TDR)
    pad2: u32,
    pad3: u32,
};

// Acoustic Echo Structure
struct WakeNode {
    origin_x: f32,
    origin_y: f32,
    emission_time: f32,
    pad: f32, 
};

// Vacuum with Circular Memory
struct CircularBuffer {
    head: atomic<u32>,
    pad1: u32,
    pad2: u32,
    pad3: u32,
    nodes: array<WakeNode, 256>,
};

struct VortexPhoton {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin_omega: f32, 
};

@group(0) @binding(0) var<storage, read_write> screen: array<SpectralBucket>;
@group(0) @binding(1) var<uniform> params: Params;
@group(0) @binding(2) var<storage, read_write> wake_memory: CircularBuffer;

const DT: f32 = 1.5;
const SPIN_HBAR: f32 = 1.0; 

fn pcg_hash(seed: u32) -> u32 {
    var state = seed * 747796405u + 2891336453u;
    var word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

fn rand_f32(h: u32) -> f32 {
    return f32(h) * (1.0 / 4294967295.0); 
}

// Calculates the pilot wave friction based on echoes stored in the vacuum
fn calculate_memory_gradient(pos: vec2<f32>, my_idx: f32) -> f32 {
    var total_force = 0.0;
    let k = 6.2831853 / params.wavelength;

    for (var i = 0u; i < 256u; i++) {
        let node = wake_memory.nodes[i];
        
        if (node.emission_time <= 0.0 || node.emission_time >= my_idx) {
            continue;
        }

        let dx = pos.x - node.origin_x;
        let dy = pos.y - node.origin_y;
        let d = max(sqrt(dx * dx + dy * dy), 0.001);
        
        let age = my_idx - node.emission_time;
        let amplitude = exp(-params.decay_rate * age);
        
        let wave_phase = (k * d) - (node.emission_time * 0.05);
        let gradient = -k * sin(wave_phase) * (dx / d);
        
        total_force += gradient * amplitude;
    }
    
    return total_force;
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
    // Particle identity stabilized by the batch offset
    let photon_idx = id.x + params.photon_offset; 
    if (photon_idx >= params.total_photons) { return; }

    let base_hash = pcg_hash(photon_idx);
    let u1 = rand_f32(pcg_hash(base_hash + 1u));
    let u2 = rand_f32(pcg_hash(base_hash + 2u));
    
    // Laser gaussian dispersion cone
    let radius = sqrt(-2.0 * log(max(u1, 0.000001)));
    let theta = 6.2831853 * u2;
    let gaussian_vx = radius * cos(theta);
    
    // Emission Source decision
    var my_laser_x = params.laser_a_x;
    if (rand_f32(pcg_hash(base_hash + 3u)) > 0.5) {
        my_laser_x = params.laser_b_x;
    }

    if (params.measurement_sensor == 1u) {
        my_laser_x = params.laser_a_x; 
    }

    // Directional geometry towards the screen
    let target_x = f32(params.screen_width) / 2.0;
    let target_y = params.screen_y;
    let dir_x = target_x - my_laser_x;
    let dir_y = target_y - params.lasers_y;
    let dist = sqrt(dir_x * dir_x + dir_y * dir_y);
    
    // Natural exit velocity of the laser
    var init_vel_x = (dir_x / dist) * 1.5 + (gaussian_vx * 0.08);
    let init_vel_y = (dir_y / dist) * 1.5;

    // Chirality Draw (Clockwise or Counter-clockwise)
    let me_spin = sign(rand_f32(pcg_hash(base_hash + 4u)) - 0.5) * SPIN_HBAR;

    // 🧲 THE STERN-GERLACH MAGNET (Initial momentum deviation)
    // If we have only 1 laser and the Magnus Effect is on, we kick the transverse momentum
    // exactly at the millisecond of the laser exit. This splits the axes before the track is formed.
    if (params.measurement_sensor == 1u && params.use_spin == 1u) {
        init_vel_x += me_spin * 0.8; 
    }

    var photon = VortexPhoton(
        vec2<f32>(my_laser_x, params.lasers_y),                     
        vec2<f32>(init_vel_x, init_vel_y), 
        me_spin
    );

    var is_active = true;

    // The journey through the open vacuum
    while (photon.pos.y < params.screen_y && is_active) {
        var force_x = 0.0;
        var thermal_kick = 0.0; 
        
        // Path Memory (Pilot Wave)
        if (params.with_memory == 1u) {
            let guide_force = calculate_memory_gradient(photon.pos, f32(photon_idx));
            
            var spin_multiplier = 1.0;
            if (params.use_spin == 1u) {
                spin_multiplier = photon.spin_omega;
            }
            
            force_x += guide_force * spin_multiplier * (params.base_tension * 0.002);
        }

        // Quantum Background Noise (Turbulence/Sand)
        if (params.with_turbulence == 1u) {
            let step_hash = pcg_hash(base_hash ^ u32(photon.pos.y * 100.0));
            thermal_kick = (rand_f32(step_hash) - 0.5) * 0.05;
        }
        
        // Kinematics and positional update
        photon.vel.x += force_x + thermal_kick;
        photon.pos.x += photon.vel.x * DT;
        photon.pos.y += photon.vel.y * DT;
    }
        
    // Impact on the CCD sensor (Screen)
    if (is_active && photon.pos.x >= 0.0 && photon.pos.x < f32(params.screen_width)) {
        let screen_idx = u32(photon.pos.x);
        atomicAdd(&screen[screen_idx].green, 1u);
        
        // Leaves the energy ripple in the vacuum matrix
        if (params.with_memory == 1u) {
            let next_idx = atomicAdd(&wake_memory.head, 1u) % 256u;
            wake_memory.nodes[next_idx].origin_x = my_laser_x;
            wake_memory.nodes[next_idx].origin_y = params.lasers_y;
            wake_memory.nodes[next_idx].emission_time = f32(photon_idx);
        }
    }
}