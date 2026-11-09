"""Stream the Companies House BasicCompanyData CSV and keep companies whose
name (or previous name) shares its leading words with a member name, or whose
registered postcode is one of the member postcodes."""
import csv, io, json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(__file__)); from common import core, pcnorm
zpath, mpath, out = sys.argv[1:4]
mem = json.load(open(mpath))
pcs, heads = set(), set()
for m in mem:
    for p in m["postcodes"]: pcs.add(pcnorm(p))
    for n in [m["member"]] + m["trading_names"]:
        w = core(n).split()
        if w: heads.add(" ".join(w[:2]))
def head(n): return " ".join(core(n).split()[:2])
keep = []
with zipfile.ZipFile(zpath) as z:
    f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", errors="replace")
    r = csv.reader(f); hdr = [h.strip() for h in next(r)]; ix = {h: i for i, h in enumerate(hdr)}
    prev = [ix[f"PreviousName_{k}.CompanyName"] for k in range(1, 11) if f"PreviousName_{k}.CompanyName" in ix]
    for row in r:
        if len(row) < len(hdr): continue
        name = row[ix["CompanyName"]]; pc = pcnorm(row[ix["RegAddress.PostCode"]])
        pn = [row[i] for i in prev if row[i]]
        if pc in pcs or head(name) in heads or any(head(x) in heads for x in pn):
            keep.append({"name": name, "number": row[ix["CompanyNumber"]], "postcode": row[ix["RegAddress.PostCode"]],
                "town": row[ix["RegAddress.PostTown"]], "status": row[ix["CompanyStatus"]], "category": row[ix["CompanyCategory"]],
                "sic": [row[ix[f"SICCode.SicText_{k}"]] for k in range(1, 5) if row[ix[f"SICCode.SicText_{k}"]]], "previous_names": pn})
json.dump(keep, open(out, "w"))
print(len(keep), "candidate companies kept")
