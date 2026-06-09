import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Estilo Acadêmico/Publicação
plt.rcParams.update({'font.size': 12, 'font.family': 'serif', 'axes.facecolor': 'white', 'figure.facecolor': 'white'})
colors = {'prog': '#d62728', 'retro': '#1f77b4', 'barrier': 'gray', 'text': 'black'}

def plot_exp3_tunneling():
    file_path = "result_exp3_tunneling.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.histplot(data=df, x='pos_x', bins=40, color=colors['retro'], alpha=0.7, ax=ax, edgecolor='black')
    
    ax.axvspan(50.0, 55.0, color=colors['barrier'], alpha=0.2, label='Energy Wall (Potential Barrier)')
    ax.axvline(50.0, color='black', linestyle='--', linewidth=1.5)
    ax.axvline(55.0, color='black', linestyle='--', linewidth=1.5)

    ax.set_title('Exp 3: Stochastic Tunneling (Bouncing Phase)', fontweight='bold', pad=15)
    ax.set_xlabel('Spatial Coordinate X (Matrix)', color=colors['text'])
    ax.set_ylabel('Vortex Density (Particles)', color=colors['text'])
    ax.legend(frameon=True, edgecolor='black')
    
    plt.tight_layout()
    plt.savefig('dwe_exp3_tunneling.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_exp4_zeeman():
    file_path = "result_exp4_zeeman.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    df['Spin'] = df['helicity'].apply(lambda x: 'Prograde (+1)' if x > 0 else 'Retrograde (-1)')

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.violinplot(data=df, x='Spin', y='orbital_energy', hue='Spin', palette=[colors['prog'], colors['retro']], ax=ax, inner="stick", legend=False)

    ax.set_title('Exp 4: Zeeman Degeneracy\n(Coriolis Shear on Energy Levels)', fontweight='bold', pad=15)
    ax.set_ylabel('Stationary Orbital Energy', color=colors['text'])
    ax.set_xlabel('Topological Vortex Helicity', color=colors['text'])
    ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('dwe_exp4_zeeman.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_exp5_anderson():
    file_path = "result_exp5_anderson.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(8, 8))

    # Scatter plot com cores acadêmicas
    ax.scatter(df['pos_x'], df['pos_y'], c='#1f77b4', alpha=0.6, s=40, edgecolors='black', linewidth=0.5)

    ax.set_title('Exp 5: Anderson Localization\n(Ballistic-Thermodynamic Confinement Matrix)', fontweight='bold', pad=15)
    ax.set_xlabel('Vectorial Dispersion X', color=colors['text'])
    ax.set_ylabel('Vectorial Dispersion Y', color=colors['text'])
    ax.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.savefig('dwe_exp5_anderson.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_exp3_tunneling()
    plot_exp4_zeeman()
    plot_exp5_anderson()