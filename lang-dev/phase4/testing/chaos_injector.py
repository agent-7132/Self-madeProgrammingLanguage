import random
import subprocess
import time

FAILURE_TYPES = {
    'network': lambda: subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", "50051", "-j", "DROP"]),
    'process': lambda: subprocess.run(["pkill", "-9", "qpu_scheduler"]),
    'memory': lambda: subprocess.run(["stress-ng", "--vm", "2", "--vm-bytes", "2G", "-t", "60s"])
}

def inject_failure(duration=3600, interval=60):
    start_time = time.time()
    while time.time() - start_time < duration:
        failure = random.choice(list(FAILURE_TYPES.keys()))
        FAILURE_TYPES[failure]()
        time.sleep(interval)
