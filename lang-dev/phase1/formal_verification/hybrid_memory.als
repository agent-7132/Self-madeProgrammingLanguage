open memory_model

pred HybridGC(t: Time) {
    QuantumBarrierMaintenance[t]
    some t': t.next | {
        GarbageCollection[t] implies ClassicMemoryReclamation[t']
        (qiskit_symbex_verify[t] and klee_verify[t]) => SafeAccess[t']
    }
}

assert HybridSafety {
    always all t: Time | HybridGC[t]
}

check HybridSafety for 10 but 5 Qubit, 4 Process

pred QuantumClassicSync(t: Time) {
    all q: Qubit | {
        q.quantum_state.t != none implies q.owner.t in q.zone.accessPolicy.permits[q.zone]
        q.gc_status.t = ManualControlled implies q.monitor_flag.t = True
    }
}

check QuantumClassicSync for 7
