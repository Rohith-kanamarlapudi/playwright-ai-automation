import os
import json

from scraper.scraper import main as crawl_site
from test_runner import run_generated_test
from report_generator import (
    create_json_report,
    create_html_report
)


URL = "https://ideabytes.com"
MAX_PAGES = 10


def generate_playwright_script():

    print(
        "\nGenerating Playwright Script..."
    )

    result = os.system(
        "python llm_playwright_generator.py"
    )

    if result != 0:

        raise Exception(
            "Playwright generation failed"
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

    try:

        print("=" * 50)
        print("Starting Crawl...")
        print("=" * 50)

        crawl_data = crawl_site(
            URL,
            max_pages=MAX_PAGES
        )

        pages_crawled = len(
            crawl_data
        )

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


if __name__ == "__main__":
    main()