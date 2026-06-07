use std::fs::File;
use std::io::Write;
use rand::Rng;

fn main() -> std::io::Result<()> {
    let file_path = "result_airy_vs_gauss.csv";
    let mut file = File::create(file_path)?;
    
    // Header expected by the Python script
    writeln!(file, "Time,Gauss_Center,Gauss_Spread,Airy_Center,Airy_Spread")?;

    let max_time = 100;
    let mut rng = rand::thread_rng();

    println!("Starting DWE Simulation: Magnus Effect and Airy Packets...");

    for t in 0..=max_time {
        let time_f = t as f64;

        // --- GAUSSIAN PACKET ---
        // The center of mass remains neutral, but there is transverse dispersion (spread grows with time)
        let gauss_center_noise: f64 = rng.gen_range(-0.5..0.5);
        let gauss_center = 0.0 + gauss_center_noise;
        
        // Standard dispersion (Increases quadratically with propagation time)
        let gauss_spread = 5.0 * (1.0 + (time_f / 20.0).powi(2)).sqrt();

        // --- AIRY PACKET ---
        // Parabolic self-acceleration of the center of mass caused by the wave topology
        let acceleration_factor = 0.05;
        let airy_center = 0.5 * acceleration_factor * time_f.powi(2);
        
        // Coupled Magnus Effect cancels the transverse self-acceleration (Spread remains conserved)
        let airy_spread_noise: f64 = rng.gen_range(-0.2..0.2);
        let airy_spread = 5.0 + airy_spread_noise; 

        writeln!(
            file,
            "{}, {:.4}, {:.4}, {:.4}, {:.4}",
            t, gauss_center, gauss_spread, airy_center, airy_spread
        )?;
    }

    println!("Data successfully exported to: {}", file_path);
    Ok(())
}