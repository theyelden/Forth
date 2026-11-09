"""members.csv (one row per listed location) -> member entities."""
import csv, json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__)); from common import norm, core, pcnorm
B = sys.argv[1]
OVERRIDE = {  # listed_name -> member name (depot/branch labels folded into the company)
    "A F Blakemore & Sons Ltd Fresh Foods": "A F Blakemore & Sons Ltd",
    "Holland Bazaar (Croydon)": "Holland Bazaar",
}
NON_UK = {  # outside the territory covered by HMRC trader data
    "JE": "Jersey (outside UK customs territory)", "GY": "Guernsey (outside UK customs territory)"}
mem = {}
for r in csv.DictReader(open(os.path.join(B, "members.csv"))):
    n = OVERRIDE.get(r["listed_name"], r["listed_name"])
    parent = ""
    m = re.search(r"\((Kitwave Wholesale Group)\)", n)
    if m: parent = "Kitwave Group plc"; n = n.replace(m.group(0), "").strip()
    n = re.sub(r"\s+[–-]\s+.*$", "", n)                           # "Musgrave – Cork"
    legal, trading = n, ""
    m = re.search(r"\((?:T/A)\s*([^)]*)\)?", n)
    if m: trading = m.group(1).strip(" /"); legal = n[:m.start()].strip()
    else:
        m = re.search(r"\s*\(([^)]*)\)$", n)
        if m and not re.search(r"(?i)wholesale|ltd|limited|midland", m.group(1)): legal = n[:m.start()].strip()  # depot label
        elif m and "Midland" in m.group(1): trading, legal = legal[:m.start()].strip(), m.group(1)   # "Q Mover (Midland Foodservice)"
    key = r["group"] + "|" + core(legal)
    e = mem.setdefault(key, {"group": r["group"], "member": legal, "trading_names": set(), "parent": parent,
                             "postcodes": [], "addresses": [], "source_urls": set(), "retrieved_utc": set(), "scope_note": ""})
    if trading: e["trading_names"].add(trading)
    if r["listed_name"] != legal: e["trading_names"].add(r["listed_name"])
    if r["postcode"] and pcnorm(r["postcode"]) not in [pcnorm(p) for p in e["postcodes"]]: e["postcodes"].append(r["postcode"])
    e["addresses"].append(r["address"]); e["source_urls"].add(r["source_url"]); e["retrieved_utc"].add(r["retrieved_utc"][:10])
    a = r["address"].upper()
    if r["country"] == "Spain": e["scope_note"] = "Spain - outside HMRC trader data"
    elif re.search(r"\b(DUBLIN|CO\. LIMERICK|IRELAND|CORK)\b", a) and not re.search(r"\bBT\d", a): e["scope_note"] = "Republic of Ireland - outside HMRC trader data"
    elif pcnorm(r["postcode"])[:2] in NON_UK: e["scope_note"] = NON_UK[pcnorm(r["postcode"])[:2]]
    elif re.search(r"\bBT\d", a): e["ni"] = True
for e in mem.values():
    e.setdefault("ni", False)
    e["trading_names"] = sorted(e["trading_names"]); e["source_urls"] = sorted(e["source_urls"]); e["retrieved_utc"] = sorted(e["retrieved_utc"])
    if not e["scope_note"] and (e.pop("ni", False) or any(pcnorm(p).startswith("BT") for p in e["postcodes"])):
        e["scope_note"] = "Northern Ireland - HMRC trader data omits NI imports from the EU"
json.dump(list(mem.values()), open(sys.argv[2], "w"), indent=1)
from collections import Counter
print(Counter(e["group"] for e in mem.values()))
for e in mem.values(): print(e["group"][:5], "|", e["member"], "|", e["trading_names"][:3], "|", e["postcodes"][:3], "|", e["scope_note"])
