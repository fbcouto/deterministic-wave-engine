import pandas as pd
import matplotlib.pyplot as plt
import os

# Estilo Acadêmico
plt.rcParams.update({'font.size': 12, 'font.family': 'serif', 'axes.facecolor': 'white', 'figure.facecolor': 'white'})

def plot_bell_test():
    file_path = "result_bell_test.csv"
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        return

    df = pd.read_csv(file_path)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Curvas em cores acadêmicas de alto contraste
    ax.plot(df['Angle_Diff'], df['Fluid_Correlation'], color='#1f77b4', label='Fluid Vacuum Correlation (DWE)', linewidth=2.5)
    ax.plot(df['Angle_Diff'], df['Classical_Limit'], color='black', linestyle='--', label='Classical Local Limit (Markovian)', linewidth=2)

    # Linhas de limite de Bell/CHSH
    ax.axhline(y=0.707, color='#d62728', linestyle=':', label='Bell/CHSH Violation Threshold')
    ax.axhline(y=-0.707, color='#d62728', linestyle=':')

    ax.set_title('Exp 1: Bell\'s Inequality Test via Retrospective Fluid Torque', fontsize=14, fontweight='bold')
    ax.set_xlabel('Polarizer Angle Difference (Degrees)')
    ax.set_ylabel('Correlation Coefficient')
    
    ax.set_xlim(0, 360)
    ax.set_ylim(-1.1, 1.1)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='upper right', frameon=True, edgecolor='black')

    output_filename = 'bell_test_violation.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Success! Chart saved to: {output_filename}")

if __name__ == "__main__":
    plot_bell_test()