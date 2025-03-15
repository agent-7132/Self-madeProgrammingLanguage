import subprocess
import sys

def run_valgrind_check(binary_path):
    try:
        result = subprocess.run(
            ["valgrind", "--leak-check=full", "--error-exitcode=1", binary_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print("Valgrind Output:\n", result.stderr)
        
        if "ERROR SUMMARY: 0 errors" not in result.stderr:
            raise AssertionError(f"内存泄漏检测失败:\n{result.stderr}")
            
        return True
    except subprocess.TimeoutExpired:
        print("Valgrind检测超时")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python valgrind_check.py <binary_path>")
        sys.exit(1)
        
    success = run_valgrind_check(sys.argv[1])
    sys.exit(0 if success else 1)
