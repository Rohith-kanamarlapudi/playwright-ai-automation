import json
from datetime import datetime
from pathlib import Path


REPORT_FOLDER = "reports"


def create_json_report(
    pages_crawled,
    tests_run,
    passed,
    failed,
    execution_time,
    failures
):

    Path(REPORT_FOLDER).mkdir(
        exist_ok=True
    )

    report = {

        "generated_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "pages_crawled":
        pages_crawled,

        "tests_run":
        tests_run,

        "passed":
        passed,

        "failed":
        failed,

        "execution_time":
        execution_time,

        "failures":
        failures
    }

    json_file = (
        f"{REPORT_FOLDER}/"
        "test_execution_report.json"
    )

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"JSON Report Saved: {json_file}"
    )

    return report


def create_html_report(report):

    rows = ""

    for failure in report["failures"]:

        rows += f"""
        <tr>
            <td>{failure['url']}</td>
            <td>{failure['selector']}</td>
            <td>{failure['error']}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>

<head>

<title>Automation Report</title>

<style>

body {{
    font-family: Arial;
    margin: 30px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 10px;
}}

th {{
    background-color: #f2f2f2;
}}

</style>

</head>

<body>

<h1>Playwright Automation Report</h1>

<p><b>Pages Crawled:</b> {report['pages_crawled']}</p>

<p><b>Tests Run:</b> {report['tests_run']}</p>

<p><b>Passed:</b> {report['passed']}</p>

<p><b>Failed:</b> {report['failed']}</p>

<p><b>Execution Time:</b> {report['execution_time']} sec</p>

<h2>Failures</h2>

<table>

<tr>
<th>URL</th>
<th>Selector</th>
<th>Error</th>
</tr>

{rows}

</table>

</body>
</html>
"""

    html_file = (
        f"{REPORT_FOLDER}/"
        "test_execution_report.html"
    )

    with open(
        html_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    print(
        f"HTML Report Saved: {html_file}"
    )