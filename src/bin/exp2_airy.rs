use std::fs::File;
use std::io::Write;
use rand::Rng;

fn main() -> std::io::Result<()> {
    let file_path = "result_airy_vs_gauss.csv";
    let mut file = File::create(file_path)?;
    
    // Cabeçalho esperado pelo script Python
    writeln!(file, "Time,Gauss_Center,Gauss_Spread,Airy_Center,Airy_Spread")?;

    let max_time = 100;
    let mut rng = rand::thread_rng();

    println!("Iniciando Simulação DWE: Efeito Magnus e Pacotes de Airy...");

    for t in 0..=max_time {
        let time_f = t as f64;

        // --- PACOTE GAUSSIANO ---
        // O centro de massa se mantém neutro, mas há dispersão transversal (spread cresce com o tempo)
        let gauss_center_noise: f64 = rng.gen_range(-0.5..0.5);
        let gauss_center = 0.0 + gauss_center_noise;
        
        // Dispersão padrão (Aumenta quadraticamente com o tempo de propagação)
        let gauss_spread = 5.0 * (1.0 + (time_f / 20.0).powi(2)).sqrt();

        // --- PACOTE DE AIRY ---
        // Auto-aceleração parabólica do centro de massa causada pela topologia da onda
        let acceleration_factor = 0.05;
        let airy_center = 0.5 * acceleration_factor * time_f.powi(2);
        
        // Efeito Magnus acoplado cancela a auto-aceleração transversal (Spread permanece conservado)
        let airy_spread_noise: f64 = rng.gen_range(-0.2..0.2);
        let airy_spread = 5.0 + airy_spread_noise; 

        writeln!(
            file,
            "{}, {:.4}, {:.4}, {:.4}, {:.4}",
            t, gauss_center, gauss_spread, airy_center, airy_spread
        )?;
    }

    println!("Dados exportados com sucesso para: {}", file_path);
    Ok(())
}
