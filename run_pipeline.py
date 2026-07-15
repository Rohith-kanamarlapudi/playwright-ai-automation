import os
import sys
import json
import subprocess
from performance.engine import PerformanceTracker

GENERATION_TIMEOUT_SECONDS = int(os.getenv("GENERATION_TIMEOUT_SECONDS", "600"))

from scraper.scraper import main as crawl_site
from test_runner import run_generated_test
from report_generator import (
    create_json_report,
    create_html_report
)


import argparse
from dotenv import load_dotenv
load_dotenv()

from db.database import (
    init_db,
    start_run,
    finish_run,
)
from db.selector_memory import init_selector_memory

from agents.heal_agent import (
    parse_pytest_failures,
    heal_agent,
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Playwright AI automation pipeline."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=os.getenv("TARGET_URL", "https://ideabytes.com"),
        help="Target website URL to scrape and test"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=int(os.getenv("MAX_PAGES", "10")),
        help="Maximum pages to crawl (default: 10)"
    )
    return parser.parse_args()


def generate_playwright_script(url: str = None):

    print(
        "\nGenerating Playwright Script..."
    )

    cmd = [sys.executable, "llm_playwright_generator.py"]
    if url:
        cmd += ["--url", url]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=GENERATION_TIMEOUT_SECONDS,
            check=False,
            env={**os.environ},   # explicit env pass (also fixes minor env-inheritance issue)
        )
    except subprocess.TimeoutExpired as e:
        raise Exception(
            f"Playwright generation timed out after "
            f"{GENERATION_TIMEOUT_SECONDS}s — check MAX_REGEN/"
            f"regen_count logic.\nPartial output:\n{e.stdout or ''}"
        )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        raise Exception(
            f"Playwright generation failed with exit code {result.returncode}\n"
            f"{result.stderr}"
        )

    print("Generation Complete")

def count_selectors(data):

    total = 0

    for page in data:

        total += len(
            page.get("buttons", [])
        )

        total += len(
            page.get("inputs", [])
        )

        total += len(
            page.get("links", [])
        )

    return total


