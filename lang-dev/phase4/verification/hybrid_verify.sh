#!/bin/bash
set -e

# 混合符号执行验证
qiskit-symbex --hybrid phase4/verification/hybrid_model.als \
  --quantum-backend aer_simulator \
  --classic-solver z3 \
  --output generated/hybrid_verification.c

# 编译为LLVM IR
clang-18 -S -emit-llvm -o generated/hybrid_verification.ll \
  -DQUANTUM_EXTENSION \
  generated/hybrid_verification.c

# 运行KLEEHybrid扩展
klee --hybrid-mode=quantum-classic \
  --quantum-simulator=qiskit \
  --max-qubit=16 \
  generated/hybrid_verification.ll \
  --output-dir=klee-out-hybrid

# 生成联合验证报告
python3 analyze_hybrid.py klee-out-hybrid/ \
  --quantum-metrics \
  --classic-coverage \
  --output=hybrid_verification.qvr
