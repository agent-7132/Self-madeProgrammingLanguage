import subprocess
import sys

def validate_embedded_memory():
    """基于Alloy模型验证嵌入式内存安全"""
    result = subprocess.run(
        ["alloy", "analyze", "phase1/formal_verification/memory_model.als"],
        capture_output=True,
        text=True
    )
    
    if "Counterexample found" in result.stdout:
        print("内存模型验证失败!")
        sys.exit(1)
    elif "No counterexample found" in result.stdout:
        print("内存模型验证通过")
        return True
    else:
        print("验证过程出现异常:")
        print(result.stderr)
        sys.exit(2)

if __name__ == "__main__":
    validate_embedded_memory()
