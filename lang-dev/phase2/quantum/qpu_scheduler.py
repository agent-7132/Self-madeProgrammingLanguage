from qiskit import QuantumCircuit, execute, pulse
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy
from qiskit.transpiler import CouplingMap
from .simd_simulator import HardwareAwareScheduler
import numpy as np
import logging
import cpuinfo

logger = logging.getLogger('QuantumScheduler')

class EnhancedQuantumScheduler:
    def __init__(self, backend_name='ibmq_montreal'):
        self.service = QiskitRuntimeService()
        self.simd_capability = cpuinfo.get_cpu_info()['flags']
        self.hardware_scheduler = HardwareAwareScheduler()
        
        try:
            self.backend = self.service.backend(backend_name)
            self.calibration = self.backend.properties()
            logger.info(f"成功连接量子后端：{backend_name}")
        except Exception as e:
            logger.error(f"硬件连接失败，启用模拟器模式: {str(e)}")
            from qiskit.providers.aer import AerSimulator
            self.backend = AerSimulator()
            self.calibration = None
            
    def schedule_optimization(self, problem_graph):
        """核心调度入口"""
        backend_type = self.hardware_scheduler.select_backend(problem_graph.depth)
        
        if backend_type == "SIMD_ACCELERATED":
            return self._optimized_simd_path(problem_graph)
        elif backend_type == "QUANTUM_HARDWARE":
            return self._quantum_hardware_path(problem_graph)
        else:
            return self._fallback_quantum_path(problem_graph)
    
    def _optimized_simd_path(self, problem_graph):
        from .simd_simulator import avx2_state_initialization
        initial_state = avx2_state_initialization(problem_graph.qubits)
        
        circuit = QuantumCircuit(problem_graph.qubits)
        # 构建量子线路
        for i in range(problem_graph.qubits):
            circuit.h(i)
        for edge in problem_graph.adjacency:
            circuit.cx(edge[0], edge[1])
        
        # 执行SIMD加速模拟
        from qiskit.providers.aer import AerSimulator
        simulator = AerSimulator(method='statevector', device='CPU')
        t_circ = transpile(circuit, simulator)
        result = simulator.run(t_circ, shots=1024).result()
        return result.get_counts(circuit)
    
    def _quantum_hardware_path(self, problem_graph):
        """物理量子硬件路径"""
        optimized_circuit = self.apply_hardware_optimization(problem_graph.circuit)
        job = execute(optimized_circuit, self.backend, shots=1024)
        return job.result()
    
    def apply_hardware_optimization(self, circuit):
        """硬件感知优化"""
        coupling_map = CouplingMap(self.backend.configuration().coupling_map)
        return transpile(circuit, 
                       coupling_map=coupling_map,
                       basis_gates=['id', 'rz', 'sx', 'x', 'cx'],
                       optimization_level=3)
    
    def _fallback_quantum_path(self, problem_graph):
        """传统量子路径"""
        circuit = QuantumCircuit(problem_graph.qubits)
        for i in range(problem_graph.qubits):
            circuit.h(i)
        for edge in problem_graph.adjacency:
            circuit.cx(edge[0], edge[1])
        return execute(circuit, self.backend).result()
