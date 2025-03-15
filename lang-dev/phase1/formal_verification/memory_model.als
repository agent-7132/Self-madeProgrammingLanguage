module memory_model
open util/ordering[Time]

sig Complex {
  real: one univ,
  imag: one univ
} {
  real in Int
  imag in Int
  add[mul[real, real], mul[imag, imag]] >= 0
}

sig MemoryBlock {
  var owner: lone Process,
  var zone: Zone,
  var gc_status: GcState
}

enum GcState { Reachable, Unreachable, ManualControlled }

sig Qubit extends MemoryBlock {
  entanglement: set Qubit,
  var quantum_state: lone QuantumState,
  var monitor_flag: Bool
}

pred GarbageCollection(t: Time) {
  some t': t.next | {
    all b: MemoryBlock |
      b.gc_status.t = Unreachable => {
        b.owner.t' = none
        b.zone.t' = b.zone.t
        b.gc_status.t' = Reachable
        b in Qubit => b.quantum_state.t' = none
      }
  }
}

pred SafeAccess(t: Time) {
  all p: Process, b: MemoryBlock |
    b in Qubit => {
      b.monitor_flag.t = True
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

fact Initialization {
  all q: Qubit | q.monitor_flag.first = True
}

fact QuantumBarrierMaintenance {
  always all q: Qubit | q.entanglement != none => after q.zone' != q.entanglement.zone
}

sig Process {}
sig Zone { accessPolicy: Policy }
sig Policy { permits: Process -> Zone }

fact Normalization {
  always all qs: QuantumState | 
    add[mul[qs.amplitude.real, qs.amplitude.real], 
        mul[qs.amplitude.imag, qs.amplitude.imag]] = 1
}

assert SafetyInvariant {
  always SafeAccess
}

check SafetyInvariant for 5 but 3 Process, 2 Zone, 2 Qubit
