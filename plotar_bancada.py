import csv
import matplotlib.pyplot as plt
import os

def generate_plot(csv_name, output_name, title, subtitle, theme_color):
    if not os.path.exists(csv_name):
        print(f" [Warning] {csv_name} not found. Skipping...")
        return

    x_coords, uv, green, red = [], [], [], []
    with open(csv_name, 'r') as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            x_coords.append(int(row[0]))
            uv.append(int(row[1]))
            green.append(int(row[2]))
            red.append(int(row[3]))

    plt.style.use('dark_background')
    plt.figure(figsize=(12, 6))

    # Chromatic Dissipative Spectrum Plotting
    plt.plot(x_coords, red, color='#ff3333', linewidth=1.5, label='Red (Long)')
    plt.fill_between(x_coords, red, color='#ff3333', alpha=0.15)
    
    plt.plot(x_coords, green, color='#33ff33', linewidth=1.5, label='Green (Medium)')
    plt.fill_between(x_coords, green, color='#33ff33', alpha=0.15)
    
    plt.plot(x_coords, uv, color='#cc33ff', linewidth=1.5, label='Ultraviolet (Short)')
    plt.fill_between(x_coords, uv, color='#cc33ff', alpha=0.15)

    plt.xlim(350, 650)
    plt.title(f'{title}\n{subtitle}', pad=20, fontsize=13, color=theme_color)
    plt.xlabel('Screen X Axis (Pixels)', fontsize=11)
    plt.ylabel('Photon Density', fontsize=11)
    plt.grid(True, color='#222222', linestyle='--', alpha=0.5)
    plt.legend(loc='upper right', fontsize=10)

    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f" -> [{output_name}] generated successfully!")
    plt.close()

# ==========================================
# MASS PLOTTING EXECUTION
# ==========================================
print("Processing the 4 Theoretical Quadrants...")

generate_plot("result_A_newton.csv", "A_Newtonian_World.png", 
              "Scenario A: Deflection Mechanism [OFF] | Turbulence [OFF]", 
              "(Classical Ballistics: Perfect Geometric Shadows of the Slits)", "white")

generate_plot("result_B_sand.csv", "B_Sand_Dispersion.png", 
              "Scenario B: Deflection Mechanism [OFF] | Turbulence [ON]", 
              "(Sand Effect / Pure Thermodynamics: Two Gaussian Mounds)", "yellow")

generate_plot("result_C_comb.csv", "C_Rigid_Interference.png", 
              "Scenario C: Deflection Mechanism [ON] | Turbulence [OFF]", 
              "(Pure Deterministic Wave: Rigid Broken Pattern)", "orange")

generate_plot("result_D_feynman.csv", "D_Fluid_Reality.png", 
              "Scenario D: Deflection Mechanism [ON] | Turbulence [ON]", 
              "(The Complete Real Vacuum: Organic and Chromatic Feynman Pattern)", "cyan")

print("\nAll plots have been saved in the current directory!")