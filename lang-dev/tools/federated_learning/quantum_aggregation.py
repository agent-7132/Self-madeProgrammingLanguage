from qiskit import QuantumCircuit, execute
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.crypto.bb84 import BB84
from qiskit.crypto.kyber import Kyber
import numpy as np

class QuantumAggregator:
    def __init__(self, backend_name='ibmq_montreal'):
        self.service = QiskitRuntimeService()
        self.backend = self.service.backend(backend_name)
        self.bb84 = BB84()
        self.kyber = Kyber()

    def _apply_hardware_optimization(self, qc):
        optimized = qc.copy()
        cmap = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10]]
        for gate in qc.data:
            if len(gate.qubits) == 2:
                q1, q2 = gate.qubits[0].index, gate.qubits[1].index
                if [q1,q2] not in cmap:
                    path = self._find_shortest_path(q1, q2, cmap)
                    for swap in path:
                        optimized.swap(swap[0], swap[1])
        return optimized

class SecureQuantumAggregator(QuantumAggregator):
    def __init__(self, backend_name='ibmq_montreal'):
        super().__init__(backend_name)
        from cryptography.hazmat.primitives.secret_sharing import ShamirSharedSecret
        self.shamir = ShamirSharedSecret(threshold=3)
        
    def hybrid_aggregate(self, gradients):
        shares = [self.shamir.split(g.numpy()) for g in gradients]
        quantum_encrypted = [self._quantum_encrypt(s) for s in shares]
        noisy_grads = self._add_dp_noise(quantum_encrypted)
        return super().hybrid_aggregate(noisy_grads)
    
    def _quantum_encrypt(self, data):
        alice_bases, bob_bases = self.bb84.generate_bases(256)
        raw_key = self.bb84.reconcile_keys(alice_bases, bob_bases)
        return self.kyber.encrypt(data, raw_key)
    
    def _add_dp_noise(self, grads, epsilon=0.5):
        noise = np.random.laplace(0, 1/epsilon, len(grads))
        return [g + n for g, n in zip(grads, noise)]
