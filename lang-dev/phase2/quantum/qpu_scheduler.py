from qiskit import QuantumCircuit, execute, pulse
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy
import numpy as np

class EnhancedQuantumScheduler:
    def __init__(self, backend_name='ibmq_montreal'):
        self.service = QiskitRuntimeService()
        self.backend = self.service.backend(backend_name)
        self.calibration = self.backend.properties()
        
    def schedule_optimization(self, problem_graph):
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
                duration=160,
                amp=theta/(2*np.pi),
                sigma=40,
                beta=1.5
            ), pulse.DriveChannel(qubit))
        qc.add_calibration('rz', [qubit], rz_schedule)
    
    def _dynamic_error_mitigation(self, qc):
        for inst in qc.data:
            if inst[0].name == 'cx':
                q1, q2 = inst.qubits
                if self.calibration.gate_error('cx', [q1,q2]) > 0.01:
                    self._apply_echo_sequence(qc, q1, q2)
        return qc
    
    def _apply_echo_sequence(self, qc, q1, q2):
        qc.delay(100, q1)
        qc.x(q1)
        qc.delay(100, q1)
        qc.x(q1)
