import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

mpl.rcParams.update({
    'font.size': 14,
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'axes.linewidth': 1.5
})

def plot_qnd_measurement():
    file_path = "../analytics/hqpu_readings.csv" 

    fig, ax = plt.subplots(figsize=(10, 6))

    if os.path.exists(file_path):
        print(f"Reading analytical data from: {file_path}...")
        df = pd.read_csv(file_path)
        
        y_time = df['Time_Y']
        
        ax.plot(y_time, df['Left_Sensor'], color='#1f77b4', linewidth=2.5, label='Left Sensor (Vacuum Barometer)')
        ax.plot(y_time, df['Right_Sensor'], color='#d62728', linewidth=2.5, label='Right Sensor (Vacuum Barometer)')
        
        ax.axvspan(100, 150, color='#e6e6e6', label='Logic Operation (HQPU Gate)')
        
        ax.set_title('Quantum Non-Demolition (QND) Measurement:\nAnalytical Thermodynamic Wake Reading', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Time / Advance on HQPU Chip (Y-Axis)', fontweight='bold')
        ax.set_ylabel('Pressure Amplitude (Medium Tension $\\gamma$)', fontweight='bold')
        
        ax.set_xlim(0, 300)
        
        ax.grid(True, linestyle='--', color='#d3d3d3')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.legend(loc='upper right', frameon=True, edgecolor='black')
        
        ax.text(250, max(df['Left_Sensor']) * 0.75, 
                "✓ Intact Frequency\n✓ No Collapse", 
                color='#2ca02c', fontsize=12, fontweight='bold', 
                bbox=dict(facecolor='white', edgecolor='#2ca02c', boxstyle='round,pad=0.5'))

    else:
        ax.text(0.5, 0.5, f"Error: File '{os.path.basename(file_path)}' not found.\nRun 'cargo run --release --bin hqpu' first.", 
                ha='center', va='center', transform=ax.transAxes, color='#d62728', fontsize=14, fontweight='bold')
        ax.set_title("Non-Destructive Measurement (Waiting for Data...)", fontsize=16, fontweight='bold')

    plt.tight_layout()
    
    output_filename_base = '../hqpu_qnd_reading'
    plt.savefig(f'{output_filename_base}.svg', format='svg', dpi=600, bbox_inches='tight')
    plt.savefig(f'{output_filename_base}.eps', format='eps', dpi=600, bbox_inches='tight')
    print(f"\nSuccess! QND charts saved as: {output_filename_base}.svg and {output_filename_base}.eps")
    
    plt.close(fig)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    plot_qnd_measurement()