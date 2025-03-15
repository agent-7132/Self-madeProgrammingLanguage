from locust import HttpUser, task, between
import random

class QuantumChaosMonkey(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def inject_quantum_error(self):
        error_types = ['bit_flip', 'phase_flip', 'measurement_error']
        self.client.post("/chaos/quantum", json={
            "error_type": random.choice(error_types),
            "duration": f"{random.randint(1,10)}s",
            "qubit_target": random.randint(0, 27)
        })
    
    @task(2)
    def corrupt_classical_memory(self):
        self.client.post("/chaos/classic", json={
            "corruption_type": "random_bit_flip",
            "severity": random.choice([1, 2, 3]),
            "target_process": f"Process-{random.randint(1,8)}"
        })
    
    @task(1)
    def network_partition(self):
        self.client.post("/chaos/network", json={
            "partition_duration": f"{random.randint(5,15)}s",
            "affected_nodes": random.sample(range(8), k=3)
        })
