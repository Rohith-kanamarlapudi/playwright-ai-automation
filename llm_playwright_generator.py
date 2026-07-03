"""
Entry point called by run_pipeline.py.

Reads the scraper output from reports/website_elements.json
and runs it through the LangGraph multi-agent pipeline.
"""

import json
import os

from agents.pipeline import run_agent_pipeline
from agents.scraper_adapter import build_selectors_from_crawl

SCRAPER_OUTPUT = "reports/website_elements.json"


def main():

    # ------------------------------------------------------
    # Check scraper output
    # ------------------------------------------------------

    if not os.path.exists(SCRAPER_OUTPUT):
        print(f"ERROR: {SCRAPER_OUTPUT} not found.")
        print("Run the scraper first.")
        return

    # ------------------------------------------------------
    # Load crawler output
    # ------------------------------------------------------

    with open(
        SCRAPER_OUTPUT,
        "r",
        encoding="utf-8"
    ) as f:

        crawl_data = json.load(f)

    # ------------------------------------------------------
    # Build design document summary
    # ------------------------------------------------------

    page_summaries = []

    for page in crawl_data:

        summary = (
            f"Page: {page.get('url', '')}\n"
            f"- Buttons : {len(page.get('buttons', []))}\n"
            f"- Inputs  : {len(page.get('inputs', []))}\n"
            f"- Links   : {len(page.get('links', []))}"
        )

        page_summaries.append(summary)

    design_doc = (
        "Generate Playwright automation tests for this website.\n\n"
        + "\n\n".join(page_summaries)
    )

    # ------------------------------------------------------
    # Convert scraper output into selector list
    # ------------------------------------------------------

    selectors = build_selectors_from_crawl(crawl_data)

    print("=" * 70)
    print("LangGraph Playwright Generator")
    print("=" * 70)
    print(f"Pages      : {len(crawl_data)}")
    print(f"Selectors  : {len(selectors)}")
    print("=" * 70)

    # ------------------------------------------------------
    # Run pipeline
    # ------------------------------------------------------

    result = run_agent_pipeline(
        design_doc=design_doc,
        selectors=selectors
    )

    print("\nPipeline completed successfully.\n")

    print(f"Task Plan        : {len(result['task_plan'])} tasks")
    print(f"Generated Code   : {len(result['generated_code'])} characters")
    print(f"Edge Cases       : {len(result['edge_cases'])}")

    print("\nGenerated files:")
    print("  generated_tests/generated_yaml.yaml")
    print("  generated_tests/generated_test.py")


if __name__ == "__main__":
    main()