import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib as mpl

mpl.rcParams.update({
    'font.size': 14,
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
})

def plot_epr_matrix():
    print("Loading data...")
    try:
        df = pd.read_csv('epr_sweep_results.csv')
    except FileNotFoundError:
        print("Error: CSV file not found. Run the simulator first.")
        return

    pivot_df = df.pivot(index='Alice_Angle', columns='Bob_Angle', values='Correlation')

    try:
        e_0_22 = pivot_df.loc[0.0, 22.5]
        e_0_67 = pivot_df.loc[0.0, 67.5]
        e_45_22 = pivot_df.loc[45.0, 22.5]
        e_45_67 = pivot_df.loc[45.0, 67.5]
        
        s_value = abs(e_0_22 - e_0_67 + e_45_22 + e_45_67)
        chsh_title_text = f"CHSH Value (S) Achieved: {s_value:.4f}"
    except KeyError:
        chsh_title_text = "Exact angles for CHSH not found in the matrix."
        s_value = None

    print(f">> {chsh_title_text}")

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        pivot_df, 
        annot=True, 
        fmt=".3f",
        cmap="coolwarm", 
        vmin=-1.0, 
        vmax=1.0, 
        square=True,
        cbar_kws={'label': 'Correlation Value $E(\\alpha, \\beta)$'},
        linewidths=1.0,
        linecolor='white',
        annot_kws={'size': 10, 'weight': 'bold'}
    )

    ax.invert_yaxis()

    plt.title(f'EPR/CHSH Spectral Matrix\n{chsh_title_text}', 
              fontsize=16, fontweight='bold', pad=15)
              
    plt.xlabel('Bob Angle $\\beta$ (Degrees)', fontsize=14, fontweight='bold')
    plt.ylabel('Alice Angle $\\alpha$ (Degrees)', fontsize=14, fontweight='bold')
    plt.tight_layout()

    base_path = 'analytics/epr_spectral_plot' if os.path.exists('analytics') else 'epr_spectral_plot'
    
    plt.savefig(f'{base_path}.svg', format='svg', dpi=600, bbox_inches='tight')
    plt.savefig(f'{base_path}.eps', format='eps', dpi=600, bbox_inches='tight')
    
    print(f"Success! Charts saved as '{base_path}.svg' and '{base_path}.eps'")

if __name__ == "__main__":
    plot_epr_matrix()