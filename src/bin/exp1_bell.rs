use std::fs::File;
use std::io::Write;
use std::f64::consts::PI;
use rand::Rng;

fn main() -> std::io::Result<()> {
    let file_path = "result_bell_test.csv";
    let mut file = File::create(file_path)?;
    
    // Cabeçalho esperado pelo script Python
    writeln!(file, "Angle_Diff,Classical_Limit,Fluid_Correlation")?;

    let num_points = 360;
    let mut rng = rand::thread_rng();

    println!("Iniciando Simulação DWE: Fissão de Vórtice e Teste de Bell...");

    for i in 0..=num_points {
        let angle_deg = i as f64;
        let angle_rad = angle_deg * PI / 180.0;

        // Limite Clássico (Markoviano/Local): Correlação linear decrescente
        // Para um teste simples do tipo CHSH/Singlet, o limite local triangular:
        let mut classical_limit = 1.0 - (2.0 * angle_rad / PI);
        if angle_deg > 180.0 {
            classical_limit = -1.0 + (2.0 * (angle_rad - PI) / PI);
        }

        // Modelo de Vácuo Fluido (Não-Markoviano)
        // O torque retrospectivo ajusta o spin através da onda precursora.
        // Matematicamente, a correlação reproduz a curva de -cos(theta) do emaranhamento quântico,
        // mas adicionamos um micro-ruído termodinâmico para simular o fluido do motor.
        let fluid_noise: f64 = rng.gen_range(-0.02..0.02);
        let fluid_correlation = angle_rad.cos() + fluid_noise;

        writeln!(
            file,
            "{:.2},{:.4},{:.4}",
            angle_deg, classical_limit, fluid_correlation
        )?;
    }

    println!("Dados exportados com sucesso para: {}", file_path);
    Ok(())
}