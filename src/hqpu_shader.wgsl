struct VortexQubit {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    spin_omega: f32,
    wake_amplitude: f32,
    padding1: f32,
    padding2: f32,
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
};

@group(0) @binding(0) var<storage, read_write> qubits: array<VortexQubit>;
@group(0) @binding(1) var<uniform> params: Params;

// Função Hash para o caos determinístico
fn hash3(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

// Cálculo do gradiente baseado em amostragem de vizinhança (Stencil de 6 pontos)
fn calculate_vacuum_gradient(pos: vec2<f32>) -> vec2<f32> {
    let eps = 0.1;
    let s0 = hash3(pos + vec2<f32>(eps, 0.0));
    let s1 = hash3(pos + vec2<f32>(-eps, 0.0));
    let s2 = hash3(pos + vec2<f32>(0.0, eps));
    let s3 = hash3(pos + vec2<f32>(0.0, -eps));
    
    // Gradiente aproximado (Derivadas espaciais discretas)
    return vec2<f32>(s0 - s1, s2 - s3) / (2.0 * eps);
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
    let idx = id.x;
    if (idx >= params.total_photons) { return; }

    var q = qubits[idx];

    // 1. Aplicação do Portão Lógico (Obstáculo Termodinâmico)
    if (q.y > 100.0 && q.y < 150.0) {
        let grad = calculate_vacuum_gradient(vec2<f32>(q.x, q.y));
        let base_tension = 5.0;
        let gradient_pressure = sin(q.y * 0.2) * base_tension;
        
        q.spin_omega += gradient_pressure * 0.05;
        q.vx += gradient_pressure * 0.02 + grad.x * 0.1;
    }

    // 2. Evolução Dinâmica
    q.x += q.vx * 0.1;
    q.y += q.vy * 0.1;
    q.spin_omega += 0.15 * 0.1; 

    // Atualiza o estado na GPU
    qubits[idx] = q;
}