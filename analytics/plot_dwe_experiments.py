import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# DWE Visual Style Configuration
plt.style.use('dark_background')
colors = {'prog': '#ff0055', 'retro': '#00ffcc', 'barrier': '#ffcc00', 'text': 'gray'}

def plot_exp3_tunneling():
    file_path = "result_exp3_tunneling.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Particle distribution on the X axis
    sns.histplot(data=df, x='pos_x', bins=40, color=colors['retro'], alpha=0.7, ax=ax, edgecolor='white')
    
    # Draw the Restrictive Dome (Topological Barrier)
    ax.axvspan(50.0, 55.0, color=colors['barrier'], alpha=0.15, label='Energy Wall (Potential Barrier)')
    ax.axvline(50.0, color=colors['barrier'], linestyle='--', linewidth=2)
    ax.axvline(55.0, color=colors['barrier'], linestyle='--', linewidth=2)

    ax.set_title('Exp 3: Stochastic Tunneling (Bouncing Phase)', color='white', fontweight='bold', pad=15)
    ax.set_xlabel('Spatial Coordinate X (Matrix)', color=colors['text'])
    ax.set_ylabel('Vortex Density (Particles)', color=colors['text'])
    ax.legend(facecolor='#1a1a1a', edgecolor='gray')
    
    plt.tight_layout()
    plt.savefig('dwe_exp3_tunneling.png', dpi=300)
    plt.close()
    print("[+] Exp 3 Plot generated: dwe_exp3_tunneling.png")

def plot_exp4_zeeman():
    file_path = "result_exp4_zeeman.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    # Identify Helicity for the Legend
    df['Spin'] = df['helicity'].apply(lambda x: 'Prograde (+1)' if x > 0 else 'Retrograde (-1)')

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Violin Plot to show the Splitting
    sns.violinplot(data=df, x='Spin', y='orbital_energy', hue='Spin', palette=[colors['prog'], colors['retro']], ax=ax, inner="stick", legend=False)

    ax.set_title('Exp 4: Zeeman Degeneracy\n(Coriolis Shear on Energy Levels)', color='white', fontweight='bold', pad=15)
    ax.set_ylabel('Stationary Orbital Energy', color=colors['text'])
    ax.set_xlabel('Topological Vortex Helicity', color=colors['text'])
    
    plt.tight_layout()
    plt.savefig('dwe_exp4_zeeman.png', dpi=300)
    plt.close()
    print("[+] Exp 4 Plot generated: dwe_exp4_zeeman.png")

def plot_exp5_anderson():
    file_path = "result_exp5_anderson.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # 2D Mapping of thermal confinement positions
    ax.scatter(df['pos_x'], df['pos_y'], c='#ffffff', alpha=0.6, s=40, edgecolors='#00ffcc', linewidth=1.5)

    ax.set_title('Exp 5: Anderson Localization\n(Ballistic-Thermodynamic Confinement Matrix)', color='white', fontweight='bold', pad=15)
    ax.set_xlabel('Vectorial Dispersion X', color=colors['text'])
    ax.set_ylabel('Vectorial Dispersion Y', color=colors['text'])
    ax.grid(True, linestyle=':', alpha=0.1)
    
    plt.tight_layout()
    plt.savefig('dwe_exp5_anderson.png', dpi=300)
    plt.close()
    print("[+] Exp 5 Plot generated: dwe_exp5_anderson.png")

if __name__ == "__main__":
    print("Starting analytical rendering of the Engine (DWE)...")
    plot_exp3_tunneling()
    plot_exp4_zeeman()
    plot_exp5_anderson()