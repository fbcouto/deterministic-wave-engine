import csv
import matplotlib.pyplot as plt
import os

csv_file = "hqpu_readings.csv"

if not os.path.exists(csv_file):
    print(f"Erro: {csv_file} não encontrado. Rode o código em Rust primeiro.")
    exit()

time_y, left_sensor, right_sensor = [], [], []

with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    next(reader) # Pula o cabeçalho
    for row in reader:
        time_y.append(float(row[0]))
        left_sensor.append(float(row[1]))
        right_sensor.append(float(row[2]))

plt.style.use('dark_background')
plt.figure(figsize=(10, 5))

# Plotando a leitura dos sensores (A Marola do Vácuo)
plt.plot(time_y, left_sensor, color='cyan', alpha=0.8, linewidth=1.5, label='Sensor Analítico Esquerdo (x=20)')
plt.plot(time_y, right_sensor, color='magenta', alpha=0.8, linewidth=1.5, label='Sensor Analítico Direito (x=80)')

# Destacando a zona da Porta Lógica no gráfico
plt.axvspan(100, 150, color='white', alpha=0.1, label='Porta Lógica (Gradiente de Tensão)')

plt.title('HQPU: Medição Quântica Não-Demolidora (Barômetro de Vácuo)\nProva de leitura contínua de estado sem colapsar a partícula', color='yellow', pad=15)
plt.xlabel('Trajetória do Qubit pelo Chip (Tempo/Eixo Y)')
plt.ylabel('Variação de Pressão Lida no Vácuo (γ)')
plt.legend(loc='upper right')
plt.grid(True, color='#333333', linestyle='--')

output_img = "HQPU_Measurement.png"
plt.savefig(output_img, dpi=300, bbox_inches='tight')
print(f"Gráfico gerado com sucesso: {output_img}")