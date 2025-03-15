namespace Lang.QuantumOptimizer {
  open Microsoft.Quantum.Intrinsic;
  open Microsoft.Quantum.Canon;
  open Microsoft.Quantum.Diagnostics;
  open Microsoft.Quantum.Math;
  open Microsoft.Quantum.Convert;

  struct Coupling {
    Control: Int;
    Target: Int;
  }

  operation GetTopology(qubits : Qubit[]) : Topology {
    mutable topology = [];
    for i in 0..Length(qubits)-2 {
      set topology += [Coupling(i, i+1)];
    }
    return topology;
  }

  operation ApplyLayoutOptimization(qubits : Qubit[], topology : Topology) : Unit {
    ApplyToEach(H, qubits);
    for coupling in topology {
      CNOT(qubits[coupling.Control], qubits[coupling.Target]);
    }
  }

  operation MeasureDecoherence(qubits : Qubit[], samples : Int) : Double {
    use register = Qubit[2];
    ApplyPauliMeasurement([PauliX, PauliY, PauliZ], qubits, register);
    let fidelity = CalculateFidelity(register);
    ResetAll(register);
    return fidelity;
  }

  operation CalculateFidelity(register : Qubit[]) : Double {
    mutable sum = 0.0;
    for state in [Zero, One] {
      set sum += Probability([state], register);
    }
    return sum / 2.0;
  }

  operation OptimizeTypeGraph(qubits : Qubit[], adjacencyMatrix : Double[][]) : Double {
    let topology = GetTopology(qubits);
    ApplyLayoutOptimization(qubits, topology);

    using (ancilla = Qubit()) {
      H(ancilla);
      
      for i in IndexRange(qubits) {
        Controlled Ry([qubits[i]], (PI(adjacencyMatrix[i][i]), ancilla));
        for j in i+1..Length(qubits)-1 {
          if adjacencyMatrix[i][j] > 0.7 {
            CCNOT(qubits[i], qubits[j], qubits[j]);
            R1(0.5 * PI(), qubits[j]);
            CCNOT(qubits[i], qubits[j], qubits[j]);
          }
          Controlled Rz([qubits[i], qubits[j]], 
            (adjacencyMatrix[i][j] * 2.0 * PI(), ancilla));
        }
      }
      
      let fidelity = MeasureDecoherence(qubits, 3);
      return Expectation(PauliZ, ancilla) * fidelity;
    }
  }
}
