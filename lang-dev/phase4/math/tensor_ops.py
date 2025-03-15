import numpy as np
from ctypes import cdll, c_int, c_float, POINTER

# 加载OpenBLAS库
openblas = cdll.LoadLibrary("libopenblas.so")

def simd_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """使用OpenBLAS的SGEMM接口"""
    m, n, k = a.shape[0], b.shape[1], a.shape[1]
    result = np.zeros((m, n), dtype=np.float32)
    openblas.sgemm_(c_int(0), c_int(0), c_int(m), c_int(n), c_int(k),
                    c_float(1.0), a.ctypes.data_as(POINTER(c_float)), c_int(m),
                    b.ctypes.data_as(POINTER(c_float)), c_int(k),
                    c_float(0.0), result.ctypes.data_as(POINTER(c_float)), c_int(m))
    return result

def vectorized_relu(x: np.ndarray) -> np.ndarray:
    """SIMD加速的ReLU激活函数"""
    return np.maximum(0, x)
