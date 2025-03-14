from qiskit import QuantumCircuit, execute
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy

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
            qc.rz(weight * 3.1415, j)
            qc.cx(i, j)
        qc = self._dynamic_error_mitigation(qc)
        qc.measure_all()
        job = execute(qc, least_busy(self.service.backends()), shots=1024)
        return job.result().get_counts()
    
    def _dynamic_error_mitigation(self, qc):
        for inst in qc.data:
            if isinstance(inst[0], CXGate):
                q1, q2 = inst.qubits
                if self.calibration.gate_error('cx', [q1,q2]) > 0.01:
                    qc.u3(np.pi/2, 0, np.pi, q1)
                    qc.u2(0, np.pi, q2)
                    qc.cx(q1, q2)
        return qc
