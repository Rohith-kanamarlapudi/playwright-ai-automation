import subprocess
import time
import os
import sys


def run_generated_test():
    """
    Executes the generated Playwright test and returns execution details.
    """

    test_file = "generated_tests/generated_test.py"

    if not os.path.exists(test_file):
        raise FileNotFoundError(
            f"{test_file} not found. Run the code generation pipeline first."
        )

    print("\n" + "=" * 70)
    print("Executing Generated Test")
    print("=" * 70)

    start_time = time.time()


    TIMEOUT_SECONDS = 60

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        print(f"[Test Runner] TIMEOUT after {TIMEOUT_SECONDS}s — killing process.")
        return {
            "return_code": -1,
            "stdout": "",
            "stderr": f"Test timed out after {TIMEOUT_SECONDS} seconds.",
            "execution_time": TIMEOUT_SECONDS
        }

    end_time = time.time()

    execution_time = round(
        end_time - start_time,
        2
    )

    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "execution_time": execution_time
    }


if __name__ == "__main__":

    try:

        result = run_generated_test()

        print("\n" + "=" * 70)
        print("TEST RUNNER REPORT")
        print("=" * 70)

        print(f"Return Code    : {result['return_code']}")
        print(f"Execution Time : {result['execution_time']} seconds")

        print("\n" + "=" * 70)
        print("STDOUT")
        print("=" * 70)

        if result["stdout"].strip():
            print(result["stdout"])
        else:
            print("No stdout generated.")

        print("\n" + "=" * 70)
        print("STDERR")
        print("=" * 70)

        if result["stderr"].strip():
            print(result["stderr"])
        else:
            print("No stderr generated.")

    except Exception as e:

        print("\n" + "=" * 70)
        print("TEST RUNNER FAILED")
        print("=" * 70)
        print(e)