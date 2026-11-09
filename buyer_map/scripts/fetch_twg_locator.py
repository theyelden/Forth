"""Tile the UK with WP Store Locator store_search queries (the same public
endpoint thewholesalegroup.co.uk/where-to-buy/ calls) and save each raw reply."""
import json, os, sys, time, urllib.request, datetime
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
BASE = "https://thewholesalegroup.co.uk/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&max_results=50&search_radius={r}&autoload=0"
log = open(os.path.join(OUT, "DOWNLOAD_LOG.tsv"), "a")
seen = {}
def q(lat, lng, r):
    u = BASE.format(lat=round(lat,3), lng=round(lng,3), r=r)
    req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0","X-Requested-With":"XMLHttpRequest"})
    b = urllib.request.urlopen(req, timeout=60).read()
    fn = f"q_{lat:.3f}_{lng:.3f}_{r}.json"
    open(os.path.join(OUT, fn), "wb").write(b)
    log.write(f"{fn}\t{u}\t{datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ}\t{len(b)}\n"); log.flush()
    time.sleep(0.7)
    return json.loads(b) if b.strip() not in (b"", b"0") else []
def cell(lat, lng, dlat, dlng, r):
    d = q(lat, lng, r)
    for s in d: seen[s["id"]] = s
    if len(d) >= 50 and r > 5:   # saturated: split into 4
        for a in (-0.25, 0.25):
            for b in (-0.25, 0.25):
                cell(lat+a*dlat, lng+b*dlng, dlat/2, dlng/2, max(5, r//2))
lat = 49.9
while lat <= 61.0:
    lng = -8.5
    while lng <= 2.0:
        cell(lat, lng, 1.0, 1.6, 60); lng += 1.6
    lat += 1.0
json.dump(sorted(seen.values(), key=lambda s:int(s["id"])), open(os.path.join(OUT, "_merged_unique_stores.json"),"w"), indent=1)
print(len(seen), "unique stores")
