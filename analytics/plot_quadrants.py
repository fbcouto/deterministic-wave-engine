import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Academic/Publication Style
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black'
})

def plot_quadrants_visual_calibrated():
    quadrants = [
        ("../result_A_newton_gpu.csv", "A: Newtonian World (Pure Ballistics)"),
        ("../result_B_sand_gpu.csv", "B: Thermodynamic Dispersion (Pure Turbulence)"),
        ("../result_C_comb_gpu.csv", "C: Rigid Interference (Mathematical Wave)"),
        ("../result_D_feynman_gpu.csv", "D: Fluid Reality (Full Feynman Pattern)")
    ]

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle('3D Hydrodynamic Engine - The 4 Quadrants (Monochromatic Green)', 
                 fontsize=18, fontweight='bold')
    axes = axes.flatten()

    weight_green = 1.0

    # ALINHAMENTO GEOMÉTRICO (Igual ao Rust e WGSL)
    slit_width = 5.0
    slits_distance = 100.0
    screen_dist = 450.0 # Calibração do eixo Z (fator de escala horizontal)
    wave_len = 11.0
    
    screen_center = 1000.0
    screen_width = 2000

    for i, (file_path, title) in enumerate(quadrants):
        ax = axes[i]
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            x = df['X']
            green_visual = df['Green'] * weight_green

            # MODIFICAÇÃO CHAVE 3: Estilização empírica para destacar organicidade da Figura D
            if i == 2: 
                # Figura C: Ênfase na matemática rígida
                ax.fill_between(x, green_visual, color='darkgreen', alpha=0.2)
                ax.plot(x, green_visual, color='#003300', alpha=1.0, linewidth=1.0, label='Rigid Simulated Data')
            elif i == 3: 
                # Figura D: Ênfase no preenchimento contínuo e orgânico
                ax.fill_between(x, green_visual, color='limegreen', alpha=0.6)
                ax.plot(x, green_visual, color='#32cd32', alpha=0.8, linewidth=2.5, label='Organic Fluid Data')
            else:
                # Figuras A e B
                ax.fill_between(x, green_visual, color='green', alpha=0.3)
                ax.plot(x, green_visual, color='#2ca02c', alpha=0.9, linewidth=1.5, label='Simulated Data (Green)')
            
            # --- GAUSSIAN-MODULATED THEORETICAL FRAUNHOFER CURVE ---
            if i == 3:
                delta_x = x - screen_center
                sin_theta = delta_x / np.sqrt(delta_x**2 + screen_dist**2)
                
                # 1. Diffraction Envelope and Interference Fringes
                difracao_envelope = np.sinc((slit_width * sin_theta) / wave_len)**2
                fase_interferencia = (np.pi * slits_distance * sin_theta) / wave_len
                interferencia_franjas = np.cos(fase_interferencia)**2
                
                # 2. Thermal/Ballistic Envelope (Initial Beam Gaussian Profile)
                sigma_gauss = 800.0 
                envelope_termico = np.exp(-(delta_x**2) / (2 * sigma_gauss**2))
                
                # 3. Full Theoretical Equation for a Gaussian Beam
                intensidade_teorica = difracao_envelope * interferencia_franjas * envelope_termico
                intensidade_escalada = intensidade_teorica * green_visual.max()
                
                # Usamos um zorder alto para que a linha teórica sobreponha sem afogar a cor viva
                ax.plot(x, intensidade_escalada, color='gray', 
                        linestyle='--', linewidth=2, zorder=5, label=r'Gaussian-Mod. Fraunhofer')
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            
            ax.set_xlim(0, screen_width) 
            ax.set_ylabel('Relative Luminous Intensity')
            ax.set_xlabel('Screen Coordinate X (px)')
            ax.grid(True, linestyle='--', alpha=0.4)
            
            if i == 3: 
                ax.legend(loc='upper right', frameon=True, edgecolor='black')
        else:
            ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.", 
                    ha='center', va='center', transform=ax.transAxes, color='red')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    output_filename = '../hqpu_quadrantes_fotometricos.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Success! Chart saved to: {output_filename}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_quadrants_visual_calibrated()