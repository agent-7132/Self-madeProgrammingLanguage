from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from qiskit.quantum_info import entanglement  # 新增纠缠度计算
from perf.hybrid_profiler import HybridProfiler  # 新增性能分析
from memory.memcheck import MEMCHECK_ALLOC

logger = logging.getLogger('HybridScheduler')

class HybridScheduler:
    def __init__(self):
        self.quantum_queue = []
        self.classic_queue = []
        self.executor = ThreadPoolExecutor(max_workers=8)

    def _schedule_quantum(self):
        """量子任务调度（新增纠缠度优先级）"""
        # 根据纠缠度调整优先级
        for task in self.quantum_queue:
            ent = entanglement(task.qubits)
            task.priority = ent * 100  # 纠缠度越高优先级越高
        self.quantum_queue.sort(key=lambda x: x.priority, reverse=True)

    def _execute_tasks(self):
        """执行任务（保持原逻辑不变）"""
        while self.quantum_queue or self.classic_queue:
            if self.quantum_queue:
                task = self.quantum_queue.pop(0)
                self._run_quantum_task(task)
            if self.classic_queue:
                task = self.classic_queue.pop(0)
                self._run_classic_task(task)

    def run(self):
        """启动调度器（新增性能分析）"""
        with HybridProfiler(track_quantum=True):  # 启动混合性能分析
            self._execute_tasks()

    # 以下保持原有方法不变
    def _run_quantum_task(self, task):
        MEMCHECK_ALLOC(task.memory_required)
        sim = AerSimulator()
        transpiled = transpile(task.circuit, sim)
        result = sim.run(transpiled).result()
        task.callback(result)

    def _run_classic_task(self, task):
        future = self.executor.submit(task.function, *task.args)
        future.add_done_callback(task.callback)

class ErrorMonitor:
    """错误监控模块（保持原有实现）"""
    def __init__(self):
        self.error_log = []
