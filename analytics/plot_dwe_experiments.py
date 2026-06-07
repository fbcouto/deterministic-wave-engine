import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuração de Estilo Visual do DWE
plt.style.use('dark_background')
colors = {'prog': '#ff0055', 'retro': '#00ffcc', 'barrier': '#ffcc00', 'text': 'gray'}

def plot_exp3_tunneling():
    file_path = "result_exp3_tunneling.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Distribuição das partículas no eixo X
    sns.histplot(data=df, x='pos_x', bins=40, color=colors['retro'], alpha=0.7, ax=ax, edgecolor='white')
    
    # Desenhar o Domo Restritivo (Barreira Topológica)
    ax.axvspan(50.0, 55.0, color=colors['barrier'], alpha=0.15, label='Energy Wall (Barreira de Potencial)')
    ax.axvline(50.0, color=colors['barrier'], linestyle='--', linewidth=2)
    ax.axvline(55.0, color=colors['barrier'], linestyle='--', linewidth=2)

    ax.set_title('Exp 3: Tunelamento Estocástico (Bouncing Phase)', color='white', fontweight='bold', pad=15)
    ax.set_xlabel('Coordenada Espacial X (Matriz)', color=colors['text'])
    ax.set_ylabel('Densidade de Vórtices (Partículas)', color=colors['text'])
    ax.legend(facecolor='#1a1a1a', edgecolor='gray')
    
    plt.tight_layout()
    plt.savefig('dwe_exp3_tunneling.png', dpi=300)
    plt.close()
    print("[+] Gráfico Exp 3 gerado: dwe_exp3_tunneling.png")

def plot_exp4_zeeman():
    file_path = "result_exp4_zeeman.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    # Identificar a Helicidade para a Legenda
    df['Spin'] = df['helicity'].apply(lambda x: 'Prógrado (+1)' if x > 0 else 'Retrógrado (-1)')

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Gráfico de Violino para mostrar a Separação (Splitting)
    sns.violinplot(data=df, x='Spin', y='orbital_energy', hue='Spin', palette=[colors['prog'], colors['retro']], ax=ax, inner="stick", legend=False)

    ax.set_title('Exp 4: Degeneração Zeeman\n(Cisalhamento Coriolis em Níveis de Energia)', color='white', fontweight='bold', pad=15)
    ax.set_ylabel('Energia Orbital Estacionária', color=colors['text'])
    ax.set_xlabel('Helicidade Topológica do Vórtice', color=colors['text'])
    
    plt.tight_layout()
    plt.savefig('dwe_exp4_zeeman.png', dpi=300)
    plt.close()
    print("[+] Gráfico Exp 4 gerado: dwe_exp4_zeeman.png")

def plot_exp5_anderson():
    file_path = "result_exp5_anderson.csv"
    if not os.path.exists(file_path): return
    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Mapeamento 2D das posições de confinamento térmico
    ax.scatter(df['pos_x'], df['pos_y'], c='#ffffff', alpha=0.6, s=40, edgecolors='#00ffcc', linewidth=1.5)

    ax.set_title('Exp 5: Localização de Anderson\n(Matriz de Confinamento Balístico-Termodinâmico)', color='white', fontweight='bold', pad=15)
    ax.set_xlabel('Dispersão Vetorial X', color=colors['text'])
    ax.set_ylabel('Dispersão Vetorial Y', color=colors['text'])
    ax.grid(True, linestyle=':', alpha=0.1)
    
    plt.tight_layout()
    plt.savefig('dwe_exp5_anderson.png', dpi=300)
    plt.close()
    print("[+] Gráfico Exp 5 gerado: dwe_exp5_anderson.png")

if __name__ == "__main__":
    print("Iniciando renderização analítica do Motor (DWE)...")
    plot_exp3_tunneling()
    plot_exp4_zeeman()
    plot_exp5_anderson()
