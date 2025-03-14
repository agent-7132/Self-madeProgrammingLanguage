from qiskit import QuantumCircuit, execute
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import hashlib
import numpy as np
from qiskit.circuit.library import QuantumFourierTransform, CRYGate

class QuantumValidator:
    def __init__(self, backend=AerSimulator(method='matrix_product_state')):
        self.backend = backend
        self.shots = 100000

    def validate_shor_21(self):
        qc = QuantumCircuit(9, 4)
        # 21层Shor算法实现
        for _ in range(21):
            qc.h(range(4))
            qc.append(self._modular_exponentiation(15), [0,1,2,3,4,5,6,7,8])
            qc.append(self._quantum_fourier_transform(4), [0,1,2,3])
        
        # 量子哈希校验
        qasm_str = qc.qasm()
        qc_hash = hashlib.sha3_256(qasm_str.encode()).hexdigest()
        
        result = execute(qc, self.backend, shots=self.shots).result()
        counts = result.get_counts(qc)
        
        return {
            "hash": qc_hash,
            "counts": counts,
            "fidelity": result.results[0].metadata.get('state_fidelity', 0.0)
        }

    def _modular_exponentiation(self, N):
        cc = QuantumCircuit(9, name="ModExp")
        for exponent in range(4):
            for q in range(4):
                cc.append(CRYGate(2**exponent * np.pi/N), [q, 4+exponent])
            cc.append(QuantumFourierTransform(4, do_swaps=False), [4,5,6,7])
            for i in reversed(range(4)):
                for j in reversed(range(i)):
                    cc.cp(-np.pi/(2**(i-j)), j, i)
            cc.append(QuantumFourierTransform(4, inverse=True, do_swaps=False), [4,5,6,7])
        return cc.to_instruction()

    def _quantum_fourier_transform(self, n):
        qft = QuantumCircuit(n, name="QFT")
        for j in range(n):
            for k in range(j):
                qft.cp(np.pi/(2**(j-k)), k, j)
            qft.h(j)
        return qft.to_instruction()
