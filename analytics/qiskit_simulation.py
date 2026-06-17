import numpy as np
import pandas as pd
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def run_local_simulator():
    print("Iniciando varredura local EPR via Qiskit AerSimulator (10.000 shots)...")
    
    step_degrees = 7.5
    max_degrees = 90.0
    angles = np.arange(0, max_degrees + step_degrees, step_degrees)
    num_shots = 1000000 
    
    simulator = AerSimulator()
    
    circuits_list = []
    metadata_list = [] # Para lembrarmos qual circuito pertence a quais ângulos

    # 1. CONSTRUÇÃO DO LOTE DE CIRCUITOS
    for a_deg in angles:
        for b_deg in angles:
            theta_a = np.radians(a_deg)
            theta_b = np.radians(b_deg)
            
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            qc.ry(-2 * theta_a, 0)
            qc.ry(-2 * theta_b, 1)
            qc.measure([0, 1], [0, 1])
            
            circuits_list.append(qc)
            metadata_list.append((a_deg, b_deg))

    # 2. EXECUÇÃO EM LOTE (Transpila e roda os 169 circuitos de uma vez)
    compiled_circuits = transpile(circuits_list, simulator)
    job = simulator.run(compiled_circuits, shots=num_shots)
    result = job.result()
    
    # 3. EXTRAÇÃO DE DADOS
    results_data = []
    for idx, (a_deg, b_deg) in enumerate(metadata_list):
        counts = result.get_counts(idx)
        
        n_00 = counts.get('00', 0)
        n_11 = counts.get('11', 0)
        n_01 = counts.get('01', 0)
        n_10 = counts.get('10', 0)
        
        evaluated_total = n_00 + n_11 + n_01 + n_10
        correlation = ((n_00 + n_11) - (n_01 + n_10)) / evaluated_total if evaluated_total > 0 else 0
        
        results_data.append({
            'Alice_Angle': a_deg,
            'Bob_Angle': b_deg,
            'Correlation': correlation,
            'Survivors': evaluated_total,
            'Absorbed': 0
        })
        
        print(f"A:{a_deg:>5.1f}° | B:{b_deg:>5.1f}° | Corr: {correlation:>7.4f}")

    # Exportação
    df = pd.DataFrame(results_data)
    df.to_csv('qiskit_local_epr_results.csv', index=False)
    print("\nConcluído. Dados salvos em 'qiskit_local_epr_results.csv'.")

if __name__ == "__main__":
    run_local_simulator()