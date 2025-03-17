import socket
import struct
import json
import pickle
import ssl
import tempfile
import subprocess
import restrictedpython
from typing import Dict, Callable
from qiskit import QuantumCircuit

class SecurityError(Exception):
    pass

class JTAGQVMDebugger:
    def __init__(self, ip: str = "192.168.1.100", port: int = 12345):
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.wrapped_sock = self.context.wrap_socket(self.sock, server_hostname=ip)
        try:
            self.wrapped_sock.connect((ip, port))
        except (socket.timeout, ConnectionRefusedError) as e:
            raise RuntimeError(f"连接失败: {str(e)}")

    def capture_statevector(self, circuit: QuantumCircuit) -> Dict[int, complex]:
        cmd = struct.pack('!B', 0x01)
        self.wrapped_sock.sendall(cmd)
        raw_data = self.wrapped_sock.recv(16 * 1024)
        return self._parse_statevector(raw_data)

    def _parse_statevector(self, data: bytes) -> Dict[int, complex]:
        state = {}
        for i in range(0, len(data), 12):
            idx, real, imag = struct.unpack('!Iff', data[i:i+12])
            state[idx] = complex(real, imag)
        return state

    def _safe_eval(self, condition_code: str) -> Callable:
        loc = {}
        allowed_globals = {'__builtins__': {'None': None, 'complex': complex}}
        try:
            code = restrictedpython.compile_restricted(condition_code)
            exec(code, allowed_globals, loc)
            return loc['condition']
        except restrictedpython.RestrictedError as e:
            raise SecurityError(f"非法代码: {str(e)}")

    def set_conditional_breakpoint(self, qubit: int, condition: str):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(condition)
            tmp.flush()
            result = subprocess.run(
                ["bandit", "-r", tmp.name],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise SecurityError(f"安全检查失败: {result.stdout}")

        condition_func = self._safe_eval(condition)
        code_bytes = pickle.dumps(condition_func.__code__, protocol=4)
        if len(code_bytes) > 4096:
            raise ValueError("条件代码过大")
        
        header = struct.pack('!BII', 0x04, qubit, len(code_bytes))
        self.wrapped_sock.sendall(header + code_bytes)

    def close(self):
        self.wrapped_sock.close()
