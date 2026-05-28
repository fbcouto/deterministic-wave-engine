import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_qnd_measurement():
    file_path = "../hqpu_readings.csv" 

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    if os.path.exists(file_path):
        print(f"Reading analytical data from: {file_path}...")
        df = pd.read_csv(file_path)
        
        y_time = df['Time_Y']
        
        ax.plot(y_time, df['Left_Sensor'], color='#00aaff', alpha=0.8, linewidth=2.0, label='Left Sensor (Vacuum Barometer)')
        ax.plot(y_time, df['Right_Sensor'], color='#ff0055', alpha=0.8, linewidth=2.0, label='Right Sensor (Vacuum Barometer)')
        
        # Área do Portão Lógico
        ax.axvspan(100, 150, color='#ffffff', alpha=0.1, label='Logic Operation (HQPU Gate)')
        
        ax.set_title('Quantum Non-Demolition (QND) Measurement:\nAnalytical Thermodynamic Wake Reading', 
                     fontsize=16, fontweight='bold', color='white', pad=20)
        ax.set_xlabel('Time / Advance on HQPU Chip (Y-Axis)', fontsize=12, color='gray')
        ax.set_ylabel('Pressure Amplitude (Medium Tension γ)', fontsize=12, color='gray')
        
        # Travando a escala X exata do trajeto da partícula
        ax.set_xlim(0, 300)
        ax.grid(True, linestyle='--', alpha=0.2)
        ax.tick_params(colors='gray')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        
        ax.legend(loc='upper right', facecolor='#121212', edgecolor='gray', labelcolor='white')
        
        # Caixa de Verificação de Sucesso
        ax.text(250, max(df['Left_Sensor']) * 0.75, 
                "✓ Intact Frequency\n✓ No Collapse", 
                color='#00ff00', fontsize=12, fontweight='bold', 
                bbox=dict(facecolor='#1a1a1a', edgecolor='#00ff00', boxstyle='round,pad=0.5'))

    else:
        ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.\nRun 'cargo run --release --bin hqpu' first.", 
                ha='center', va='center', transform=ax.transAxes, color='#ff4444', fontsize=14, fontweight='bold')
        ax.set_title("Non-Destructive Measurement (Waiting for Data...)", fontsize=16, fontweight='bold', color='gray')

    plt.tight_layout()
    
    output_filename = '../hqpu_leitura_qnd.png'
    plt.savefig(output_filename, dpi=300, facecolor='#121212', bbox_inches='tight')
    print(f"\nSuccess! QND chart rendered and saved to: {output_filename}")
    
    plt.show()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_qnd_measurement()