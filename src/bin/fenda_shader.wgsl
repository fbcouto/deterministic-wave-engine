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
    with_pilot_wave: u32,
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

const SLITS_Y_POS: f32 = 400.0;
const SCREEN_Y_POS: f32 = 500.0;
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

fn calculate_gradient(x: f32, y: f32, wavelength: f32, sensor_active: u32) -> f32 {
    if (sensor_active == 1u) {
        return 0.0; // Decoerência ativada: A onda guia morre
    }

    let left_slit_x = params.center_x - (params.slits_distance / 2.0);
    let right_slit_x = params.center_x + (params.slits_distance / 2.0);
    
    let dx1 = x - left_slit_x;
    let dy1 = y - SLITS_Y_POS;
    let d1 = sqrt(dx1 * dx1 + dy1 * dy1);
    
    let dx2 = x - right_slit_x;
    let dy2 = y - SLITS_Y_POS;
    let d2 = sqrt(dx2 * dx2 + dy2 * dy2);
    
    let k = 6.2831853 / wavelength;

    let safe_d1 = max(d1, 0.001);
    let safe_d2 = max(d2, 0.001);

    let grad_p1_x = -k * sin(k * d1) * (dx1 / safe_d1);
    let grad_p2_x = -k * sin(k * d2) * (dx2 / safe_d2);
    
    return grad_p1_x + grad_p2_x;
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
    
    let divergence = 0.85; 
    
    var photon = VortexPhoton(
        vec2<f32>(params.center_x, 0.0),                     
        vec2<f32>(gaussian_vx * divergence, 0.75), 
        0.0,
        11.0, 
        1u
    );
    
    let spin_rand = rand_f32(pcg_hash(base_hash + 4u));
    let spin_direction = sign(spin_rand - 0.5); 
    photon.spin_omega = spin_direction * SPIN_HBAR;

    var is_active = true;

    while (photon.pos.y < SCREEN_Y_POS && is_active) {
        var force_x = 0.0;
        var thermal_kick = 0.0; 
        
        if (photon.pos.y < SLITS_Y_POS) {
            if (params.with_pilot_wave == 1u && params.measurement_sensor == 0u) {
                let source_x = params.center_x;
                let source_y = 0.0; 
                
                let dx = photon.pos.x - source_x;
                let dy = photon.pos.y - source_y;
                let d = sqrt(dx * dx + dy * dy);
                
                let k = 6.2831853 / photon.wavelength;
                let safe_d = max(d, 0.001);
                
                let single_wave_gradient = -k * sin(k * d) * (dx / safe_d);
                force_x += single_wave_gradient * (params.base_tension * 0.5); 
            }
        } 
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
                var normal_vector = 0.0; 
                
                if (in_left) {
                    let d_min = photon.pos.x - left_slit_min;
                    let d_max = left_slit_max - photon.pos.x;
                    if (d_min < d_max) { dist_to_edge = d_min; normal_vector = 1.0; }
                    else { dist_to_edge = d_max; normal_vector = -1.0; }
                } else {
                    let d_min = photon.pos.x - right_slit_min;
                    let d_max = right_slit_max - photon.pos.x;
                    if (d_min < d_max) { dist_to_edge = d_min; normal_vector = 1.0; }
                    else { dist_to_edge = d_max; normal_vector = -1.0; }
                }

                let safe_dist = max(dist_to_edge, 0.2);
                let elastic_bounce = normal_vector * (1.5 / safe_dist);
                
                let step_hash = pcg_hash(base_hash ^ u32(abs(photon.pos.y) * 100.0));
                let spin_variance = rand_f32(step_hash); 
                let spin_traction = (photon.spin_omega * 1.5 * spin_variance) / safe_dist;
                
                photon.vel.x += (elastic_bounce + spin_traction) * 2.5; 
            }
            
            // O ATO DA MEDIÇÃO
            if (params.measurement_sensor == 1u && in_right) {
                let kick_rand = rand_f32(pcg_hash(base_hash + 5u));
                // Impacto cinético suave que destrói a ressonância sem pulverizar a partícula
                photon.vel.x += (kick_rand - 0.5) * 0.5; 
                photon.spin_omega = 0.0; // Perda total do spin (Decoerência)
            }
        }
        else {
            if (params.with_pilot_wave == 1u) {
                let guide_force = calculate_gradient(photon.pos.x, photon.pos.y, photon.wavelength, params.measurement_sensor);
                force_x += guide_force * params.base_tension;
            }
            
            if (params.with_vortices == 1u) {
                let hw = params.slit_width / 2.0;
                let left_center = params.center_x - (params.slits_distance / 2.0);
                let right_center = params.center_x + (params.slits_distance / 2.0);
                
                let gamma = 1500.0; 
                let eps = 100.0;    

                let v_y_out = SLITS_Y_POS + 0.5; 
                let r_y_out = photon.pos.y - v_y_out;
                let sq_l_out = r_y_out * r_y_out + eps;
                
                let f1_x_out = -gamma * r_y_out / ((photon.pos.x - (left_center - hw)) * (photon.pos.x - (left_center - hw)) + sq_l_out); 
                let f2_x_out = gamma * r_y_out / ((photon.pos.x - (left_center + hw)) * (photon.pos.x - (left_center + hw)) + sq_l_out);  
                let f3_x_out = -gamma * r_y_out / ((photon.pos.x - (right_center - hw)) * (photon.pos.x - (right_center - hw)) + sq_l_out); 
                let f4_x_out = gamma * r_y_out / ((photon.pos.x - (right_center + hw)) * (photon.pos.x - (right_center + hw)) + sq_l_out);  

                let v_y_in = SLITS_Y_POS - 0.5; 
                let r_y_in = photon.pos.y - v_y_in;
                let sq_l_in = r_y_in * r_y_in + eps;
                
                let f1_x_in = gamma * r_y_in / ((photon.pos.x - (left_center - hw)) * (photon.pos.x - (left_center - hw)) + sq_l_in); 
                let f2_x_in = -gamma * r_y_in / ((photon.pos.x - (left_center + hw)) * (photon.pos.x - (left_center + hw)) + sq_l_in);  
                let f3_x_in = gamma * r_y_in / ((photon.pos.x - (right_center - hw)) * (photon.pos.x - (right_center - hw)) + sq_l_in); 
                let f4_x_in = -gamma * r_y_in / ((photon.pos.x - (right_center + hw)) * (photon.pos.x - (right_center + hw)) + sq_l_in);

                force_x += (f1_x_out + f2_x_out + f3_x_out + f4_x_out + f1_x_in + f2_x_in + f3_x_in + f4_x_in) * 1.0; 
            }

            if (params.with_turbulence == 1u) {
                let step_hash = pcg_hash(base_hash ^ u32(photon.pos.y * 100.0));
                let base_kick = rand_f32(step_hash) - 0.5;
                
                // FREIOS TERMODINÂMICOS DE DECOERÊNCIA
                // Se o experimento é Clássico (Areia) OU se a onda foi Colapsada pelo Sensor:
                if (params.with_pilot_wave == 0u || params.measurement_sensor == 1u) {
                    // O banho fluido dissolve-se e a partícula viaja de forma quase balística
                    thermal_kick = base_kick * 0.04; 
                } else {
                    // Se o estado for Coerente (Figura D), aplica o micro-ruído quântico contínuo
                    thermal_kick = base_kick * 1.2;
                }
            }
        }
        
        let coupling_factor = 0.045; 
        photon.vel.x += force_x * coupling_factor;
        
        photon.vel.x += thermal_kick;
        
        let vacuum_drag = 0.996; 
        photon.vel.x *= vacuum_drag; 
        
        photon.pos.x += photon.vel.x * DT;
        photon.pos.y += photon.vel.y * DT;
    }
        
    if (is_active && photon.pos.x >= 0.0 && photon.pos.x < f32(params.screen_width)) {
        let screen_idx = u32(photon.pos.x);
        atomicAdd(&screen[screen_idx].green, 1u);
    }
}