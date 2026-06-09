import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

def run_empirical_validation_plots():
    print("Iniciando carregamento dos dados reais (Gaia DR3)...")
    
    file_ven = "venus_dr3_anomalies.csv"
    file_jup = "jupiter_dr3_anomalies.csv"
    
    if not os.path.exists(file_ven) or not os.path.exists(file_jup):
        print("Erro: Arquivos CSV não encontrados. Verifique se os nomes estão corretos e se estão na mesma pasta de execução.")
        return

    df_venus = pd.read_csv(file_ven)
    df_jupiter = pd.read_csv(file_jup)

    col_name = 'dgm_sector'

    ven_prog = df_venus[df_venus[col_name].str.lower() == 'prograde']['astrometric_excess_noise'].dropna().values
    ven_retro = df_venus[df_venus[col_name].str.lower() == 'retrograde']['astrometric_excess_noise'].dropna().values

    jup_prog = df_jupiter[df_jupiter[col_name].str.lower() == 'prograde']['astrometric_excess_noise'].dropna().values
    jup_retro = df_jupiter[df_jupiter[col_name].str.lower() == 'retrograde']['astrometric_excess_noise'].dropna().values

    # Teste de Bootstrapping
    def bootstrap_diff(data_prog, data_retro, n_iterations=10000):
        diffs = [] 
        for _ in range(n_iterations):
            sample_p = np.random.choice(data_prog, size=len(data_prog), replace=True)
            sample_r = np.random.choice(data_retro, size=len(data_retro), replace=True)
            diffs.append(np.mean(sample_p) - np.mean(sample_r))
        diffs = np.array(diffs)
        mean_diff = np.mean(diffs)
        std_diff = np.std(diffs)
        sigma = mean_diff / std_diff if std_diff > 0 else 0
        return mean_diff, std_diff, sigma

    ven_diff, ven_std, ven_sigma = bootstrap_diff(ven_prog, ven_retro)
    jup_diff, jup_std, jup_sigma = bootstrap_diff(jup_prog, jup_retro)

    # PLOT 1: Estimativa de Densidade de Kernel (KDE) - Padrão Acadêmico
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax in axes:
        ax.grid(True, linestyle='--', alpha=0.4)

    # Painel Vênus
    sns.kdeplot(ven_prog, ax=axes[0], color='#d62728', fill=True, alpha=0.4, label='Prograde Sector', linewidth=2)
    sns.kdeplot(ven_retro, ax=axes[0], color='#1f77b4', fill=True, alpha=0.4, label='Retrograde Sector', linewidth=2)
    axes[0].set_title(f'Venus (Retrograde Atmosphere)\n Empirical Shift: {ven_diff:.2f} mas | {abs(ven_sigma):.1f}$\\sigma$ Confidence', fontweight='bold')
    axes[0].set_xlabel('Astrometric Excess Noise (mas)')
    axes[0].set_ylabel('Probability Density')
    axes[0].legend(frameon=True, edgecolor='black')

    # Painel Júpiter
    sns.kdeplot(jup_prog, ax=axes[1], color='#d62728', fill=True, alpha=0.4, label='Prograde Sector', linewidth=2)
    sns.kdeplot(jup_retro, ax=axes[1], color='#1f77b4', fill=True, alpha=0.4, label='Retrograde Sector', linewidth=2)
    axes[1].set_title(f'Jupiter (Standard Prograde)\nEmpirical Shift: {jup_diff:.2f} mas | {abs(jup_sigma):.1f}$\\sigma$ Confidence', fontweight='bold')
    axes[1].set_xlabel('Astrometric Excess Noise (mas)')
    axes[1].set_ylabel('Probability Density')
    axes[1].legend(frameon=True, edgecolor='black')

    plt.tight_layout()
    plt.savefig('dgm_experiment3_kde.png', dpi=300, bbox_inches='tight')
    plt.close()

    # PLOT 2: Topologia 3D do Arraste de Vácuo - Padrão Acadêmico
    y, x = np.mgrid[-2:2:100j, -2:2:100j]
    r = np.sqrt(x**2 + y**2)

    u = y / (r**2 + 0.1) * np.where(r>=1, 1/r, 0)
    v = -x / (r**2 + 0.1) * np.where(r>=1, 1/r, 0)
    drag_magnitude = np.sqrt(u**2 + v**2)

    fig, ax = plt.subplots(figsize=(10, 8))

    contour = ax.contourf(x, y, drag_magnitude, levels=20, cmap='magma', alpha=0.85)

    # Streamlines ajustadas para contraste com o fundo claro/magma
    stream = ax.streamplot(x, y, u, v, color='black', linewidth=1.2, density=1.2, arrowsize=1.5)
    stream.lines.set_alpha(0.5)

    # Planeta central ajustado para fundo claro
    circle = plt.Circle((0, 0), 1.0, color='white', zorder=10)
    circle_edge = plt.Circle((0, 0), 1.0, color='black', fill=False, lw=2, zorder=11)
    ax.add_patch(circle)
    ax.add_patch(circle_edge)
    ax.text(0, 0, 'Venus\n(Retrograde Vortex)', color='black', ha='center', va='center', zorder=12, fontweight='bold')

    ax.set_title('Experiment 3: Viscoelastic Vacuum Drag Topology', pad=20, fontsize=16, fontweight='bold')
    ax.set_xlabel('Spatial Coordinate X (Relative to Barycenter)')
    ax.set_ylabel('Spatial Coordinate Y (Relative to Barycenter)')
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)

    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Spatial Tension Gradient $\\nabla P$ (Drag Magnitude)')

    plt.tight_layout()
    plt.savefig('dgm_experiment3_topology.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    run_empirical_validation_plots()