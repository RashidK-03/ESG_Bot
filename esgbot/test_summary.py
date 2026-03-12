from summarizer import generate_summary
from sources.eu_commission import fetch_eu_updates

updates = fetch_eu_updates()

if not updates:
    raise RuntimeError("fetch_eu_updates() returned an empty list.")

first = updates[0]

print("=== RAW NEWS ITEM ===")
print(first)
print("\n=== GENERATED SUMMARY ===\n")

summary = generate_summary(
    first["title"],
    first.get("description", "")  # безопасный доступ
)

print(summary)