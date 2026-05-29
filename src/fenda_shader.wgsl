struct SpectralBucket {
    uv: atomic<u32>,
    green: atomic<u32>,
    red: atomic<u32>,
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

// A ESTRUTURA DO VÓRTICE (Fóton)
struct VortexPhoton {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin_omega: f32,
    wavelength: f32,
    color_channel: u32,
};

@group(0) @binding(0) var<storage, read_write> screen: array<SpectralBucket>;
@group(0) @binding(1) var<uniform> params: Params;

const SLITS_Y_POS: f32 = 200.0;
const SCREEN_Y_POS: f32 = 800.0;
const DT: f32 = 2.0;
const FLUID_C: f32 = 300.0; // Velocidade inercial de cruzeiro no fluido

fn hash2(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

fn curl_noise(pos: vec2<f32>) -> f32 {
    let n1 = hash2(pos + vec2<f32>(0.1, 0.0));
    let n2 = hash2(pos - vec2<f32>(0.1, 0.0));
    return (n1 - n2) * 15.0;
}

fn calculate_gradient(x: f32, y: f32, wavelength: f32, sensor_active: u32) -> f32 {
    let left_slit_x = params.center_x - (params.slits_distance / 2.0);
    let right_slit_x = params.center_x + (params.slits_distance / 2.0);
    
    let d1 = distance(vec2<f32>(x, y), vec2<f32>(left_slit_x, SLITS_Y_POS));
    let d2 = distance(vec2<f32>(x, y), vec2<f32>(right_slit_x, SLITS_Y_POS));
    
    let k = 6.28318 / wavelength; 
    let phase1 = k * d1;
    let phase2 = k * d2;
    
    var pressure_gradient = 0.0;
    
    if (sensor_active == 1u) {
        pressure_gradient = sin(phase1); // Colapso simétrico
    } else {
        pressure_gradient = sin(phase1) + sin(phase2); // Superposição
    }
    
    return pressure_gradient; 
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
    let photon_idx = id.x;
    if (photon_idx >= params.total_photons) { return; }

    let seed = f32(photon_idx) * 0.12345;
    let left_slit_x = params.center_x - (params.slits_distance / 2.0);
    let right_slit_x = params.center_x + (params.slits_distance / 2.0);

    let is_left_slit = hash2(vec2<f32>(seed, 1.0)) > 0.5;
    var pos_x: f32;
    
    if (is_left_slit) {
        pos_x = left_slit_x + (hash2(vec2<f32>(seed, 2.0)) - 0.5) * params.slit_width;
    } else {
        pos_x = right_slit_x + (hash2(vec2<f32>(seed, 3.0)) - 0.5) * params.slit_width;
    }
    
    var photon = VortexPhoton(
        vec2<f32>(pos_x, SLITS_Y_POS),
        vec2<f32>(0.0, 5.0),
        0.0,
        10.0, 
        1u
    );
    
    let color_rand = hash2(vec2<f32>(seed, 4.0));
    if (color_rand < 0.1) {
        photon.wavelength = 8.0; 
        photon.color_channel = 0u;
    } else if (color_rand > 0.65) {
        photon.wavelength = 12.0; 
        photon.color_channel = 2u;
    }

    // Frequência angular é diretamente proporcional à energia de rotação
    photon.spin_omega = FLUID_C / photon.wavelength;

    if (params.measurement_sensor == 1u && !is_left_slit) {
        photon.vel.x += (hash2(vec2<f32>(seed, 8.5)) - 0.5) * 15.0;
        photon.spin_omega *= 0.5; 
    }

    // CICLO DE PROPAGAÇÃO DO VÓRTICE
    while (photon.pos.y < SCREEN_Y_POS) {
        var force_x = 0.0;
        
        if (params.with_deflection == 1u) {
            let grad = calculate_gradient(photon.pos.x, photon.pos.y, photon.wavelength, params.measurement_sensor);
            
            // Fótons mais rápidos (UV) sofrem maior fricção angular com a topologia de grade do fluido
            force_x += grad * (photon.spin_omega * params.base_tension * 0.01);
        }
        
        if (params.with_turbulence == 1u) {
            force_x += curl_noise(photon.pos * 0.05);
        }
        
        photon.vel.x += force_x * 0.1;

        /* ====================================================================
        CONCEITO: Efeito Luz Cansada (Redshift / Fricção Residual)
        TEORIA: A supercavitação elimina quase todo o atrito, mas a rotação 
        gera um micro-arrasto contínuo, fazendo o fóton transferir energia.
        COMPUTAÇÃO: Para fins de performance nesta simulação em GPU da Fenda Dupla, 
        este decaimento está comentado. A distância percorrida pelo vórtice (600px) 
        é insignificante e não provoca deformação de trajetória ou perda de energia 
        visível nestas dimensões geométricas locais.
        ====================================================================
        let residual_friction = 1.0 - (0.000002 * params.base_tension * photon.spin_omega);
        photon.vel.x *= residual_friction;
        photon.vel.y *= residual_friction;
        ==================================================================== 
        */

        photon.pos.x += photon.vel.x * DT;
        photon.pos.y += photon.vel.y * DT;
    }

    if (photon.pos.x >= 0.0 && photon.pos.x < f32(params.screen_width)) {
        let screen_idx = u32(photon.pos.x);
        if (photon.color_channel == 0u) {
            atomicAdd(&screen[screen_idx].uv, 1u);
        } else if (photon.color_channel == 1u) {
            atomicAdd(&screen[screen_idx].green, 1u);
        } else {
            atomicAdd(&screen[screen_idx].red, 1u);
        }
    }
}