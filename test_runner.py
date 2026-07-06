import subprocess
import time
import os
import sys
import ast

BANNED_ATTR_CALLS = {
    "os.system",
    "os.popen",
}

BANNED_FUNCTIONS = {
    "eval",
    "exec",
    "__import__",
    "compile",
}


def ast_safety_check(filepath: str) -> tuple[bool, str]:
    """
    Parse the generated file with AST and reject any file that
    contains dangerous calls or imports.

    Returns:
        (is_safe: bool, reason: str)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            # Block: import os / import subprocess
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("os", "subprocess"):
                        return False, f"Banned import: {alias.name}"

            # Block: from os import system
            if isinstance(node, ast.ImportFrom):
                if node.module in ("os", "subprocess", "sys"):
                    return False, f"Banned from-import: {node.module}"

            # Block: eval(...) / exec(...) / __import__(...)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in BANNED_FUNCTIONS:
                        return False, f"Banned call: {node.func.id}()"
                if isinstance(node.func, ast.Attribute):
                    full = f"{getattr(node.func.value, 'id', '')}."
                    full += node.func.attr
                    if full in BANNED_ATTR_CALLS:
                        return False, f"Banned call: {full}()"

        return True, "OK"

    except SyntaxError as e:
        return False, f"Syntax error in generated file: {e}"
    except Exception as e:
        return False, f"AST check failed: {e}"

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
    is_safe, reason = ast_safety_check(test_file)
    if not is_safe:
        print(f"[Test Runner] SAFETY BLOCK: {reason}")
        return {
            "return_code": -2,
            "stdout": "",
            "stderr": f"Generated file blocked by safety check: {reason}",
            "execution_time": 0,
        }

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False  # We handle return codes ourselves
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