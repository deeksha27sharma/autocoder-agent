import subprocess
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

def execute_code(code: str, timeout: int = 10) -> dict:
    """
    Executes Python code in a safe subprocess sandbox.
    Returns stdout, stderr, and success status.
    """
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(code)
        fname = f.name

    try:
        result = subprocess.run(
            ["python", fname],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Timeout: code exceeded {timeout} seconds",
            "success": False
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Executor error: {str(e)}",
            "success": False
        }

    finally:
        os.unlink(fname)  # always delete temp file


def format_result(result: dict) -> str:
    """
    Formats execution result into readable string for the agent.
    """
    if result["success"]:
        return f"✅ Code ran successfully.\nOutput:\n{result['stdout']}"
    else:
        return f"❌ Code failed.\nError:\n{result['stderr']}"
    


if __name__ == "__main__":
    # Test 1: successful code
    result = execute_code("x = 5 + 3\nprint(f'Result: {x}')")
    print(format_result(result))
    print("---")

    # Test 2: syntax error
    result = execute_code("def broken(\n    print('oops')")
    print(format_result(result))
    print("---")

    # Test 3: runtime error
    result = execute_code("print(1 / 0)")
    print(format_result(result))
    print("---")

    # Test 4: timeout
    result = execute_code("while True: pass", timeout=3)
    print(format_result(result))