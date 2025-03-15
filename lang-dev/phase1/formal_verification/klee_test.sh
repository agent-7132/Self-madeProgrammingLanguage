#!/bin/bash
set -e

qiskit-symbex --llvm phase1/formal_verification/memory_model.als \
  --output phase1/formal_verification/generated_model.c

clang -emit-llvm -c -DQUANTUM_EXTENSION \
  phase1/formal_verification/generated_model.c \
  -o phase1/formal_verification/model.bc

klee --libc=uclibc --posix-runtime \
  phase1/formal_verification/model.bc \
  --output-dir=klee-out \
  --max-time=3600 \
  --sym-mem-size=4096 \
  --quantum-sim=ibmq_qasm_sim \
  --qpu-topology=27-qubit-lattice

python3 analyze_klee.py klee-out/ \
  --quantum-report \
  --entanglement-check \
  --output=verification_report.qvr
