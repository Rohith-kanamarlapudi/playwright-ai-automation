from scraper.scraper import main
import json

data = main()

print("\n========== SCRAPER OUTPUT ==========\n")
print(json.dumps(data, indent=2))