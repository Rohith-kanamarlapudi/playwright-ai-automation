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

    try:
        with open(
            SCRAPER_OUTPUT,
            "r",
            encoding="utf-8"
        ) as f:
            crawl_data = json.load(f)

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {SCRAPER_OUTPUT}")
        print(e)
        return
    if not crawl_data:
        print("ERROR: Scraper output is empty.")
        return

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
    
    if not selectors:
        print("ERROR: No selectors extracted from crawler output.")
        return

    print("=" * 70)
    print("LangGraph Playwright Generator")
    print("=" * 70)
    print(f"Pages      : {len(crawl_data)}")
    print(f"Selectors  : {len(selectors)}")
    print("=" * 70)

    # ------------------------------------------------------
    # Run pipeline
    # ------------------------------------------------------

    try:
        result = run_agent_pipeline(
            design_doc=design_doc,
            selectors=selectors
        )
    except Exception as e:
        print(f"\nERROR: Pipeline execution failed.\n{e}")
        return

    print("\nPipeline completed successfully.\n")

    print(f"Task Plan        : {len(result.get('task_plan', []))} tasks")
    print(f"Generated Code   : {len(result.get('generated_code', ''))} characters")
    print(f"Edge Cases       : {len(result.get('edge_cases', []))}")



    print("\nGenerated files:")

    for file in [
        "generated_tests/generated_yaml.yaml",
        "generated_tests/generated_test.py",
    ]:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (not generated)")

if __name__ == "__main__":
    main()