from qiskit import QuantumCircuit, Aer
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class QuantumKeyExchange:
    def __init__(self, qubits=8):
        self.simulator = Aer.get_backend('aer_simulator')
        self.qubits = qubits
        
    def generate_key(self):
        qc = QuantumCircuit(self.qubits)
        qc.h(range(self.qubits))
        qc.measure_all()
        result = self.simulator.run(qc).result()
        raw_key = ''.join(str(b) for b in result.get_counts().most_frequent())
        return HKDF(
            algorithm=hashes.SHA3_256(),
            length=32,
            salt=None,
            info=b'quantum-key'
        ).derive(raw_key.encode())
