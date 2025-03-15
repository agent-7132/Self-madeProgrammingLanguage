from protoactor import Actor, ActorContext, RootContext, Props
import numpy as np
from ..math.gpu_quantum_ops import HybridGPUQuantum

class TensorShard:
    def __init__(self, data: np.ndarray, weights: np.ndarray, shard_id: int):
        self.data = data
        self.weights = weights
        self.shard_id = shard_id

class ProcessedShard:
    def __init__(self, data: np.ndarray, shard_id: int):
        self.data = data
        self.shard_id = shard_id

class QuantumTaskActor(Actor):
    async def receive(self, context: ActorContext):
        if isinstance(context.message, dict):
            if 'matrix' in context.message and 'other_matrix' in context.message:
                result = HybridGPUQuantum.quantum_guided_gemm(
                    context.message['matrix'], 
                    context.message['other_matrix']
                )
                context.respond({'result': result, 'task_id': context.message.get('task_id')})

class TensorShardActor(Actor):
    def __init__(self):
        self.accumulator = None
        
    async def receive(self, context: ActorContext):
        if isinstance(context.message, TensorShard):
            shard = context.message
            processed = HybridGPUQuantum.hybrid_precision_gemm(shard.data, shard.weights)
            context.send(context.parent, ProcessedShard(processed, shard.shard_id))

class CoordinatorActor(Actor):
    def __init__(self):
        self.received_shards = {}
        self.expected_shards = 0
        
    async def receive(self, context: ActorContext):
        if isinstance(context.message, ProcessedShard):
            shard = context.message
            self.received_shards[shard.shard_id] = shard.data
            if len(self.received_shards) == self.expected_shards:
                aggregated = self._aggregate_shards()
                context.respond(aggregated)
                
        elif isinstance(context.message, int):
            self.expected_shards = context.message
            
    def _aggregate_shards(self) -> np.ndarray:
        sorted_shards = [self.received_shards[k] for k in sorted(self.received_shards)]
        return np.concatenate(sorted_shards, axis=1)

class ActorSystem:
    def __init__(self):
        self.root = RootContext()
        self.shard_actor = self.root.spawn(Props(TensorShardActor))
        self.coordinator = self.root.spawn(Props(CoordinatorActor))
        
    def distribute_task(self, tensor: np.ndarray, weights: np.ndarray, num_shards: int):
        shards = np.split(tensor, num_shards, axis=0)
        self.coordinator.tell(num_shards)
        
        for i, shard in enumerate(shards):
            task = TensorShard(shard, weights, i)
            self.root.send(self.shard_actor, task)
            
    def get_result(self, timeout: float = 5.0) -> np.ndarray:
        return self.root.request_future(self.coordinator, None, timeout).result()
