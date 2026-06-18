import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'font.size': 14,
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'axes.linewidth': 1.5,
    'lines.linewidth': 2.5
})

df = pd.read_csv('output.csv')

titles = {
    1: "1. Bunching State (HOM Effect - Bottom-Left Output)",
    2: "2. Bunching State (HOM Effect - Top-Right Output)",
    3: "3. Independent Transmission (Classical HOM Breaking)",
    4: "4. Independent Reflection (Classical HOM Breaking)"
}

colors = {0: '#0072b2', 1: '#d95f02'}

for i in range(4):
    scenario_id = i + 1
    fig, ax = plt.subplots(figsize=(7, 7))
    
    scenario_data = df[df['scenario'] == scenario_id]
    
    ax.plot([440, 580], [440, 580], linestyle='--', color='#888888', linewidth=2, label='Beam Splitter')
    
    for vortex_id, group in scenario_data.groupby('id'):
        start_x = group['pos_x'].iloc[0]
        start_y = group['pos_y'].iloc[0]
        
        pos_x_str = "Right" if start_x > 500 else "Left"
        pos_y_str = "Top" if start_y > 500 else "Bottom"
        dynamic_label = f"Photon {vortex_id + 1} (Origin: {pos_x_str}/{pos_y_str})"

        ax.plot(group['pos_x'], group['pos_y'], color=colors[vortex_id], label=dynamic_label)
        
        ax.scatter(start_x, start_y, color=colors[vortex_id], s=150, marker='X', zorder=5, edgecolor='black')

        final_x = group['pos_x'].iloc[-1]
        final_y = group['pos_y'].iloc[-1]
        final_vel_x = group['vel_x'].iloc[-1]
        final_vel_y = group['vel_y'].iloc[-1]
        ax.quiver(final_x, final_y, final_vel_x, final_vel_y, color='black', scale=15, zorder=6)
    
    ax.set_title(titles[scenario_id], fontsize=14, pad=15)
    ax.set_xlabel('Position X', fontweight='bold')
    ax.set_ylabel('Position Y', fontweight='bold')
    
    ax.grid(True, linestyle=':', color='#d3d3d3')
    ax.legend(loc='best', frameon=True, edgecolor='black') 
    ax.axis('equal') 

    output_filename_base = f'hom_scattering_scenario_{scenario_id}'
    plt.tight_layout()
    plt.savefig(f'{output_filename_base}.svg', format='svg', dpi=600, bbox_inches='tight')
    plt.savefig(f'{output_filename_base}.eps', format='eps', dpi=600, bbox_inches='tight')
    print(f"Generated: {output_filename_base} (SVG and EPS)")
    plt.close(fig)