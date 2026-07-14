from scraper.scraper import main as scrape
import time

print("=" * 70)
print("Selector Stability Test")
print("=" * 70)

URL = "https://live.ideabytesiot.com/demolive"

results = []

for run in range(1, 4):

    print(f"\nRun {run}")

    data = scrape(URL, max_pages=3)

    total = 0

    for page in data:
        total += (
            len(page.get("buttons", []))
            + len(page.get("inputs", []))
            + len(page.get("links", []))
        )

    results.append(total)

    print(f"Pages: {len(data)}")
    print(f"Selectors: {total}")

    time.sleep(5)

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

for i, total in enumerate(results, 1):
    print(f"Run {i}: {total}")

variation = max(results) - min(results)

print(f"\nVariation: {variation}")

if variation <= 5:
    print("✅ Selector stability PASS")
else:
    print("❌ Selector stability FAIL")