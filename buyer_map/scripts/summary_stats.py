"""Counts for the summary: per-group status, top pilot codes, target shortlist inputs."""
import csv, json, re, sys
from collections import Counter, defaultdict
bm, members_csv, smka = sys.argv[1:4]
desc = {}
for line in open(smka, encoding="latin-1"):
    f = line.rstrip("\n").split("|")
    if len(f) > 26 and re.fullmatch(r"\d{9}", f[0]): desc[f[0][:8]] = f[-1].strip()
rows = list(csv.DictReader(open(bm)))
depots = Counter((r["group"], r["listed_name"]) for r in csv.DictReader(open(members_csv)))
svc = defaultdict(set)
for r in csv.DictReader(open(members_csv)):
    for s in r["services"].split("; "): svc[r["group"]].add(s)
for g in ("Unitas Wholesale", "The Wholesale Group"):
    gr = [r for r in rows if r["group"] == g]
    c = Counter(r["direct_importer"] for r in gr)
    imp = [r for r in gr if r["direct_importer"].startswith("yes")]
    print(f"\n== {g}: {len(gr)} members; {dict(c)}")
    print("  importers with any pilot code:", sum(1 for r in imp if r["pilot_codes"]), "| with 1509:", sum(1 for r in imp if r["olive_oil_1509_codes"]))
    print("  exact-only: yes", c["yes"], "; any pilot (exact only):", sum(1 for r in gr if r["direct_importer"] == "yes" and r["pilot_codes"]))
cc = Counter(); who = defaultdict(list)
for r in rows:
    if r["direct_importer"].startswith("yes"):
        for code in r["pilot_codes"].split():
            cc[code] += 1; who[code].append(r["member"])
print("\n== top pilot codes by number of member importers (both groups, exact+likely)")
for code, n in cc.most_common(15): print(n, code, desc.get(code, "?")[:90])
ch = Counter()
for code, n in cc.items(): ch[code[:4] if code.startswith("1509") else code[:2]] += 0
print("\n== olive oil importers:")
for r in rows:
    if r["olive_oil_1509_codes"]: print(" ", r["group"][:5], r["member"], r["direct_importer"], r["olive_oil_1509_codes"])
print("\n== no pilot-code imports, in coverage")
for r in rows:
    if r["coverage_note"].startswith(("Spain", "Republic", "Jersey")): continue
    if r["pilot_codes"]: continue
    print(f"  {r['group'][:5]} | {r['member'][:40]} | {r['direct_importer'][:14]} | any_codes={r['all_codes_count']} | sic={r['ch_status'][:6]} | {r['coverage_note'][:12]}")
