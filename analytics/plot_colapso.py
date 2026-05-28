import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_collapse_comparison():
    cenarios = [
        ("../result_D_feynman_gpu.csv", "BEFORE MEASUREMENT \n Coherent Wave Field (Unobserved)"),
        ("../result_E_colapso.csv", "AFTER MEASUREMENT \n Classical Collapse (Right Slit Monitored)")
    ]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('The Observer Effect - Hydrodynamic Phase Decoherence', fontsize=18, fontweight='bold', color='white')

    weight_green = 1.0
    weight_red = 0.35
    weight_uv = 0.10

    for ax, (arquivo, titulo) in zip(axes, cenarios):
        if os.path.exists(arquivo):
            print(f"Plotting collapse metrics from: {arquivo}")
            df = pd.read_csv(arquivo)
            x = df['X']
            uv = df['UV'] * weight_uv
            green = df['Green'] * weight_green
            red = df['Red'] * weight_red

            ax.fill_between(x, uv, color='purple', alpha=0.25)
            ax.plot(x, uv, color='purple', alpha=0.7, linewidth=1.5, label='UV Spectrogram')
            
            ax.fill_between(x, red, color='red', alpha=0.25)
            ax.plot(x, red, color='red', alpha=0.7, linewidth=1.5, label='Red Dispersion')
            
            ax.fill_between(x, green, color='green', alpha=0.35)
            ax.plot(x, green, color='#00cc00', alpha=0.9, linewidth=2.0, label='Green Main Channel')
            
            ax.set_title(titulo, fontsize=14, fontweight='bold', color='white')
            
            # --- A CORREÇÃO DE ZOOM AQUI ---
            # Focando exatamente no centro do anteparo (onde a interferência ocorre)
            ax.set_xlim(600, 1400)
            # -------------------------------
            
            ax.set_xlabel('Screen Coordinate X (px)', color='gray')
            ax.set_ylabel('Relative Luminous Intensity', color='gray')
            ax.grid(True, linestyle='--', alpha=0.15)
            ax.tick_params(colors='gray')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#333333')
            ax.spines['left'].set_color('#333333')
        else:
            ax.text(0.5, 0.5, f"Error: Dataset '{os.path.basename(arquivo)}' is missing.\nRun the Rust simulation first.", 
                    ha='center', va='center', transform=ax.transAxes, color='#ff4444', fontsize=12, fontweight='bold')
            ax.set_facecolor('#1a1a1a')

    plt.style.use('dark_background')
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#121212')

    axes[0].legend(loc='upper right', facecolor='#121212', edgecolor='gray', labelcolor='white')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_filename = '../hqpu_colapso.png'
    plt.savefig(output_filename, dpi=300, facecolor='#121212', bbox_inches='tight')
    print(f"Success! Collapse chart saved to: {output_filename}")
    plt.show()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_collapse_comparison()