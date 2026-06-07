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
    with_vortices: u32,
    pad2: u32,
    pad3: u32,
};

struct VortexPhoton {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin_omega: f32, 
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
const SPIN_HBAR: f32 = 1.0; 

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

// A FÍSICA DA INTERFERÊNCIA: Diferença de caminho acústico na malha viscoelástica
fn calculate_gradient(x: f32, y: f32, wavelength: f32, sensor_active: u32) -> f32 {
    let left_slit_x = params.center_x - (params.slits_distance / 2.0);
    let right_slit_x = params.center_x + (params.slits_distance / 2.0);
    
    let d1 = distance(vec2<f32>(x, y), vec2<f32>(left_slit_x, SLITS_Y_POS));
    let d2 = distance(vec2<f32>(x, y), vec2<f32>(right_slit_x, SLITS_Y_POS));
    
    if (sensor_active == 1u) {
        return 0.0; 
    } else {
        let path_diff = d1 - d2;
        let phase_diff = (6.2831853 / wavelength) * path_diff;
        
        // Atua como uma força restauradora para os canais de interferência construtiva
        return -sin(phase_diff);
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
        vec2<f32>(gaussian_vx * divergence, 1.5), 
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
                
                let elastic_bounce = normal_vetor * (1.5 / safe_dist);
                let spin_traction = (photon.spin_omega * 1.5) / safe_dist;
                
                photon.vel.x += (elastic_bounce + spin_traction) * 2.5; 
            }
            
            if (params.measurement_sensor == 1u && in_right) {
                let kick_rand = rand_f32(pcg_hash(base_hash + 5u));
                photon.vel.x += (kick_rand - 0.5) * 12.0; 
                photon.spin_omega = 0.0; 
            }
        }
        // ZONA C: O GRADIENTE DE INTERFERÊNCIA E FÍSICA FLUIDA
        else {
            if (params.with_deflection == 1u) {
                let guide_force = calculate_gradient(photon.pos.x, photon.pos.y, photon.wavelength, params.measurement_sensor);
                
                // AUMENTADO: De 0.4 para 0.75. 
                // A gravidade do nó central (X=1000) agora puxa com o dobro da força.
                force_x += guide_force * params.base_tension * 0.75;
            }
            
            if (params.with_turbulence == 1u) {
                force_x += curl_noise(photon.pos * 0.05, p_seed);
            }
            
            if (params.with_vortices == 1u) {
                let hw = params.slit_width / 2.0;
                let left_center = params.center_x - (params.slits_distance / 2.0);
                let right_center = params.center_x + (params.slits_distance / 2.0);
                
                let v_y = SLITS_Y_POS + 0.5; 
                
                // SUCÇÃO DE ESTEIRA PROFUNDA (DEEP WAKE):
                let circ_out = 45.0;   // Mantém o espalhamento externo intacto
                let circ_in  = 2000.0; // MAIS DO QUE O DOBRO (de 1200 para 2800).
                let eps = 100.0;       // NÚCLEO MASSIVO (de 50 para 100). A força agora atua suavemente até bem perto da tela!
                
                let r_y = photon.pos.y - v_y;

                let dx1 = photon.pos.x - (left_center - hw);
                let sq1 = dx1 * dx1 + r_y * r_y + eps;
                let f1_x = -circ_out * r_y / sq1; 

                let dx2 = photon.pos.x - (left_center + hw);
                let sq2 = dx2 * dx2 + r_y * r_y + eps;
                let f2_x = circ_in * r_y / sq2;

                let dx3 = photon.pos.x - (right_center - hw);
                let sq3 = dx3 * dx3 + r_y * r_y + eps;
                let f3_x = -circ_in * r_y / sq3;

                let dx4 = photon.pos.x - (right_center + hw);
                let sq4 = dx4 * dx4 + r_y * r_y + eps;
                let f4_x = circ_out * r_y / sq4;

                // Aumentamos a "autoridade" do fluido de 0.8 para 1.0
                force_x += (f1_x + f2_x + f3_x + f4_x) * 1.0; 
            }
        }
        
        // Mais responsividade ao empurrão (de 0.04 para 0.045)
        photon.vel.x += force_x * 0.045;
        
        // MENOS ATRITO HORIZONTAL: (De 0.995 para 0.996)
        // Permite que as partículas continuem a deslizar livremente até baterem umas nas outras no centro exato.
        photon.vel.x *= 0.996; 
        
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