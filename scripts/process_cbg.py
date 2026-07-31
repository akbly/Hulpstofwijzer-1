import csv
import json
import re
import datetime

SRC = "metadata.csv"

MAANDEN = ["januari","februari","maart","april","mei","juni","juli",
           "augustus","september","oktober","november","december"]

def split_stoffen(raw):
    if not raw or not isinstance(raw, str):
        return []
    raw = raw.strip()
    if raw == "" or raw.upper() in ("GEEN HULPSTOFFEN", "GEEN WERKZAME STOFFEN", "GEEN"):
        return []
    parts = [p.strip() for p in raw.split("#")]
    seen = set()
    out = []
    for p in parts:
        p2 = re.sub(r"\s+", " ", p).strip()
        if not p2:
            continue
        key = p2.upper()
        if key in seen:
            continue
        seen.add(key)
        out.append(p2)
    return out

records = []
with open(SRC, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="|")
    for row in reader:
        productnaam = (row.get("PRODUCTNAAM") or "").strip()
        if not productnaam:
            continue
        hulpstoffen = split_stoffen(row.get("HULPSTOFFEN", ""))
        werkzamestoffen = split_stoffen(row.get("WERKZAMESTOFFEN", ""))
        atc_raw = (row.get("ATC") or "").strip()
        atc_code, atc_naam = "", ""
        if " - " in atc_raw:
            atc_code, atc_naam = atc_raw.split(" - ", 1)
        else:
            atc_code = atc_raw

        rec = {
            "id": (row.get("REGISTRATIENUMMER") or "").strip(),
            "soort": (row.get("SOORT") or "").strip(),
            "naam": productnaam,
            "houder": (row.get("HANDELSVERGUNNINGHOUDER") or "").strip(),
            "afleverstatus": (row.get("AFLEVERSTATUS") or "").strip(),
            "vorm": (row.get("FARMACEUTISCHEVORM") or "").strip(),
            "toedieningsweg": (row.get("TOEDIENINGSWEG") or "").strip(),
            "atc_code": atc_code.strip(),
            "atc_naam": atc_naam.strip(),
            "werkzamestoffen": werkzamestoffen,
            "hulpstoffen": hulpstoffen,
            "smpc": (row.get("SMPC_FILENAAM") or "").strip(),
            "bijsluiter": (row.get("BIJSLUITER_FILENAAM") or "").strip(),
            "link": (row.get("PRODUCTDETAIL_LINK") or "").strip(),
        }
        records.append(rec)

print(f"Aantal producten verwerkt: {len(records)}")

freq = {}
for r in records:
    for h in r["hulpstoffen"]:
        freq[h] = freq.get(h, 0) + 1
hulpstoffen_index = sorted(freq.items(), key=lambda x: -x[1])
print(f"Aantal unieke hulpstoffen: {len(hulpstoffen_index)}")

with open("data.js", "w", encoding="utf-8") as f:
    f.write("window.MEDICIJNEN=" + json.dumps(records, ensure_ascii=False, separators=(",", ":")) + ";")

with open("hulpstoffen.js", "w", encoding="utf-8") as f:
    f.write("window.HULPSTOFFEN_INDEX=" + json.dumps(hulpstoffen_index, ensure_ascii=False, separators=(",", ":")) + ";")

now = datetime.datetime.now(datetime.timezone.utc)
gegenereerd_label = f"{now.day} {MAANDEN[now.month-1]} {now.year}"
meta = {
    "gegenereerd_iso": now.strftime("%Y-%m-%d"),
    "gegenereerd_label": gegenereerd_label,
    "aantal_producten": len(records),
    "aantal_hulpstoffen": len(hulpstoffen_index),
}
with open("meta.js", "w", encoding="utf-8") as f:
    f.write("window.CBG_META=" + json.dumps(meta, ensure_ascii=False) + ";")

print("data.js, hulpstoffen.js en meta.js zijn bijgewerkt.")
