import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

# Academic / Publication Style
mpl.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black'
})

# Creates the FOUR subplots
fig, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True)

base_file = 'result_A_no_memory.csv'
total_photons = 0
if os.path.exists(base_file):
    df_base = pd.read_csv(base_file)
    total_photons = int(df_base['Green'].sum())

# English title and comma as thousand separator
fig.suptitle(
    'DWE V4.0 - Evolution of Classical Wave Mechanics\n'
    'Angled Lasers Converging to the Center (RAW DATA)\n'
    f'Total Photons Detected: {total_photons:,}', 
    fontsize=16, fontweight='bold', y=0.96
)

# Colors adjusted to be readable on a white background
data_files = [
    ('result_A_no_memory.csv', 'A: Two Lasers (Classical Dispersion / No Memory)', '#d95f02'), # Dark Orange
    ('result_B_pfleegor_mandel.csv', 'B: Fluid Reality (Turbulence + Memory)', '#1b9e77'), # Forest Green
    ('result_C_magnus_spin.csv', 'C: Quantum Magnus Effect (Emergent Fraunhofer = Memory + Spin + Turbulence)', '#e7298a'), # Crimson/Pink
    ('result_D_single_laser.csv', 'D: Stern-Gerlach Experiment (ONLY 1 LASER + Spin)', '#0072b2') # Teal/Blue
]

for ax, (filename, title, color) in zip(axes, data_files):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        x = df['X']
        y = df['Green'] 
        
        ax.set_title(title, fontsize=12, pad=10)
        ax.bar(x, y, color=color, width=1.0, alpha=0.9)
        
        current_peak = y.max()
        ax.set_ylabel('Raw Photons')
        ax.grid(True, alpha=0.15, linestyle='--', color='black') # Subtle grid
        ax.set_xlim(0, 2000)
        
        if current_peak > 0:
            ax.set_ylim(0, current_peak * 1.15)
    else:
        ax.text(0.5, 0.5, f'File not found:\n{filename}', 
                horizontalalignment='center', verticalalignment='center', 
                transform=ax.transAxes, color='#ff4444', fontsize=12)

axes[-1].set_xlabel('CCD Sensor Pixel (X-Axis)', fontsize=12)
plt.subplots_adjust(hspace=0.4)

output_filename = 'pfleegor_mandel_raw_data_full.png'
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Plot successfully generated and saved as: {output_filename}")
plt.close()