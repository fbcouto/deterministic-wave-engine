import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_bell_test_fluid():
    file_path = "../analytics/result_bell_test.csv"
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    if os.path.exists(file_path):
        print(f"Lendo dados de {file_path}...")
        df = pd.read_csv(file_path)
        
        # Limite Clássico
        ax.plot(df['Angle_Diff'], df['Classical_Limit'], color='gray', linestyle='--', 
                linewidth=2, label='Classical Bound (Markovian/Local)')
        
        # Modelo Fluido
        ax.plot(df['Angle_Diff'], df['Fluid_Correlation'], color='#00ffcc', 
                linewidth=3, label='Fluid Vacuum Model (Non-Markovian Retro-Torque)')
        
        # Destacar a área de violação
        ax.fill_between(df['Angle_Diff'], df['Classical_Limit'], df['Fluid_Correlation'], 
                        where=(df['Fluid_Correlation'] > df['Classical_Limit']), 
                        color='#ff0055', alpha=0.3, label='Bell Violation Area')
        
        ax.fill_between(df['Angle_Diff'], df['Classical_Limit'], df['Fluid_Correlation'], 
                        where=(df['Fluid_Correlation'] < -df['Classical_Limit']), 
                        color='#ff0055', alpha=0.3)

        ax.set_title('Experiment 1: Bell Inequality Violation via Hydrodynamic Retrospective Torque', 
                     fontsize=14, fontweight='bold', color='white', pad=15)
        ax.set_xlabel('Polarizer Angle Difference (Degrees)', color='gray')
        ax.set_ylabel('Correlation Coefficient E(θ)', color='gray')
        
        ax.grid(True, linestyle=':', alpha=0.3)
        ax.legend(facecolor='#1a1a1a', edgecolor='gray')
        
        output_file = 'bell_test_violation.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300) 
        print(f"Gráfico salvo com sucesso: {output_file}")
        
    else:
        ax.text(0.5, 0.5, f"File {file_path} not found.\nRun the Bell Test in Rust first.", 
                ha='center', va='center', color='red', fontsize=12)
        plt.tight_layout()

if __name__ == "__main__":
    plot_bell_test_fluid()