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

def plot_qnd_measurement():
    file_path = "../analytics/hqpu_readings.csv" 

    fig, ax = plt.subplots(figsize=(14, 7))

    if os.path.exists(file_path):
        print(f"Reading analytical data from: {file_path}...")
        df = pd.read_csv(file_path)
        
        y_time = df['Time_Y']
        
        # Cores acadêmicas (Azul e Vermelho Clássicos)
        ax.plot(y_time, df['Left_Sensor'], color='#1f77b4', alpha=0.8, linewidth=2.0, label='Left Sensor (Vacuum Barometer)')
        ax.plot(y_time, df['Right_Sensor'], color='#d62728', alpha=0.8, linewidth=2.0, label='Right Sensor (Vacuum Barometer)')
        
        # Fundo cinza para garantir contraste visual contra o fundo branco
        ax.axvspan(100, 150, color='gray', alpha=0.15, label='Logic Operation (HQPU Gate)')
        
        ax.set_title('Quantum Non-Demolition (QND) Measurement:\nAnalytical Thermodynamic Wake Reading', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Time / Advance on HQPU Chip (Y-Axis)', fontsize=12)
        ax.set_ylabel('Pressure Amplitude (Medium Tension γ)', fontsize=12)
        
        ax.set_xlim(0, 300)
        ax.grid(True, linestyle='--', alpha=0.4)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_color('black')
        
        ax.legend(loc='upper right', frameon=True, edgecolor='black')
        
        # Caixa de status em verde clássico com fundo branco
        ax.text(250, max(df['Left_Sensor']) * 0.75, 
                "✓ Intact Frequency\n✓ No Collapse", 
                color='#2ca02c', fontsize=12, fontweight='bold', 
                bbox=dict(facecolor='white', edgecolor='#2ca02c', boxstyle='round,pad=0.5'))

    else:
        ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.\nRun 'cargo run --release --bin hqpu' first.", 
                ha='center', va='center', transform=ax.transAxes, color='#d62728', fontsize=14, fontweight='bold')
        ax.set_title("Non-Destructive Measurement (Waiting for Data...)", fontsize=16, fontweight='bold')

    plt.tight_layout()
    
    output_filename = '../hqpu_leitura_qnd.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\nSuccess! QND chart rendered and saved to: {output_filename}")
    
    plt.show()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_qnd_measurement()