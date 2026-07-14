from scraper.scraper import main as scrape
import json

print("=" * 70)
print("Testing Authenticated Live App Scraper")
print("=" * 70)

data = scrape(
    "https://live.ideabytesiot.com/demolive",
    max_pages=10
)

print(f"\nPages Crawled: {len(data)}")
print("=" * 70)

for i, page in enumerate(data, start=1):
    print(f"\n[{i}] {page['url']}")
    print(f"Buttons   : {len(page.get('buttons', []))}")
    print(f"Inputs    : {len(page.get('inputs', []))}")
    print(f"Links     : {len(page.get('links', []))}")

    if "dropdowns" in page:
        print(f"Dropdowns : {len(page.get('dropdowns', []))}")

    if "tables" in page:
        print(f"Tables    : {len(page.get('tables', []))}")

    if "headings" in page:
        print(f"Headings  : {len(page.get('headings', []))}")

print("\n" + "=" * 70)

if data:
    print("First Page Sample")
    print("=" * 70)
    print(json.dumps(data[0], indent=2)[:2000])