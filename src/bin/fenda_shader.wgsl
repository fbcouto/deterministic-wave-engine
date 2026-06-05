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

struct VortexPhoton {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin_omega: f32, // Agora armazena a orientação/sinal do Spin Invariável
    wavelength: f32,
    color_channel: u32,
};

@group(0) @binding(0) var<storage, read_write> screen: array<SpectralBucket>;
@group(0) @binding(1) var<uniform> params: Params;

// DISTÂNCIAS DO LABORATÓRIO E CONSTANTES FÍSICAS GLOBAIS
const SLITS_Y_POS: f32 = 200.0;
const SCREEN_Y_POS: f32 = 800.0;
const DT: f32 = 2.0;
const FLUID_C: f32 = 300.0;
const SPIN_HBAR: f32 = 1.0; // NOVO PARADIGMA: O spin do fotão é fixo e invariável.

fn pcg_hash(seed: u32) -> u32 {
    var state = seed * 747796405u + 2891336453u;
    var word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

fn rand_f32(h: u32) -> f32 {
    return f32(h) * (1.0 / 4294967295.0); 
}

fn hash2(p: vec2<f32>) -> f32 {
    return fract(sin(dot(p, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

fn curl_noise(pos: vec2<f32>, photon_seed: f32) -> f32 {
    let p = pos + vec2<f32>(photon_seed, -photon_seed);
    let n1 = hash2(p + vec2<f32>(0.1, 0.0));
    let n2 = hash2(p - vec2<f32>(0.1, 0.0));
    return (n1 - n2) * 1.5; 
}

fn calculate_gradient(x: f32, y: f32, wavelength: f32, sensor_active: u32) -> f32 {
    let left_slit_x = params.center_x - (params.slits_distance / 2.0);
    let right_slit_x = params.center_x + (params.slits_distance / 2.0);
    
    let d1 = distance(vec2<f32>(x, y), vec2<f32>(left_slit_x, SLITS_Y_POS));
    let d2 = distance(vec2<f32>(x, y), vec2<f32>(right_slit_x, SLITS_Y_POS));
    
    // A periodicidade espacial da esteira mecânica é governada pelo comprimento de onda (1/nu)
    let k = 6.28318 / wavelength; 
    let phase1 = k * d1;
    let phase2 = k * d2;
    
    if (sensor_active == 1u) {
        return sin(phase1);
    } else {
        return sin(phase1) + sin(phase2);
    }
}

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {
    let photon_idx = id.y * 16640000u + id.x;
    if (photon_idx >= params.total_photons) { return; }

    let base_hash = pcg_hash(photon_idx);
    let p_seed = rand_f32(base_hash); 
    
    let u1 = rand_f32(pcg_hash(base_hash + 1u));
    let u2 = rand_f32(pcg_hash(base_hash + 2u));
    
    let radius = sqrt(-2.0 * log(max(u1, 0.000001)));
    let theta = 6.2831853 * u2;
    let gaussian_vx = radius * cos(theta);
    
    let divergence = 1.5;
    
    var photon = VortexPhoton(
        vec2<f32>(params.center_x, 0.0),                     
        vec2<f32>(gaussian_vx * divergence, 5.0),      
        0.0,
        10.0, 
        1u
    );
    
    let color_rand = rand_f32(pcg_hash(base_hash + 3u));
    if (color_rand < 0.1) {
        photon.wavelength = 8.0; 
        photon.color_channel = 0u;
    } else if (color_rand > 0.65) {
        photon.wavelength = 12.0; 
        photon.color_channel = 2u;
    }

    let spin_rand = rand_f32(pcg_hash(base_hash + 4u));
    let spin_direction = sign(spin_rand - 0.5); 
    
    // O spin ganha a direção, mas usa a magnitude global fixa.
    photon.spin_omega = spin_direction * SPIN_HBAR;

    var is_active = true;

    while (photon.pos.y < SCREEN_Y_POS && is_active) {
        var force_x = 0.0;
        
        if (photon.pos.y < SLITS_Y_POS) {
            // Zona de Voo Livre
        } 
        // ZONA B: A COLISÃO MECÂNICA (Fricção Invariável de Borda)
        else if (photon.pos.y >= SLITS_Y_POS && photon.pos.y - photon.vel.y * DT < SLITS_Y_POS) {
            let half_width = params.slit_width / 2.0;
            let left_center = params.center_x - (params.slits_distance / 2.0);
            let right_center = params.center_x + (params.slits_distance / 2.0);

            let left_slit_min = left_center - half_width;
            let left_slit_max = left_center + half_width;
            let right_slit_min = right_center - half_width;
            let right_slit_max = right_center + half_width;
            
            let in_left = photon.pos.x >= left_slit_min && photon.pos.x <= left_slit_max;
            let in_right = photon.pos.x >= right_slit_min && photon.pos.x <= right_slit_max;
            
            if (!in_left && !in_right) {
                is_active = false; 
                break; 
            }
            
            if (params.with_deflection == 1u && params.measurement_sensor == 0u) {
                var dist_to_edge = 0.0;
                var normal_vetor = 0.0; 
                
                if (in_left) {
                    let d_min = photon.pos.x - left_slit_min;
                    let d_max = left_slit_max - photon.pos.x;
                    if (d_min < d_max) { dist_to_edge = d_min; normal_vetor = 1.0; }
                    else { dist_to_edge = d_max; normal_vetor = -1.0; }
                } else {
                    let d_min = photon.pos.x - right_slit_min;
                    let d_max = right_slit_max - photon.pos.x;
                    if (d_min < d_max) { dist_to_edge = d_min; normal_vetor = 1.0; }
                    else { dist_to_edge = d_max; normal_vetor = -1.0; }
                }

                let safe_dist = max(dist_to_edge, 0.2);
                
                // 1. O Ricochete Geométrico
                let elastic_bounce = normal_vetor * (1.5 / safe_dist);
                
                // 2. A Fricção Mecânica (Ajustada para o spin unitário estável)
                let spin_traction = (photon.spin_omega * 1.5) / safe_dist;
                
                photon.vel.x += (elastic_bounce + spin_traction) * 2.5; 
            }
            
            // O Sensor introduz atrito térmico catastrófico destruindo a rotação (w -> 0)
            if (params.measurement_sensor == 1u && in_right) {
                let kick_rand = rand_f32(pcg_hash(base_hash + 5u));
                photon.vel.x += (kick_rand - 0.5) * 12.0; 
                photon.spin_omega = 0.0; // Colapso mecânico determinístico da helicidade
            }
        }
        // ZONA C: O GRADIENTE DE INTERFERÊNCIA (Modulado pela compactação topológica)
        else {
            if (params.with_deflection == 1u) {
                let grad = calculate_gradient(photon.pos.x, photon.pos.y, photon.wavelength, params.measurement_sensor);
                
                // A frequência (nu = c / lambda) dita a densidade energética do núcleo comprimido
                let frequency = FLUID_C / photon.wavelength;
                force_x += grad * (frequency * params.base_tension * 0.0005);
            }
            if (params.with_turbulence == 1u) {
                force_x += curl_noise(photon.pos * 0.05, p_seed);
            }
        }
        
        photon.vel.x += force_x * 0.1;
        photon.pos.x += photon.vel.x * DT;
        photon.pos.y += photon.vel.y * DT;
    }

    if (is_active && photon.pos.x >= 0.0 && photon.pos.x < f32(params.screen_width)) {
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