import csv
import matplotlib.pyplot as plt
import os

csv_file = "hqpu_readings.csv"

if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found. Run the Rust code first.")
    exit()

time_y, left_sensor, right_sensor = [], [], []

with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    next(reader) # Skip the header
    for row in reader:
        time_y.append(float(row[0]))
        left_sensor.append(float(row[1]))
        right_sensor.append(float(row[2]))

plt.style.use('dark_background')
plt.figure(figsize=(10, 5))

# Plotting the sensor readings (The Vacuum Wake)
plt.plot(time_y, left_sensor, color='cyan', alpha=0.8, linewidth=1.5, label='Left Analytical Sensor (x=20)')
plt.plot(time_y, right_sensor, color='magenta', alpha=0.8, linewidth=1.5, label='Right Analytical Sensor (x=80)')

# Highlighting the Logic Gate zone on the graph
plt.axvspan(100, 150, color='white', alpha=0.1, label='Logic Gate (Tension Gradient)')

plt.title('HQPU: Quantum Non-Demolition Measurement (Vacuum Barometer)\nProof of continuous state reading without collapsing the particle', color='yellow', pad=15)
plt.xlabel('Qubit Trajectory Across the Chip (Time / Y-Axis)')
plt.ylabel('Vacuum Pressure Fluctuation (γ)')
plt.legend(loc='upper right')
plt.grid(True, color='#333333', linestyle='--')

output_img = "HQPU_Measurement.png"
plt.savefig(output_img, dpi=300, bbox_inches='tight')
print(f"Graph generated successfully: {output_img}")