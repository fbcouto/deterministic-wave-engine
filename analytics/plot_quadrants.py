import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_quadrants_visual_calibrated():
    quadrants = [
        ("../result_A_newton_gpu.csv", "A: Newtonian World (Pure Ballistics)"),
        ("../result_B_sand_gpu.csv", "B: Thermodynamic Dispersion (Pure Turbulence)"),
        ("../result_C_comb_gpu.csv", "C: Rigid Interference (Mathematical Wave)"),
        ("../result_D_feynman_gpu.csv", "D: Fluid Reality (Full Feynman Pattern)")
    ]

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle('3D Hydrodynamic Engine - The 4 Quadrants (True Scale at 2000px)', 
                 fontsize=18, fontweight='bold', color='white')
    axes = axes.flatten()

    weight_green = 1.0
    weight_red = 0.35
    weight_uv = 0.10

    # ==============================================================
    # Parâmetros Físicos extraídos do main.rs e fenda_shader.wgsl
    # ==============================================================
    slit_width = 5.0         # (a) Largura de cada fenda
    slits_distance = 120.0   # (d) Distância entre os centros das fendas
    screen_dist = 600.0      # (L) Distância de voo (SCREEN_Y 800 - SLITS_Y 200)
    wave_len = 10.0          # (λ) Comprimento de onda do fóton verde (channel 1)

    for i, (file_path, title) in enumerate(quadrants):
        ax = axes[i]
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            x = df['X']
            green_visual = df['Green'] * weight_green

            # Plotagem dos dados da GPU (A mecânica dos fluidos gerando o padrão)
            ax.fill_between(x, df['UV']*weight_uv, color='purple', alpha=0.3)
            ax.fill_between(x, df['Red']*weight_red, color='red', alpha=0.3)
            ax.fill_between(x, green_visual, color='green', alpha=0.35)
            ax.plot(x, green_visual, color='#00ff00', alpha=0.9, linewidth=2.0, label='Green (100%)')
            
            # --- CURVA TEÓRICA COMPLETA DE FRAUNHOFER (Quadrante D) ---
            if i == 3:
                # 1. Distância a partir do centro do sistema (X = 1000)
                delta_x = x - 1000.0
                
                # 2. Cálculo do Seno(theta) real via geometria de triângulo
                sin_theta = delta_x / np.sqrt(delta_x**2 + screen_dist**2)
                
                # 3. O Envelope de Difração (A restrição criada pela largura da fenda 'a')
                # Atenção: np.sinc(y) no numpy já executa sin(pi*y)/(pi*y), por isso o pi foi omitido da conta
                difracao_envelope = np.sinc((slit_width * sin_theta) / wave_len)**2
                
                # 4. As Franjas de Interferência (A sobreposição entre as fendas 'd')
                # O numpy.cos é o cosseno normal, então precisamos incluir o pi explicitamente
                fase_interferencia = (np.pi * slits_distance * sin_theta) / wave_len
                interferencia_franjas = np.cos(fase_interferencia)**2
                
                # 5. Combinar as ondas (Intensidade Total = Envelope * Interferência)
                intensidade_teorica = difracao_envelope * interferencia_franjas
                
                # Escalar para a altura real atingida pelos fótons no seu modelo de fluidos
                intensidade_escalada = intensidade_teorica * green_visual.max()
                
                ax.plot(x, intensidade_escalada, color='#ffcc00', 
                        linestyle='--', linewidth=2, label=r'Fraunhofer ($\cos^2 \cdot \text{sinc}^2$)')
            
            ax.set_title(title, fontsize=13, fontweight='bold', color='white')
            ax.set_xlim(0, 2000) 
            ax.set_ylabel('Relative Luminous Intensity', color='gray')
            ax.set_xlabel('Screen Coordinate X (px)', color='gray')
            ax.grid(True, linestyle='--', alpha=0.2)
            
            if i == 3: 
                ax.legend(loc='upper right', facecolor='#121212', edgecolor='gray', labelcolor='white')
        else:
            ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.", 
                    ha='center', va='center', transform=ax.transAxes, color='#ff4444')

    plt.style.use('dark_background')
    fig.patch.set_facecolor('#121212')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    
    output_filename = '../hqpu_quadrantes_fotometricos.png'
    plt.savefig(output_filename, dpi=300)
    print(f"Success! Chart saved to: {output_filename}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_quadrants_visual_calibrated()