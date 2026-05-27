use rayon::prelude::*;
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicU32, Ordering};
use std::time::Instant;

// ==========================================
// GENERAL LABORATORY PARAMETERS
// ==========================================
const SCREEN_RESOLUTION_X: usize = 1000;
const TOTAL_PHOTONS: usize = 1_500_000; 

const SLITS_Y_POS: f32 = 200.0;
const SCREEN_Y_POS: f32 = 800.0;
const CENTER_X: f32 = 500.0;

const SLITS_DISTANCE: f32 = 60.0; 
const SLIT_WIDTH: f32 = 15.0;   

const WAVE_SPEED_C: f32 = 2.0;       
const INITIAL_TENSION_GAMMA: f32 = 5.0; 

struct Photon {
    x: f32, y: f32, vx: f32, vy: f32,
    wavelength: f32, color_id: usize,
}

struct SpectralBucket {
    uv: AtomicU32, green: AtomicU32, red: AtomicU32,
}

impl SpectralBucket {
    fn new() -> Self {
        SpectralBucket { uv: AtomicU32::new(0), green: AtomicU32::new(0), red: AtomicU32::new(0) }
    }
}

// ==========================================
// THEORETICAL POSTULATION TEST BENCH
// ==========================================
fn main() {
    println!("Starting Theoretical Postulation Test Matrix (Double Slit)...\n");

    // Scenario A: Classical particles in an absolute void
    simulate(false, false, "result_A_newton.csv");
    
    // Scenario B: Classical particles falling into a trembling medium
    simulate(false, true,  "result_B_sand.csv");
    
    // Scenario C: Only the wave field operating mathematically
    simulate(true, false, "result_C_comb.csv");
    
    // Scenario D: The Complete Fluid Vacuum (Wave + Turbulence)
    simulate(true, true,  "result_D_feynman.csv");

    println!("\nTest suite completed. 4 CSV files generated successfully!");
}

fn simulate(with_deflection: bool, with_turbulence: bool, filename: &str) {
    let start = Instant::now();
    let deflex_status = if with_deflection { "ON " } else { "OFF" };
    let turb_status = if with_turbulence { "ON " } else { "OFF" };
    print!(" -> Deflection [{}]: Turbulence [{}]: Processing... ", deflex_status, turb_status);
    std::io::stdout().flush().unwrap();

    let mut screen: Vec<SpectralBucket> = Vec::with_capacity(SCREEN_RESOLUTION_X);
    for _ in 0..SCREEN_RESOLUTION_X { screen.push(SpectralBucket::new()); }

    (0..TOTAL_PHOTONS).into_par_iter().for_each(|photon_id| {
        let (wave, c_id) = match photon_id % 3 {
            0 => (10.0, 0), 1 => (15.0, 1), _ => (22.0, 2),
        };

        // NEW: Photons physically spawn inside the two slits!
        // This allows projecting the straight geometric shadow if there is no wave field.
        let spread = (photon_id as f32 / TOTAL_PHOTONS as f32) * SLIT_WIDTH - (SLIT_WIDTH / 2.0);
        let initial_x = if photon_id % 2 == 0 {
            CENTER_X - (SLITS_DISTANCE / 2.0) + spread
        } else {
            CENTER_X + (SLITS_DISTANCE / 2.0) + spread
        };
        
        let mut photon = Photon {
            x: initial_x, y: SLITS_Y_POS + 1.0, vx: 0.0, vy: 3.0,
            wavelength: wave, color_id: c_id,
        };

        let mut local_time = 0.0;
        let dt = 0.1; 

        while photon.y < SCREEN_Y_POS {
            local_time += dt;
            
            // FORCES ISOLATION
            let force_x = if with_deflection {
                calculate_gradient(&photon, local_time)
            } else {
                0.0 // No mechanical field to push the photons
            };

            let vortex_fluctuation = if with_turbulence {
                (photon.x * 0.2).cos() * 0.08
            } else {
                0.0 // Completely frozen vacuum
            };

            photon.vx += (force_x + vortex_fluctuation) * dt;
            photon.x += photon.vx * dt;
            photon.y += photon.vy * dt;
        }

        let impact_x = photon.x.round() as usize;
        if impact_x > 0 && impact_x < SCREEN_RESOLUTION_X {
            match photon.color_id {
                0 => screen[impact_x].uv.fetch_add(1, Ordering::Relaxed),
                1 => screen[impact_x].green.fetch_add(1, Ordering::Relaxed),
                _ => screen[impact_x].red.fetch_add(1, Ordering::Relaxed),
            };
        }
    });

    export_data(filename, &screen);
    println!("OK ({:.2?})", start.elapsed());
}

fn calculate_gradient(photon: &Photon, current_time: f32) -> f32 {
    let frequency = WAVE_SPEED_C / photon.wavelength;
    let k_wave = std::f32::consts::PI * 2.0 / photon.wavelength;
    let omega = std::f32::consts::PI * 2.0 * frequency;

    let mut total_gradient = 0.0;
    let opening_step = SLIT_WIDTH / 2.0;

    let center_left = CENTER_X - SLITS_DISTANCE / 2.0;
    let center_right = CENTER_X + SLITS_DISTANCE / 2.0;
    
    let sources = [
        center_left - opening_step, center_left, center_left + opening_step,
        center_right - opening_step, center_right, center_right + opening_step
    ];

    let dy = photon.y - SLITS_Y_POS; 

    for origin_x in sources.iter() {
        let dx = photon.x - origin_x; 
        let dist = (dx * dx + dy * dy).sqrt().max(0.1); 
        let phase = k_wave * dist - omega * current_time;
        let (sin_phase, cos_phase) = phase.sin_cos();
        let r3 = dist * dist * dist;
        total_gradient += (dx / r3) * (k_wave * dist * cos_phase - sin_phase);
    }

    -(total_gradient / 6.0) * INITIAL_TENSION_GAMMA
}

fn export_data(filename: &str, screen: &[SpectralBucket]) {
    let mut file = File::create(filename).expect("Failed to create CSV file");
    writeln!(file, "X_Coordinate,Ultraviolet,Green,Red").unwrap();
    for (x, bucket) in screen.iter().enumerate() {
        writeln!(file, "{},{},{},{}", x, bucket.uv.load(Ordering::Relaxed), bucket.green.load(Ordering::Relaxed), bucket.red.load(Ordering::Relaxed)).unwrap();
    }
}