import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

mpl.rcParams.update({
    'font.size': 14,
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman', 'Times New Roman', 'serif'],
    'mathtext.fontset': 'cm',
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'axes.linewidth': 1.5
})

base_file = 'result_A_no_memory.csv'
global_total_photons = 0

if os.path.exists(base_file):
    df_base = pd.read_csv(base_file)
    global_total_photons = int(df_base['Green'].sum())

data_files = [
    ('result_A_no_memory.csv', 'A: Two Lasers (Classical Dispersion / No Memory)', '#d95f02', 'panel_A'),
    ('result_B_pfleegor_mandel.csv', 'B: Fluid Reality (Turbulence + Memory)', '#1b9e77', 'panel_B'),
    ('result_C_magnus_spin.csv', 'C: Quantum Magnus Effect (Memory + Spin + Turbulence)', '#e7298a', 'panel_C'),
    ('result_D_single_laser.csv', 'D: Stern-Gerlach Experiment (ONLY 1 LASER + Spin + Transverse Magnetic Field)', '#0072b2', 'panel_D')
]

for filename, title, color, suffix in data_files:
    fig, ax = plt.subplots(figsize=(8, 5))
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        x = df['X']
        y = df['Green'] 
        
        dynamic_title = f"{title}\nTotal Photons: {global_total_photons:,}"
        
        ax.bar(x, y, color=color, width=1.0)
        
        current_peak = y.max()
        ax.set_ylabel('Raw Photons', fontweight='bold')
        ax.set_xlabel('CCD Sensor Pixel (X-Axis)', fontweight='bold')
        
        ax.grid(True, linestyle='--', color='#d3d3d3')
        
        ax.set_xlim(0, 2000) 
        
        if current_peak > 0:
            ax.set_ylim(0, current_peak * 1.15)
            
        ax.set_title(dynamic_title, fontsize=14, pad=15)
        
        output_filename_base = f'pfleegor_mandel_{suffix}'
        plt.tight_layout()
        plt.savefig(f'{output_filename_base}.svg', format='svg', dpi=600, bbox_inches='tight')
        plt.savefig(f'{output_filename_base}.eps', format='eps', dpi=600, bbox_inches='tight')
        print(f"Generated: {output_filename_base} (SVG and EPS)")
    else:
        print(f"Warning: File {filename} not found.")
        
    plt.close(fig)