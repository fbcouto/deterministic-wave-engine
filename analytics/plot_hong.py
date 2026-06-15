import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

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

# Load simulation data
df = pd.read_csv('output.csv')

# Initialize a 2x2 grid figure
fig, axs = plt.subplots(2, 2, figsize=(16, 16))
fig.suptitle('Topological Scattering Matrix - The 4 Possibilities', fontsize=22)

# Scenario titles corresponding to standard quantum optics outcomes
titles = {
    1: "1. Bunching State\nHOM Effect - Bottom-Left Output",
    2: "2. Bunching State\nHOM Effect - Top-Right Output",
    3: "3. Independent Transmission\nClassical HOM Breaking (Photon 2 Delay)",
    4: "4. Independent Reflection\nClassical HOM Breaking (Photon 1 Delay)"
}

colors = {0: 'blue', 1: 'orange'}

# Flatten axis array for iteration
axs = axs.flatten()

for i in range(4):
    ax = axs[i]
    scenario_id = i + 1
    
    # Filter data for the current scenario
    scenario_data = df[df['scenario'] == scenario_id]
    
    # Plot the 50/50 Beam Splitter diagonal
    ax.plot([440, 580], [440, 580], linestyle='--', color='black', alpha=0.5, label='Beam Splitter')
    
    for vortex_id, group in scenario_data.groupby('id'):
        
        # Dynamic origin detection based on initial spatial coordinates
        start_x = group['pos_x'].iloc[0]
        start_y = group['pos_y'].iloc[0]
        
        pos_x_str = "Right" if start_x > 500 else "Left"
        pos_y_str = "Top" if start_y > 500 else "Bottom"
        
        dynamic_label = f"Photon {vortex_id + 1} (Origin: {pos_x_str}/{pos_y_str})"

        # Plot continuous trajectory
        ax.plot(group['pos_x'], group['pos_y'], color=colors[vortex_id], linewidth=2.5, label=dynamic_label)
        
        # Mark the final coordinate state
        final_x = group['pos_x'].iloc[-1]
        final_y = group['pos_y'].iloc[-1]
        ax.scatter(final_x, final_y, color=colors[vortex_id], s=120, marker='X', zorder=5)

        # Plot the final velocity vector
        final_vel_x = group['vel_x'].iloc[-1]
        final_vel_y = group['vel_y'].iloc[-1]
        ax.quiver(final_x, final_y, final_vel_x, final_vel_y, color='red', scale=15, zorder=6)
    
    # Subplot formatting
    ax.set_title(titles[scenario_id], fontsize=14)
    ax.set_xlabel('Position X', fontsize=12)
    ax.set_ylabel('Position Y', fontsize=12)
    ax.grid(True)
    ax.legend(loc='best') 
    ax.axis('equal') 

# Adjust layout and export
plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig('matrix_4_possibilities.png', dpi=300, bbox_inches='tight')
print("Visualization generated successfully: matrix_4_possibilities.png")