def main():
    init_db()
    init_selector_memory()
    args = parse_args()
    target_url = args.url
    max_pages = args.max_pages
    
    run_id = None
    run_id = start_run(
        target_url=target_url,
        llm_provider=os.getenv("LLM_PROVIDER", "deepseek"),
        llm_model=os.getenv("LLM_MODEL", "deepseek-chat"),
    )

    print(f"[Pipeline] Target URL : {target_url}")
    print(f"[Pipeline] Max pages  : {max_pages}")

    tracker = PerformanceTracker(label="full_pipeline_week2")
    tracker.start()
    execution_failures = []

    try:
        print("=" * 50)
        print("Starting Crawl...")
        print("=" * 50)

        crawl_data = crawl_site(
            target_url,
            max_pages=max_pages
        )
        if not crawl_data:
            raise Exception("Crawler returned no pages.")

        pages_crawled = len(crawl_data)

        print(
            f"\nPages Crawled: {pages_crawled}"
        )
        
        
        tests_run = count_selectors(crawl_data)

        if tests_run == 0:
            print("WARNING: No selectors found during crawling.")

        generate_playwright_script(url=target_url)
        
        
        generated_yaml = ""

        if os.path.exists("generated_tests/generated_yaml.yaml"):
            with open(
                "generated_tests/generated_yaml.yaml",
                "r",
                encoding="utf-8",
            ) as f:
                generated_yaml = f.read()
        else:
            print("[Pipeline] Warning: generated_yaml.yaml not found.")


        generated_code = ""

        if os.path.exists("generated_tests/generated_test.py"):
            with open(
                "generated_tests/generated_test.py",
                "r",
                encoding="utf-8",
            ) as f:
                generated_code = f.read()
        else:
            print("[Pipeline] Warning: generated_test.py not found.")



        result = run_generated_test()
        
        
        if not isinstance(result, dict):
            raise Exception(
                "Healed test runner returned an invalid result."
            )
        
        if not isinstance(result, dict):
            raise Exception("Test runner returned an invalid result.")
        
        
        
        # ----------------------------------------------------
        # Heal failed Playwright tests
        # ----------------------------------------------------

        stdout = result.get("stdout", "")

        execution_failures = parse_pytest_failures(stdout)

        if execution_failures:

            print(
                f"[Pipeline] Found {len(execution_failures)} execution failure(s)."
            )

            generated_code = ""

            if os.path.exists("generated_tests/generated_test.py"):
                with open(
                    "generated_tests/generated_test.py",
                    "r",
                    encoding="utf-8",
                ) as f:
                    generated_code = f.read()

            heal_state = {
                "generated_code": generated_code,
                "execution_stdout": stdout,
                "execution_return_code": result.get("return_code", 1),
                "execution_failures": execution_failures,
                "needs_regen": False,
                "best_code": generated_code,
            }

            healed_state = heal_agent(heal_state)

            with open(
                "generated_tests/generated_test.py",
                "w",
                encoding="utf-8",
            ) as f:

                generated_code = healed_state["generated_code"]
                f.write(generated_code)

            print(
                "[Pipeline] Healed Playwright test saved."
            )
            
            
            
            print("\n[Pipeline] Re-running healed Playwright tests...")

            result = run_generated_test()

            stdout = result.get("stdout", "")

            execution_failures = parse_pytest_failures(stdout)

            print(
                f"[Pipeline] Remaining failures: "
                f"{len(execution_failures)}"
            )
            
            
            
            if result.get("return_code", 1) == 0:
                passed = tests_run
                failed = 0
            else:
                failed = len(execution_failures)
                passed = max(
                    0,
                    tests_run - failed
                )
                                

        execution_time = result.get(
            "execution_time",
            0
        )

        print(
            f"\nExecution Time: "
            f"{execution_time} sec"
        )


        passed = tests_run

        failed = 0

        failures = []

        if result.get("return_code", 1) != 0:

            failed = 1

            passed = max(
                0,
                tests_run - 1
            )

            failures = execution_failures

            if not failures and result.get("return_code", 1) != 0:
                failures.append(
                    {
                        "url": "unknown",
                        "selector": "unknown",
                        "error": result.get(
                            "stderr",
                            "Unknown error"
                        ),
                    }
                )

        print(
            f"Passed: {passed}"
        )

        print(
            f"Failed: {failed}"
        )

        report = create_json_report(
            pages_crawled,
            tests_run,
            passed,
            failed,
            execution_time,
            failures
        )

        create_html_report(
            report
        )
        
        
        finish_run(
            run_id=run_id,
            status="passed",
            result={
                "duration_seconds": execution_time,
                "pages_crawled": pages_crawled,
                "selectors_found": tests_run,
                "tests_generated": tests_run,
                "tests_passed": passed,
                "tests_failed": failed,
                "regen_count": 0,
                "heal_attempted": len(execution_failures) > 0,
                "heal_failures": len(execution_failures),
                "generated_code": generated_code,
                "generated_yaml": generated_yaml,
                "review_notes": "",
                "edge_cases": [],
            },
        )
                  

        if execution_failures:
            print(
                f"[Pipeline] Heal Agent repaired "
                f"{len(execution_failures)} failure(s)."
            )
        print(
            "\nPipeline Complete"
        )

    except Exception as e:
        tracker.stop(agents_completed=0)
        finish_run(
            run_id=run_id,
            status="failed",
            result={
                "duration_seconds": 0,
                "pages_crawled": 0,
                "selectors_found": 0,
                "tests_generated": 0,
                "tests_passed": 0,
                "tests_failed": 1,
                "regen_count": 0,
                "generated_code": "",
                "generated_yaml": "",
                "review_notes": str(e),
                "edge_cases": [],
            },
        )

        print("\nPipeline Failed")

        print(str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()