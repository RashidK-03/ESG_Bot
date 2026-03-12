from sources.eu_commission import fetch_eu_updates

updates = fetch_eu_updates()

print("Entries:", len(updates))

for u in updates[:1]:
    print("TITLE:", u["title"])
    print("LINK:", u["link"])
    print("PUBLISHED:", u["published"])
    print("------")