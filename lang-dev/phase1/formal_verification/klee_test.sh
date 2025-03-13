#!/bin/bash
# Quantum Symbolic Execution Preprocessing
qiskit-symbex --llvm memory_model.c --output memory_model.quantum.c \
  --topology ibmq_montreal \
  --optimize-level 3

clang -emit-llvm -c -DQUANTUM_EXTENSION memory_model.quantum.c -o memory_model.bc

klee --libc=uclibc --posix-runtime memory_model.bc \
  --output-dir=klee-out \
  --max-time=3600 \
  --sym-mem-size=4096 \
  --quantum-sim=ibmq_qasm_sim \
  --qpu-topology=27-qubit-lattice \
  --entanglement-threshold=0.95

python3 analyze_klee.py klee-out/ \
  --quantum-report \
  --entanglement-check \
  --output=verification_report.qvr
