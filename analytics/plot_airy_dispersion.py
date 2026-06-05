import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_packet_dispersion():
    file_path = "../analytics/result_airy_vs_gauss.csv"
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#121212')
    fig.suptitle('Experiment 2: Scattering Cone - Gaussian vs Airy Packets in Fluid Vacuum', 
                 fontsize=16, fontweight='bold', color='white')

    if os.path.exists(file_path):
        print(f"Lendo dados de {file_path}...")
        df = pd.read_csv(file_path)
        t = df['Time']
        
        # --- Plot 1: Standard Gaussian Packet ---
        ax1.set_facecolor('#121212')
        ax1.plot(t, df['Gauss_Center'], color='white', linestyle='--', label='Center of Mass')
        ax1.fill_between(t, df['Gauss_Center'] - df['Gauss_Spread'], 
                         df['Gauss_Center'] + df['Gauss_Spread'], 
                         color='#ff4444', alpha=0.3, label='Wave Spread (Decomposition)')
        
        ax1.set_title('Gaussian Packet (Standard Dispersion)', color='white')
        ax1.set_xlabel('Time / Distance of Propagation', color='gray')
        ax1.set_ylabel('Transverse Position X', color='gray')
        ax1.grid(True, linestyle=':', alpha=0.2)
        ax1.legend(loc='upper left', facecolor='#1a1a1a')

        # --- Plot 2: Airy Packet ---
        ax2.set_facecolor('#121212')
        ax2.plot(t, df['Airy_Center'], color='white', linestyle='-', label='Trajectory (Self-Accelerating)')
        ax2.fill_between(t, df['Airy_Center'] - df['Airy_Spread'], 
                         df['Airy_Center'] + df['Airy_Spread'], 
                         color='#44ff44', alpha=0.3, label='Intact Structure (Magnus Protection)')
        
        ax2.set_title('Airy Packet (Non-Dispersive / Self-Healing)', color='white')
        ax2.set_xlabel('Time / Distance of Propagation', color='gray')
        ax2.grid(True, linestyle=':', alpha=0.2)
        ax2.legend(loc='upper left', facecolor='#1a1a1a')
        
        # --- AQUI ESTÁ A ALTERAÇÃO ---
        # Salvando a imagem na mesma pasta de onde o script está sendo rodado
        output_file = 'airy_packet_dispersion.png'
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_file, dpi=300)
        print(f"Gráfico salvo com sucesso: {output_file}")
        
    else:
        for ax in (ax1, ax2):
            ax.set_facecolor('#121212')
            ax.text(0.5, 0.5, f"File {file_path} not found.", 
                    ha='center', va='center', color='red', fontsize=12)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

if __name__ == "__main__":
    plot_packet_dispersion()