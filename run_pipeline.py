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


def generate_playwright_script():

    print(
        "\nGenerating Playwright Script..."
    )

    try:
        result = subprocess.run(
            [sys.executable, "llm_playwright_generator.py"],
            capture_output=True,
            text=True,
            timeout=GENERATION_TIMEOUT_SECONDS,
            check=False,
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
            f"Playwright generation failed with exit code {result.returncode}"
        )

    print(
        "Generation Complete"
    )

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
    args = parse_args()
    URL = args.url
    MAX_PAGES = args.max_pages

    print(f"[Pipeline] Target URL : {URL}")
    print(f"[Pipeline] Max pages  : {MAX_PAGES}")

    tracker = PerformanceTracker(label="full_pipeline_week2")
    tracker.start()

    try:
        print("=" * 50)
        print("Starting Crawl...")
        print("=" * 50)

        crawl_data = crawl_site(
            URL,
            max_pages=MAX_PAGES
        )

        pages_crawled = len(crawl_data)

        print(
            f"\nPages Crawled: {pages_crawled}"
        )

        generate_playwright_script()

        result = run_generated_test()

        execution_time = result[
            "execution_time"
        ]

        print(
            f"\nExecution Time: "
            f"{execution_time} sec"
        )

        tests_run = count_selectors(
            crawl_data
        )

        passed = tests_run

        failed = 0

        failures = []

        if result["return_code"] != 0:

            failed = 1

            passed = max(
                0,
                tests_run - 1
            )

            failures.append(
                {
                    "url": "unknown",
                    "selector": "unknown",
                    "error":
                    result["stderr"]
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

        print(
            "\nPipeline Complete"
        )

    except Exception as e:

        print(
            "\nPipeline Failed"
        )

        print(str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()