import numpy as np
from numba import njit, prange
import cpuinfo

@njit(parallel=True, fastmath=True)
def simd_amplitude_estimation(state_vector: np.ndarray, 
                             oracle: np.ndarray,
                             iterations: int):
    """向量化振幅估计算法"""
    for _ in prange(iterations):
        state_vector = np.dot(oracle, state_vector)
        diffuser = 2 * np.outer(state_vector, state_vector) - np.eye(len(state_vector))
        state_vector = np.dot(diffuser, state_vector)
    return np.abs(state_vector)**2

class HardwareAwareScheduler:
    def __init__(self):
        self.cpu_info = cpuinfo.get_cpu_info()
        self.available_backends = ["SIMD_ACCELERATED", "QUANTUM_HARDWARE", "BASIC_SIMULATOR"]
        
    def select_backend(self, circuit_depth: int):
        if circuit_depth > 20 and 'avx512' in self.cpu_info['flags']:
            return "SIMD_ACCELERATED"
        elif 'ibmq' in self.available_backends:
            return "QUANTUM_HARDWARE"
        else:
            return "BASIC_SIMULATOR"

@njit(fastmath=True)
def avx2_state_initialization(qubits: int):
    state = np.zeros(2**qubits, dtype=np.complex128)
    state[0] = 1.0
    for i in prange(qubits):
        state = np.kron(state, np.array([1, 1])/np.sqrt(2))
    return state
