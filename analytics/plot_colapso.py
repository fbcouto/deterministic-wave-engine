import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Academic / Publication Style
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

def plot_collapse_comparison():
    # Caminhos corrigidos para a pasta raiz
    file_d = "../result_D_feynman_gpu.csv"
    file_e = "../result_E_colapso.csv"
    
    if not (os.path.exists(file_d) and os.path.exists(file_e)):
        print(f"Error: Missing datasets. Looked for {file_d} and {file_e}.")
        return

    df_d = pd.read_csv(file_d)
    df_e = pd.read_csv(file_e)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Deterministic Decoherence: The Wave-Function Collapse', fontsize=16, fontweight='bold')

    weight_green = 1.0

    # =========================================================
    # Left Panel: Matrix D (Coherent Wave Field / Interference Pattern)
    # =========================================================
    ax1 = axes[0]
    x_d = df_d['X']
    green_d = df_d['Green'] * weight_green
    
    ax1.fill_between(x_d, df_d['UV']*0.1, color='purple', alpha=0.2)
    ax1.fill_between(x_d, df_d['Red']*0.35, color='red', alpha=0.2)
    ax1.fill_between(x_d, green_d, color='green', alpha=0.3)
    ax1.plot(x_d, green_d, color='#2ca02c', alpha=0.9, linewidth=1.5, label='Simulated Data (Green)')

    # --- ALINHAMENTO GEOMÉTRICO (IGUAL AO PLOT_QUADRANTS) ---
    slit_width = 5.0
    slits_distance = 100.0 
    screen_dist = 450.0 # Reduzido de 1800.0 para 450.0 para ficar exatamente igual
    wave_len = 11.0
    
    screen_center = 1000.0

    delta_x = x_d - screen_center
    sin_theta = delta_x / np.sqrt(delta_x**2 + screen_dist**2)
    
    # 1. Diffraction Envelope and Interference Fringes
    difracao_envelope = np.sinc((slit_width * sin_theta) / wave_len)**2
    fase_interferencia = (np.pi * slits_distance * sin_theta) / wave_len
    interferencia_franjas = np.cos(fase_interferencia)**2
    
    # 2. Thermal/Ballistic Envelope calibrado
    sigma_gauss = 800.0
    envelope_termico = np.exp(-(delta_x**2) / (2 * sigma_gauss**2))
    
    # 3. Complete Gaussian-Modulated Fraunhofer Equation
    intensidade_teorica = difracao_envelope * interferencia_franjas * envelope_termico
    intensidade_escalada = intensidade_teorica * green_d.max()

    # Adicionado zorder=5 e cor 'gray' exatamente como no plot_quadrants
    ax1.plot(x_d, intensidade_escalada, color='gray', linestyle='--', linewidth=2, zorder=5, 
             label=r'Gaussian-Mod. Fraunhofer')
    
    ax1.set_title("Matrix D: Fluid Reality (Coherent State)", fontweight='bold')
    ax1.set_xlim(0, 2000)
    ax1.set_ylabel('Relative Luminous Intensity')
    ax1.set_xlabel('Screen Coordinate X (px)')
    ax1.grid(True, linestyle='--', alpha=0.4)
    ax1.legend(loc='upper right', frameon=True, edgecolor='black')

    # =========================================================
    # Right Panel: Matrix E (The Classical Collapse / Decoherence)
    # =========================================================
    ax2 = axes[1]
    x_e = df_e['X']
    green_e = df_e['Green'] * weight_green
    
    ax2.fill_between(x_e, green_e, color='#d62728', alpha=0.3)
    ax2.plot(x_e, green_e, color='#d62728', alpha=0.9, linewidth=1.5, label='Measured Data (Sensor Active)')
    ax2.scatter(x_e[::15], green_e[::15], color='#d62728', s=10, alpha=0.6)

    ax2.set_title("Matrix E: Thermodynamic Collapse (Sensor Active)", fontweight='bold')
    ax2.set_xlim(0, 2000)
    ax2.set_ylabel('Relative Luminous Intensity')
    ax2.set_xlabel('Screen Coordinate X (px)')
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.legend(loc='upper right', frameon=True, edgecolor='black')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_filename = '../hqpu_colapso.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Success! Collapse chart saved to: {output_filename}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_collapse_comparison()