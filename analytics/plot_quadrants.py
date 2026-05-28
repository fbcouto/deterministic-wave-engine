import pandas as pd
import matplotlib.pyplot as plt
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

    for i, (file_path, title) in enumerate(quadrants):
        ax = axes[i]
        
        if os.path.exists(file_path):
            print(f"Processing: {file_path}...")
            df = pd.read_csv(file_path)
            
            x = df['X']
            uv_visual = df['UV'] * weight_uv
            red_visual = df['Red'] * weight_red
            green_visual = df['Green'] * weight_green

            ax.fill_between(x, uv_visual, color='purple', alpha=0.3)
            ax.plot(x, uv_visual, color='purple', alpha=0.8, linewidth=1.5, label='UV (10%)')
            
            ax.fill_between(x, red_visual, color='red', alpha=0.3)
            ax.plot(x, red_visual, color='red', alpha=0.8, linewidth=1.5, label='Red (35%)')

            ax.fill_between(x, green_visual, color='green', alpha=0.35)
            ax.plot(x, green_visual, color='#00ff00', alpha=0.9, linewidth=2.0, label='Green (100%)')
            
            ax.set_title(title, fontsize=13, fontweight='bold', color='white')
            ax.set_xlim(0, 2000) 
            ax.set_ylabel('Relative Luminous Intensity', color='gray')
            ax.set_xlabel('Screen Coordinate X (px)', color='gray')
            ax.grid(True, linestyle='--', alpha=0.2)
            ax.tick_params(colors='gray')
            
            if i == 0:
                ax.legend(loc='upper right', facecolor='#121212', edgecolor='gray', labelcolor='white')
        else:
            ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.\nRun the Rust engine first.", 
                    ha='center', va='center', transform=ax.transAxes, color='#ff4444', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=13, fontweight='bold', color='gray')
            ax.set_facecolor('#1a1a1a')

    plt.style.use('dark_background')
    fig.patch.set_facecolor('#121212')
    
    for ax in axes:
        ax.set_facecolor('#121212')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    
    output_filename = '../hqpu_quadrantes_fotometricos.png'
    plt.savefig(output_filename, dpi=300, facecolor='#121212', bbox_inches='tight')
    print(f"\nSuccess! Chart rendered and saved to: {output_filename}")
    
    plt.show()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_quadrants_visual_calibrated()