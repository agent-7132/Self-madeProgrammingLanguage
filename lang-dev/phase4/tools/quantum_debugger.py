import socket
import struct
from qiskit import QuantumCircuit

class JTAGQVMDebugger:
    def __init__(self, ip="192.168.1.100", port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def capture_statevector(self, circuit: QuantumCircuit):
        # 发送调试命令
        cmd = struct.pack('!B', 0x01)  # 捕获状态命令
        self.sock.sendall(cmd)
        
        # 接收量子态数据
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
    
    def single_step(self):
        cmd = struct.pack('!B', 0x03)
        self.sock.sendall(cmd)
        return self.capture_statevector()
