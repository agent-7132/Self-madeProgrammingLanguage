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
  var zone: Zone
}

sig Qubit extends MemoryBlock {
  entanglement: set Qubit,
  var quantum_state: lone QuantumState
}

sig QuantumState {
  basis: Basis one,
  amplitude: Complex
}

enum Basis { Computational, Hadamard }

sig Process {}
sig Zone { accessPolicy: Policy }
sig Policy { permits: Process -> Zone }

pred SafeAccess(t: Time) {
  all p: Process, b: MemoryBlock |
    b in Qubit => {
      b.owner.t = p => p in b.zone.accessPolicy.permits[b.zone]
      no (b.entanglement & p.(owns.t))
    } else {
      b.owner.t = p => p in b.zone.accessPolicy.permits[b.zone]
    }
}

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
