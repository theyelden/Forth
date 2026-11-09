"""Parse saved member pages into members.csv (one row per listed location)."""
import csv, glob, html, json, os, re, sys
B = sys.argv[1]; RAW = os.path.join(B, "raw", "member_pages")
PC = re.compile(r"\b([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})\b")
def clean(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
def logmap(path):
    out = {}
    for r in csv.DictReader(open(path), delimiter="\t"): out[r["file"]] = r
    return out
rows = []
# ---- Unitas
ul = logmap(os.path.join(RAW, "unitas", "DOWNLOAD_LOG.tsv"))
for f in sorted(glob.glob(os.path.join(RAW, "unitas", "page_*.html"))):
    t = open(f, encoding="utf-8").read(); meta = ul[os.path.basename(f)]
    for blk in re.findall(r'<div class="wholesaler-search-lg">(.*?)<div class="wholesaler-search-sm">', t, re.S):
        name = clean(re.search(r"<h3>(.*?)</h3>", blk, re.S).group(1))
        site = re.search(r'<h3>\s*<a href="([^"]+)"', blk)
        c = re.search(r"<h4>Contact:</h4>(.*?)</li>", blk, re.S)
        lines = [clean(x) for x in re.split(r"<br\s*/?>", c.group(1))] if c else []
        lines = [l for l in lines if l and not l.lower().startswith(("tel", "fax", "email"))]
        addr = ", ".join(lines)
        m = PC.search(addr.upper()); pc = f"{m.group(1)} {m.group(2)}" if m else ""
        svc = re.search(r"Services & Categories:</h4>\s*<p>(.*?)</p>", blk, re.S)
        rows.append(dict(group="Unitas Wholesale", listed_name=name, address=addr, postcode=pc,
            country="UK", services="; ".join(clean(x) for x in re.split(r"<br\s*/?>", svc.group(1)) if clean(x)) if svc else "",
            website=site.group(1) if site else "", source_url=meta["source_url"], retrieved_utc=meta["downloaded_utc"], source_note=""))
# ---- TWG
tl = logmap(os.path.join(RAW, "twg", "DOWNLOAD_LOG.tsv"))
cats = {c["id"]: c["name"] for c in json.load(open(os.path.join(RAW, "twg", "rest_wpsl_store_category.json")))}
rest = {s["id"]: s for s in json.load(open(os.path.join(RAW, "twg", "rest_wpsl_stores.json")))}
tiles = {int(s["id"]): s for s in json.load(open(os.path.join(RAW, "twg", "store_search_tiles", "_merged_unique_stores.json")))}
meta = tl["rest_wpsl_stores.json"]
for sid, s in sorted(rest.items()):
    loc = tiles.get(sid, {})
    country = loc.get("country") or ("Spain" if 8 in s["wpsl_store_category"] else "")
    addr = ", ".join(clean(x) for x in [loc.get("address",""), loc.get("address2",""), loc.get("city",""), loc.get("zip","")] if x)
    zp = (loc.get("zip") or "").upper(); m = PC.search(zp)
    rows.append(dict(group="The Wholesale Group", listed_name=clean(s["title"]["rendered"]), address=addr,
        postcode=f"{m.group(1)} {m.group(2)}" if m else zp, country=country,
        services="; ".join(cats.get(c, str(c)) for c in s["wpsl_store_category"]),
        website=loc.get("url",""), source_url="https://thewholesalegroup.co.uk/where-to-buy/ (data: " + meta["source_url"] + " + store_search tiles)",
        retrieved_utc=meta["downloaded_utc"], source_note="TWG 'Where to buy' own-brand locator; page says it shows members; partial member list"))
fields = list(rows[0].keys())
with open(os.path.join(B, "members.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r["group"] for r in rows)); print(sum(1 for r in rows if not r["postcode"]), "rows without postcode")
