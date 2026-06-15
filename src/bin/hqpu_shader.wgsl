struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,     // Direction/Phase of the Invariable Spin Helicity
    frequency: f32,      // NEW: Mapped topological compaction of the core
    wake_amplitude: f32, // Thermodynamic wake force
    padding1: f32,       // Strict 32-byte alignment (8 floats)
};

struct Params {
    with_deflection: u32,
    with_turbulence: u32,
    measurement_sensor: u32,
    total_photons: u32,
    screen_width: u32,
    center_x: f32,
    slits_distance: f32,
    slit_width: f32,
    base_tension: f32,
    pad1: u32,
    pad2: u32,
    pad3: u32,
};

@group(0) @binding(0) var<storage, read_write> qubits: array<VortexQubit>;
@group(0) @binding(1) var<uniform> params: Params;

fn hash3(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

fn calculate_vacuum_gradient(pos: vec2<f32>) -> vec2<f32> {
    let eps = 0.1;
    let s0 = hash3(pos + vec2<f32>(eps, 0.0));
    let s1 = hash3(pos + vec2<f32>(-eps, 0.0));
    let s2 = hash3(pos + vec2<f32>(0.0, eps));
    let s3 = hash3(pos + vec2<f32>(0.0, -eps));
    
    return vec2<f32>(s0 - s1, s2 - s3) / (2.0 * eps);
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
    let idx = id.x;
    if (idx >= params.total_photons) { return; }

    var q = qubits[idx];

    // 1. Application of the Logic Gate (Hydrodynamic Obstacle)
    if (q.y > 100.0 && q.y < 150.0) {
        let grad = calculate_vacuum_gradient(vec2<f32>(q.x, q.y));
        let gradient_pressure = sin(q.y * 0.2) * params.base_tension;
        
        q.spin_omega += gradient_pressure * 0.05;
        
        // The lateral kinematic deviation now depends on the frequency compaction force
        q.vx += gradient_pressure * (q.frequency * 0.00066) * sign(q.spin_omega) + grad.x * 0.1;
    }

    // 2. Temporal Evolution of Position
    q.x += q.vx * 0.1;
    q.y += q.vy * 0.1;
    
    q.spin_omega += 0.15 * 0.1 * sign(q.spin_omega); 

    qubits[idx] = q;
}