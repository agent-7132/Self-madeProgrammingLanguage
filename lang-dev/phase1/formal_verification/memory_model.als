module memory_model
open util/ordering[Time]

sig Complex {
  real: one Int,
  imag: one Int
} {
  add[mul[real, real], mul[imag, imag]] = 1
}

sig MemoryBlock {
  var owner: lone Process,
  var zone: Zone,
  var gc_status: GcState  -- 新增GC状态跟踪（文档1双模式内存管理）
}

enum GcState { Reachable, Unreachable, ManualControlled }

sig Qubit extends MemoryBlock {
  entanglement: set Qubit,
  var quantum_state: lone QuantumState,
  var monitor_flag: Bool  -- 文档2热力图监控标记
}

-- 新增GC回收规则（文档1内存管理模型）
pred GarbageCollection(t: Time) {
  some t': t.next | {
    all b: MemoryBlock |
      b.gc_status.t = Unreachable => {
        b.owner.t' = none
        b.zone.t' = b.zone.t
        b.gc_status.t' = Reachable
      }
  }
}

-- 增强安全访问规则（文档2量子加密要求）
pred SafeAccess(t: Time) {
  all p: Process, b: MemoryBlock |
    b in Qubit => {
      b.monitor_flag.t = True  -- 强制监控标记
      b.owner.t = p => p in b.zone.accessPolicy.permits[b.zone]
      no (b.entanglement & p.(owns.t))
    } else {
      b.owner.t = p => p in b.zone.accessPolicy.permits[b.zone]
    }
}

sig QuantumState {
  basis: Basis one,
  amplitude: Complex
}

enum Basis { Computational, Hadamard }

sig Process {}
sig Zone { accessPolicy: Policy }
sig Policy { permits: Process -> Zone }

fact QuantumBarrier {
  always all q: Qubit | q.zone != q.entanglement.zone
}

fact Normalization {
  always all qs: QuantumState | 
    add[mul[qs.amplitude.real, qs.amplitude.real], 
        mul[qs.amplitude.imag, qs.amplitude.imag]] = 1
}

assert SafetyInvariant {
  always SafeAccess
}

check SafetyInvariant for 5 but 3 Process, 2 Zone, 2 Qubit
