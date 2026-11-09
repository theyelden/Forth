"""Read HMRC 'Importer details' monthly files -> one JSON index of traders.
Layout per row: month, row_seq, name, addr1..addr5, postcode, then 8-digit CN codes."""
import glob, json, os, re, sys
src, out = sys.argv[1], sys.argv[2]
MONTHS = [f"{y}{m:02d}" for y, m in [(2025,9),(2025,10),(2025,11),(2025,12)] + [(2026,i) for i in range(1,9)]]
tr = {}
for f in sorted(glob.glob(os.path.join(src, "importers*.txt"))):
    for line in open(f, encoding="latin-1"):
        c = line.rstrip("\r\n").split("\t")
        if len(c) < 10 or c[0] not in MONTHS: continue
        name = c[2].strip(); pc = c[8].strip().upper()
        addr = ", ".join(x.strip().strip('"\'') for x in c[3:8] if x.strip())
        key = name + "|" + pc
        t = tr.setdefault(key, {"name": name, "postcode": pc, "address": addr, "codes": {}, "months": []})
        if c[0] not in t["months"]: t["months"].append(c[0])
        for code in c[9:]:
            code = code.strip()
            if re.fullmatch(r"\d{8}", code): t["codes"].setdefault(code, [])
            if re.fullmatch(r"\d{8}", code) and c[0] not in t["codes"][code]: t["codes"][code].append(c[0])
json.dump(tr, open(out, "w"))
print(len(tr), "trader name+postcode keys across", len(MONTHS), "months")
