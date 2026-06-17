import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_epr_matrix():
    print("Carregando dados...")
    try:
        # Carrega os dados gerados pelo simulador (DWE ou Qiskit)
        df = pd.read_csv('epr_sweep_results.csv')
    except FileNotFoundError:
        print("Erro: Arquivo CSV não encontrado. Rode o simulador primeiro.")
        return

    # Pivotar os dados para criar a matriz
    pivot_df = df.pivot(index='Alice_Angle', columns='Bob_Angle', values='Correlation')

    # ==========================================
    # CÁLCULO DINÂMICO DO VALOR CHSH (S)
    # Extraindo os 4 ângulos clássicos do teste
    # ==========================================
    try:
        e_0_22 = pivot_df.loc[0.0, 22.5]
        e_0_67 = pivot_df.loc[0.0, 67.5]
        e_45_22 = pivot_df.loc[45.0, 22.5]
        e_45_67 = pivot_df.loc[45.0, 67.5]
        
        s_value = abs(e_0_22 - e_0_67 + e_45_22 + e_45_67)
        chsh_title_text = f"Valor CHSH (S) Atingido: {s_value:.4f}"
    except KeyError:
        chsh_title_text = "Ângulos exatos para CHSH não encontrados na matriz."
        s_value = None

    print(f">> {chsh_title_text}")

    # Configuração de estilo do gráfico
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        plt.style.use('default')
        
    fig, ax = plt.subplots(figsize=(14, 11))

    # Criar Heatmap
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
        linecolor='#f0f0f0',
        annot_kws={'size': 9, 'weight': 'bold'}
    )

    # Inverter o eixo Y para 0 graus começar no canto inferior esquerdo
    ax.invert_yaxis()

    # Atualização do Título para exibir o valor S real calculado
    plt.title(f'EPR/CHSH Spectral Matrix\n{chsh_title_text}', 
              fontsize=16, fontweight='bold', pad=15)
              
    plt.xlabel('Bob Angle $\\beta$ (Degrees)', fontsize=12, fontweight='bold')
    plt.ylabel('Alice Angle $\\alpha$ (Degrees)', fontsize=12, fontweight='bold')
    plt.tight_layout()

    # Salvar a imagem
    save_path = 'analytics/epr_spectral_plot.png' if os.path.exists('analytics') else 'epr_spectral_plot.png'
    plt.savefig(save_path, dpi=300)
    print(f"Sucesso! Gráfico salvo em '{save_path}'")

if __name__ == "__main__":
    plot_epr_matrix()