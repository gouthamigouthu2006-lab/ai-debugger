import subprocess
import tempfile
import sys
import traceback

def sandbox_run_python(code: str, timeout_sec=2):
    """
    Runs user-provided Python code safely in a subprocess sandbox.
    - Enforces timeout (prevents infinite loops)
    - Captures stdout and stderr
    - Executes in an isolated temporary file
    - Returns structured output
    """

    try:
        # 1️⃣ Create a temporary file for the user code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            file_path = f.name

        # 2️⃣ Run the code in a separate sandboxed process
        proc = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )

        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "timed_out": False
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Error: Program timed out (possible infinite loop or long execution)",
            "returncode": None,
            "timed_out": True
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": traceback.format_exc(),
            "returncode": None,
            "timed_out": False
        }