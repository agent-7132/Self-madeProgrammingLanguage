import numpy as np
from ctypes import cdll, c_int, c_float, POINTER
import cpuinfo
from numba import njit, prange

# 加载并行计算库
openblas = cdll.LoadLibrary("libopenblas.so")
mpi = cdll.LoadLibrary("libmpi.so")

def detect_simd():
    """检测CPU支持的SIMD指令集"""
    flags = cpuinfo.get_cpu_info()['flags']
    return {
        'avx512': 'avx512f' in flags,
        'avx2': 'avx2' in flags,
        'amx': 'amx' in flags
    }

@njit(fastmath=True, parallel=True)
def avx512_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if a.shape[1] != b.shape[0]:
        raise ValueError("Matrix dimensions mismatch")
    result = np.zeros((a.shape[0], b.shape[1]), dtype=a.dtype)
    for i in prange(a.shape[0]):
        for j in prange(b.shape[1]):
            sum_val = 0.0
            for k in prange(a.shape[1]):
                sum_val += a[i, k] * b[k, j]
            result[i, j] = sum_val
    return result

class TensorSharder:
    def __init__(self):
        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        
    def shard_tensor(self, tensor: np.ndarray, axis=0):
        chunks = np.split(tensor, self.size, axis=axis)
        return chunks[self.rank]
    
    def allgather_tensor(self, local_tensor: np.ndarray, axis=0):
        gathered = self.comm.allgather(local_tensor)
        return np.concatenate(gathered, axis=axis)

    def reduce_gradients(self, grads: np.ndarray, op=None):
        from mpi4py import MPI
        total = np.zeros_like(grads)
        self.comm.Allreduce(grads, total, op=MPI.SUM if op is None else op)
        return total / self.size

@njit(fastmath=True)
def hybrid_precision_matmul(a: np.float32, b: np.float16) -> np.float64:
    return np.dot(a.astype(np.float64), b.astype(np.float64))
