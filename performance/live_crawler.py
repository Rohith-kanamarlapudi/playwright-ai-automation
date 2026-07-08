# performance/live_crawler.py  (new file)
from email.mime import base
import time
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LIVE_URL = os.getenv("LIVE_APP_URL", "https://live.ideabytesiot.com/demolive")
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

def measure_route(url: str, label: str = "") -> dict:
    """
    Measure TTFB and total response time for a single URL.
    Returns a dict with timing metrics.
    """
    label = label or url
    headers = {"User-Agent": "Mozilla/5.0 (PlaywrightAI Crawler)"}
    cookies = {}
    session_cookie = os.getenv("SESSION_COOKIE", "")
    if session_cookie:
        cookies["session"] = session_cookie

    start = time.time()
    try:
        resp = requests.get(url, headers=headers, cookies=cookies,
                            timeout=30, allow_redirects=True)
        ttfb = resp.elapsed.total_seconds()
        total = time.time() - start

        return {
            "label": label,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status_code": resp.status_code,
            "ttfb_seconds": round(ttfb, 3),
            "total_seconds": round(total, 3),
            "content_length_bytes": len(resp.content),
            "redirected": resp.url != url,
            "final_url": resp.url,
        }
    except Exception as e:
        return {
            "label": label,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status_code": None,
            "ttfb_seconds": None,
            "total_seconds": round(time.time() - start, 3),
        }


def run_live_baseline(routes: list = None, runs: int = 3) -> dict:
    """
    Run 'runs' measurement passes over all routes.
    Saves result to reports/live_perf_baseline.json.
    Returns summary dict.
    """
    if routes is None:
        base = LIVE_URL.rstrip("/")
        routes = [
            (LIVE_URL, "dashboard"),
            (base + "/dashboard/status-list", "status_dashboard"),
            (base + "/reports/scheduled", "reports"),
            (base + "/alerts", "alerts"),
            (base + "/devices", "devices"),
            (base + "/alarms", "alarms"),
            (base + "/users/users-management", "users"),
        ]

    all_results = []

    for run_num in range(1, runs + 1):
        print(f"[Live Crawler] Run {run_num}/{runs}")
        run_results = []
        for url, label in routes:
            result = measure_route(url, label=f"{label}_run{run_num}")
            run_results.append(result)
            status = result.get("status_code", "ERR")
            ttfb   = result.get("ttfb_seconds", "N/A")
            total  = result.get("total_seconds", "N/A")
            print(f"  {label}: HTTP {status} | TTFB {ttfb}s | total {total}s")
            time.sleep(2)  # throttle — avoid hammering the live server
        all_results.append(run_results)

    # Compute averages per route
    summary = {}
    for run_results in all_results:
        for r in run_results:
            key = r["label"].rsplit("_run", 1)[0]
            if key not in summary:
                summary[key] = {"ttfb": [], "total": [], "status": []}
            if r.get("ttfb_seconds"):
                summary[key]["ttfb"].append(r["ttfb_seconds"])
            if r.get("total_seconds"):
                summary[key]["total"].append(r["total_seconds"])
            if r.get("status_code"):
                summary[key]["status"].append(r["status_code"])

    averages = {}
    for key, vals in summary.items():
        averages[key] = {
            "avg_ttfb_seconds": round(sum(vals["ttfb"]) / len(vals["ttfb"]), 3) if vals["ttfb"] else None,
            "avg_total_seconds": round(sum(vals["total"]) / len(vals["total"]), 3) if vals["total"] else None,
            "status_codes": list(set(vals["status"])),
        }

    output = {
        "generated_at": datetime.now().isoformat(),
        "live_url": LIVE_URL,
        "runs": runs,
        "raw": all_results,
        "averages": averages,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "live_perf_baseline.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[Live Crawler] Baseline saved to {out_path}")
    print("\nAverages:")
    for route, avg in averages.items():
        print(f"  {route}: TTFB={avg['avg_ttfb_seconds']}s  Total={avg['avg_total_seconds']}s")

    return output


if __name__ == "__main__":
    run_live_baseline(runs=3)