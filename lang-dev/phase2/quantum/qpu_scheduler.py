from qiskit import QuantumCircuit, execute, pulse
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy
from qiskit.crypto.kyber import Kyber
from qiskit.crypto.bb84 import BB84
import numpy as np
from numpy.lib import NumpyVersion

class EnhancedQuantumScheduler:
    def __init__(self, backend_name='ibmq_montreal'):
        self.service = QiskitRuntimeService()
        try:
            self.backend = self.service.backend(backend_name)
            self.calibration = self.backend.properties()
        except Exception as e:
            print(f"硬件连接失败，启用模拟器模式: {str(e)}")
            from qiskit.providers.aer import AerSimulator
            self.backend = AerSimulator()
            self.calibration = None
            
    def schedule_optimization(self, problem_graph):
        if hasattr(self.backend.configuration(), 'simd_extension'):
            return self._optimized_simd_path(problem_graph)
        else:
            return self._fallback_quantum_path(problem_graph)
    
    def _optimized_simd_path(self, problem_graph):
        adjacency_matrix = np.array(problem_graph.matrix, dtype=np.float64)
        if NumpyVersion(np.__version__) >= '1.20':
            eigenvalues = np.linalg.eigvalsh(adjacency_matrix, driver='evd')
        else:
            eigenvalues = np.linalg.eigvalsh(adjacency_matrix)
        return eigenvalues.max()

    def _fallback_quantum_path(self, problem_graph):
        qc = QuantumCircuit(len(problem_graph.nodes))
        qc.h(range(qc.num_qubits))
        for (i, j), weight in problem_graph.edges.data('weight'):
            qc.cx(i, j)
            self._apply_calibrated_rz(qc, j, weight * np.pi)
            qc.cx(i, j)
        qc = self._dynamic_error_mitigation(qc)
        qc.measure_all()
        job = execute(qc, least_busy(self.service.backends()), shots=1024)
        return job.result().get_counts()

    def _apply_calibrated_rz(self, qc, qubit, theta):
        with pulse.build(self.backend) as rz_schedule:
            pulse.play(pulse.Drag(
                duration=80,
                amp=theta/(2*np.pi),
                sigma=20,
                beta=1.0
            ), pulse.DriveChannel(qubit))
        qc.add_calibration('rz', [qubit], rz_schedule)
    
    def _dynamic_error_mitigation(self, qc):
        for inst in qc.data:
            if inst[0].name == 'cx':
                q1, q2 = inst.qubits
                if self.calibration and self.calibration.gate_error('cx', [q1,q2]) > 0.01:
                    self._apply_echo_sequence(qc, q1, q2)
            elif inst[0].name in ['rz', 'h', 'x']:
                qubit = inst.qubits[0]
                if self.calibration and self.calibration.gate_error(inst[0].name, qubit) > 0.015:
                    self._apply_dynamical_decoupling(qc, qubit)
        return qc
    
    def _apply_echo_sequence(self, qc, q1, q2):
        qc.delay(50, q1)
        qc.x(q1)
        qc.delay(50, q1)
        qc.x(q1)

    def _apply_dynamical_decoupling(self, qc, qubit):
        qc.delay(20, qubit)
        qc.y(qubit)
        qc.delay(20, qubit)
