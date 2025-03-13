module memory_model
open util/ordering[Time]

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
sig Complex {}

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

assert SafetyInvariant {
  always SafeAccess
}

check SafetyInvariant for 5 but 3 Process, 2 Zone, 2 Qubit
