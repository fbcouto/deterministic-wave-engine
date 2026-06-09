import pandas as pd
import matplotlib.pyplot as plt
import os

# Estilo Acadêmico / Publication-Style
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

def plot_packet_dispersion():
    file_path = "../analytics/result_airy_vs_gauss.csv"
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Experiment 2: Scattering Cone - Gaussian vs Airy Packets in Fluid Vacuum', 
                 fontsize=16, fontweight='bold')

    if os.path.exists(file_path):
        print(f"Lendo dados de {file_path}...")
        df = pd.read_csv(file_path)
        t = df['Time']
        
        # --- Plot 1: Standard Gaussian Packet ---
        ax1.plot(t, df['Gauss_Center'], color='black', linestyle='--', label='Center of Mass')
        ax1.fill_between(t, df['Gauss_Center'] - df['Gauss_Spread'], 
                         df['Gauss_Center'] + df['Gauss_Spread'], 
                         color='#d62728', alpha=0.2, label='Wave Spread (Decomposition)')
        
        ax1.set_title('Gaussian Packet (Standard Dispersion)', fontweight='bold')
        ax1.set_xlabel('Time / Distance of Propagation')
        ax1.set_ylabel('Transverse Position X')
        ax1.grid(True, linestyle='--', alpha=0.4)
        ax1.legend(loc='upper left', frameon=True, edgecolor='black')

        # --- Plot 2: Airy Packet ---
        ax2.plot(t, df['Airy_Center'], color='black', linestyle='-', label='Trajectory (Self-Accelerating)')
        ax2.fill_between(t, df['Airy_Center'] - df['Airy_Spread'], 
                         df['Airy_Center'] + df['Airy_Spread'], 
                         color='#1f77b4', alpha=0.2, label='Intact Structure (Magnus Protection)')
        
        ax2.set_title('Airy Packet (Non-Dispersive / Self-Healing)', fontweight='bold')
        ax2.set_xlabel('Time / Distance of Propagation')
        ax2.grid(True, linestyle='--', alpha=0.4)
        ax2.legend(loc='upper left', frameon=True, edgecolor='black')
        
        # Salvando a imagem na mesma pasta de onde o script está sendo rodado
        output_file = 'airy_packet_dispersion.png'
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo com sucesso: {output_file}")
        
    else:
        for ax in (ax1, ax2):
            ax.text(0.5, 0.5, f"File {file_path} not found.", 
                    ha='center', va='center', color='red', fontsize=12)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

if __name__ == "__main__":
    plot_packet_dispersion()