namespace Lang.QuantumOptimizer {
  open Microsoft.Quantum.Intrinsic;
  open Microsoft.Quantum.Canon;
  open Microsoft.Quantum.Optimization;
  open Microsoft.Quantum.Diagnostics;

  operation OptimizeTypeGraph(qubits : Qubit[], adjacencyMatrix : Double[][]) : Double {
    using (ancilla = Qubit()) {
      H(ancilla);
      
      let topology = GetTopology(qubits);
      ApplyLayoutOptimization(qubits, topology);

      for i in IndexRange(qubits) {
        Controlled Ry([qubits[i]], (PI(adjacencyMatrix[i][i]), ancilla));
        for j in i+1..Length(qubits)-1 {
          if adjacencyMatrix[i][j] > 0.7 {
            ApplyGateMerge(qubits[i], qubits[j]);
          }
          Controlled Rz([qubits[i], qubits[j]], 
            (adjacencyMatrix[i][j] * 2.0 * PI(), ancilla));
        }
      }
      
      let fidelity = MeasureDecoherence(qubits, 3);
      return Expectation(PauliZ, ancilla) * fidelity;
    }
  }

  operation ApplyGateMerge(q1 : Qubit, q2 : Qubit) : Unit {
    body (...) {
      CCNOT(q1, q2, q2);
      R1(0.5 * PI(), q2);
      CCNOT(q1, q2, q2);
    }
    adjoint auto;
  }
}
