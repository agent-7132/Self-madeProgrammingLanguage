from qiskit import QuantumCircuit, execute, transpile
from qiskit_aer import AerSimulator
import hashlib
import numpy as np

class QuantumValidator:
    def __init__(self, backend=AerSimulator(method='matrix_product_state')):
        self.backend = backend
        self.shots = 1000  # 减少shots以适应深度限制
    
    def validate_shor_21(self, N=15):
        results = []
        for stage in range(3):  # 分三个阶段执行
            qc = self._build_stage_circuit(stage, N)
            result = execute(qc, self.backend, shots=self.shots).result()
            results.append(self._analyze_stage(result))
        return self._combine_results(results)
    
    def _build_stage_circuit(self, stage, N):
        qc = QuantumCircuit(9, 4)
        for _ in range(7):  # 每阶段7层
            qc.h(range(4))
            qc.append(self._modular_exponentiation(N), [0,1,2,3,4,5,6,7,8])
            qc.append(self._quantum_fourier_transform(4), [0,1,2,3])
        return transpile(qc, optimization_level=3)
    
    def _analyze_stage(self, result):
        counts = result.get_counts()
        return max(counts, key=counts.get)
    
    def _combine_results(self, results):
        return ''.join(results)
