import subprocess
import time
import os


def run_generated_test():

    test_file = "generated_tests/generated_test.py"

    if not os.path.exists(test_file):
        raise FileNotFoundError(
            f"{test_file} not found"
        )

    print("\nExecuting Generated Test...")

    start_time = time.time()

    result = subprocess.run(
        ["python", test_file],
        capture_output=True,
        text=True
    )

    end_time = time.time()

    execution_time = round(
        end_time - start_time,
        2
    )
    print(result.stdout)
    print(result.stderr)

    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "execution_time": execution_time
    }