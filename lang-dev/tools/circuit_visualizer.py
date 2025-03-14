import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.visualization import plot_gate_map

class CircuitVisualizer:
    @staticmethod
    def plot_topology(backend):
        return plot_gate_map(backend)
    
    @staticmethod
    def plot_circuit_timeline(qc: QuantumCircuit):
        qc.draw(output='mpl', style='clifford').show()
    
    @staticmethod
    def plot_error_rates(backend):
        errors = []
        for gate in backend.properties().gates:
            errors.append(gate.parameters[0].value)
        plt.bar(range(len(errors)), errors)
        plt.title('Gate Error Rates')
        plt.show()
