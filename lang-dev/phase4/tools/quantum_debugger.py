import socket
import struct
import json
import marshal
from qiskit import QuantumCircuit

class JTAGQVMDebugger:
    def __init__(self, ip="192.168.1.100", port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def capture_statevector(self, circuit: QuantumCircuit):
        cmd = struct.pack('!B', 0x01)
        self.sock.sendall(cmd)
        raw_data = self.sock.recv(16 * 1024)
        return self._parse_statevector(raw_data)
    
    def _parse_statevector(self, data):
        state = {}
        for i in range(0, len(data), 12):
            idx, real, imag = struct.unpack('!Iff', data[i:i+12])
            state[idx] = complex(real, imag)
        return state
    
    def set_breakpoint(self, qubit: int, condition: str):
        cmd = struct.pack('!BI', 0x02, qubit) + condition.encode()
        self.sock.sendall(cmd)
    
    def set_conditional_breakpoint(self, qubit: int, condition: callable):
        """支持Lambda条件断点"""
        condition_code = marshal.dumps(condition.__code__)
        cmd = struct.pack('!BII', 0x04, qubit, len(condition_code)) + condition_code
        self.sock.sendall(cmd)
    
    def quantum_watchpoint(self, state_pattern: dict):
        """量子态模式观察点"""
        packed = json.dumps(state_pattern).encode()
        cmd = struct.pack('!BI', 0x05, len(packed)) + packed
        self.sock.sendall(cmd)
    
    def single_step(self):
        cmd = struct.pack('!B', 0x03)
        self.sock.sendall(cmd)
        return self.capture_statevector()
