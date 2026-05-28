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
};

@group(0) @binding(0) var<storage, read_write> screen: array<SpectralBucket>;
@group(0) @binding(1) var<uniform> params: Params;

const SLITS_Y_POS: f32 = 200.0;
const SCREEN_Y_POS: f32 = 800.0;
const DT: f32 = 2.0;

fn hash2(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

fn curl_noise(pos: vec2<f32>) -> f32 {
    let n1 = hash2(pos + vec2<f32>(0.1, 0.0));
    let n2 = hash2(pos - vec2<f32>(0.1, 0.0));
    return (n1 - n2) * 15.0;
}

// O Gradiente Hidrodinâmico com Sensibilidade de Colapso
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
        // COLAPSO REAL: O sensor absorve a propagação da onda da fenda direita.
        // O vácuo só propaga a onda esférica da fenda esquerda.
        // Sem cruzamento de ondas = sem padrão de interferência!
        pressure_gradient = sin(phase1); 
    } else {
        // CAMPO NORMAL: Cruzamento simétrico de ondas (Feynman).
        pressure_gradient = sin(phase1) + sin(phase2);
    }
    
    // Tensão restaurada para criar picos fortes e concentrados
    return pressure_gradient * 3.0; 
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
    
    var pos = vec2<f32>(pos_x, SLITS_Y_POS);
    var vel = vec2<f32>(0.0, 5.0);
    
    let color_rand = hash2(vec2<f32>(seed, 4.0));
    var wavelength = 10.0;
    var color_channel = 1u;
    
    if (color_rand < 0.1) {
        wavelength = 8.0;
        color_channel = 0u;
    } else if (color_rand > 0.65) {
        wavelength = 12.0;
        color_channel = 2u;
    }

    // Impacto termodinâmico severo na partícula se passar pelo sensor
    if (params.measurement_sensor == 1u && !is_left_slit) {
        vel.x += (hash2(vec2<f32>(seed, 8.5)) - 0.5) * 15.0;
    }

    while (pos.y < SCREEN_Y_POS) {
        var force_x = 0.0;
        
        if (params.with_deflection == 1u) {
            force_x += calculate_gradient(pos.x, pos.y, wavelength, params.measurement_sensor);
        }
        
        if (params.with_turbulence == 1u) {
            force_x += curl_noise(pos * 0.05);
        }
        
        vel.x += force_x * 0.1;
        pos.x += vel.x * DT;
        pos.y += vel.y * DT;
    }

    if (pos.x >= 0.0 && pos.x < f32(params.screen_width)) {
        let screen_idx = u32(pos.x);
        if (color_channel == 0u) {
            atomicAdd(&screen[screen_idx].uv, 1u);
        } else if (color_channel == 1u) {
            atomicAdd(&screen[screen_idx].green, 1u);
        } else {
            atomicAdd(&screen[screen_idx].red, 1u);
        }
    }
}