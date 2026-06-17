import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler, Batch

#  qiskit-ibm-runtime login --token "dRNNnSbMrmkRGIE9rJPY1HQM7cJL2mZY2J7MUM76YaAi" --save

def run_real_hardware():
    print("Conectando ao IBM Quantum...")
    
    # IMPORTANTE: Salve seu token na máquina antes executando no terminal:
    # qiskit-ibm-runtime login --token "SEU_TOKEN_AQUI"
    service = QiskitRuntimeService()
    
    # Pega o backend (computador quântico real) com a menor fila de espera
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Hardware selecionado: {backend.name}")

    step_degrees = 22.5  # Modificado de 7.5 para 22.5
    max_degrees = 90.0
    angles = np.arange(0, max_degrees + step_degrees, step_degrees)
    num_shots = 4096     # Modificado de 10000 para 4096
    
    circuits_list = []
    metadata_list = []

    # 1. CONSTRUÇÃO DO LOTE
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

    # 2. TRANSPILAÇÃO PARA O HARDWARE ESPECÍFICO (Mapeamento de Qubits Reais)
    print("Transpilando circuitos para a topologia do hardware...")
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    isa_circuits = pm.run(circuits_list)

    # 3. EXECUÇÃO VIA BATCH (Envia tudo como um único pacote para a fila)
    print("Enviando Job para a fila da IBM. Isso pode demorar...")
    with Batch(backend=backend) as batch:
        sampler = Sampler(mode=batch)
        # Na V2, nós enviamos os circuitos em uma tupla estruturada
        job = sampler.run(isa_circuits, shots=num_shots)
        print(f"ID do Job: {job.job_id()} (Você pode fechar e checar na dashboard da IBM depois)")
        
        result_v2 = job.result()
    
    # 4. EXTRAÇÃO DE DADOS V2
    results_data = []
    for idx, (a_deg, b_deg) in enumerate(metadata_list):
        # A API V2 retorna dados no formato PubResult
        data = result_v2[idx].data
        counts = data.c.get_counts() # 'c' é o nome padrão do registro clássico
        
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
            'Absorbed': 0 # Lembre-se, o limite quântico decai por decoerência aqui, não absorção
        })
        print(f"A:{a_deg:>5.1f}° | B:{b_deg:>5.1f}° | Corr: {correlation:>7.4f}")

    df = pd.DataFrame(results_data)
    df.to_csv(f'qiskit_real_epr_{backend.name}.csv', index=False)
    print(f"\nFinalizado! Dados gravados em 'qiskit_real_epr_{backend.name}.csv'")

if __name__ == "__main__":
    run_real_hardware()