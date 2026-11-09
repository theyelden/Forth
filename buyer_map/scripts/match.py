"""Match member entities -> Companies House -> HMRC importer records.
Writes buyer_map.csv, review_matches.csv and match_detail.json."""
import csv, json, os, sys
from collections import defaultdict
from rapidfuzz import fuzz
sys.path.insert(0, os.path.dirname(__file__)); from common import norm, core, pcnorm, outward, bare, acronym_hit
mpath, chpath, hpath, outdir = sys.argv[1:5]
mem = json.load(open(mpath)); ch = json.load(open(chpath)); hm = json.load(open(hpath))
IN_SCOPE = lambda c: c.startswith("1509") or c[:2] in ("07", "08", "20", "21")
GENERIC = {"FOODSERVICE","FOOD","FOODS","SERVICE","WHOLESALE","WHOLESALERS","CASH","CARRY","DRINKS","CATERING","SUPPLIES","DISTRIBUTION","SONS"}

# ---------- Companies House
ch_by_core = defaultdict(list); ch_by_pc = defaultdict(list)
for c in ch:
    for n in [c["name"]] + c["previous_names"]: ch_by_core[core(n)].append(c)
    ch_by_pc[pcnorm(c["postcode"])].append(c)
def ch_match(m):
    names = [m["member"]] + [t for t in m["trading_names"] if "(" not in t]
    pcs = {pcnorm(p) for p in m["postcodes"]}; outs = {outward(p) for p in m["postcodes"]}
    cands = {}
    for n in names:
        for c in ch_by_core.get(core(n), []): cands[c["number"]] = c
    for p in pcs:
        for c in ch_by_pc.get(p, []): cands[c["number"]] = c
    best = None
    for c in cands.values():
        allnames = [c["name"]] + c["previous_names"]
        sim = max(fuzz.token_sort_ratio(core(a), core(n)) for a in allnames for n in names)
        cur = core(c["name"]) in {core(n) for n in names}
        pc = pcnorm(c["postcode"]) in pcs; ow = outward(c["postcode"]) in outs
        acr = pc and any(acronym_hit(n, a) for n in names for a in allnames)
        sim = max(sim, max(fuzz.ratio(bare(a), bare(n)) for a in allnames for n in names))
        if sim < 75 and not (pc and sim >= 60) and not acr: continue
        if bare(c["name"]) in {bare(n) for n in names} or (cur and (pc or ow)): conf = "exact"
        elif sim == 100 or (sim >= 85 and (pc or ow)) or acr: conf = "likely"
        else: conf = "uncertain"
        closeness = max(fuzz.ratio(bare(c["name"]), bare(n)) for n in names) / 5
        score = sim + closeness + (30 if pc else 10 if ow else 0) + (5 if cur else 0) + (8 if c["status"] == "Active" else 0) + {"exact": 40, "likely": 20, "uncertain": 0}[conf]
        if best is None or score > best[0]: best = (score, conf, c)
    return (best[1], best[2]) if best else ("no match", None)

# ---------- HMRC
h_by_core = defaultdict(list); h_by_pc = defaultdict(list)
for k, t in hm.items():
    t["key"] = k; h_by_core[core(t["name"])].append(t); h_by_pc[pcnorm(t["postcode"])].append(t)
h_cores = list(h_by_core.keys())
from rapidfuzz import process
def hm_match(m, chc):
    names = {m["member"], *[t for t in m["trading_names"] if "(" not in t]}
    pcs = {pcnorm(p) for p in m["postcodes"]}
    if chc:
        names |= {chc["name"], *chc["previous_names"]}; pcs.add(pcnorm(chc["postcode"]))
    cores = {core(n) for n in names if core(n)}
    hits = {}
    def add(t, conf, why):
        r = {"exact": 3, "likely": 2, "uncertain": 1}
        if t["key"] not in hits or r[conf] > r[hits[t["key"]][1]]: hits[t["key"]] = (t, conf, why)
    for c in cores:
        for t in h_by_core.get(c, []):
            if pcnorm(t["postcode"]) in pcs: add(t, "exact", "same name, same postcode")
            elif len(c.split()) >= 2 or c.split()[0] not in GENERIC:
                add(t, "likely" if outward(t["postcode"]) in {outward(p) for p in pcs} else "uncertain", "same name, different postcode")
    depot_pcs = {pcnorm(p) for p in m["postcodes"]}
    for p in pcs:
        for t in h_by_pc.get(p, []):
            s = max(max(fuzz.token_set_ratio(core(t["name"]), c), fuzz.ratio(core(t["name"]).replace(" ", ""), c.replace(" ", ""))) for c in cores) if cores else 0
            if any(acronym_hit(n, t["name"]) for n in names): add(t, "likely", "same postcode, member name is the initials of this name")
            elif s >= 85: add(t, "likely", f"same postcode, similar name ({s:.0f})")
            elif s >= 60 and p in depot_pcs: add(t, "uncertain", f"same depot postcode, partly similar name ({s:.0f})")
    if m["parent"]:
        for t in h_by_core.get(core(m["parent"]), []) + h_by_core.get("KITWAVE", []):
            if t["key"] not in hits: hits[t["key"]] = (t, "uncertain", "parent company's own import record (" + m["parent"] + ") - imports may be booked here")
    return list(hits.values())

rows, review, detail = [], [], []
for m in mem:
    chconf, chc = ch_match(m)
    hits = [] if m["scope_note"].startswith(("Spain", "Republic", "Jersey")) else hm_match(m, chc)
    best = max((h[1] for h in hits), key=lambda x: {"exact": 3, "likely": 2, "uncertain": 1}[x], default="no match")
    counted = [h for h in hits if h[1] == best and best in ("exact", "likely")]
    own = {core(n) for n in [m["member"]] + m["trading_names"]}
    if best == "exact" and chconf != "exact" and not any(core(t["name"]) in own for t, _, _ in counted):
        best = "likely"   # found only through a Companies House name that is itself not certain
    codes, months = defaultdict(set), set()
    for t, _, _ in counted:
        months |= set(t["months"])
        for c, ms in t["codes"].items(): codes[c] |= set(ms)
    ins = sorted(c for c in codes if IN_SCOPE(c))
    oo = sorted(c for c in codes if c.startswith("1509"))
    if m["scope_note"].startswith(("Spain", "Republic", "Jersey")): status = "outside HMRC data coverage"
    elif best == "exact": status = "yes"
    elif best == "likely": status = "yes - to confirm"
    else: status = "no direct import found"
    conf = best if best in ("exact", "likely") else "no match"
    rows.append({"group": m["group"], "member": m["member"], "trading_names": "; ".join(m["trading_names"]),
        "parent": m["parent"], "member_postcodes": "; ".join(m["postcodes"]),
        "ch_company_number": chc["number"] if chc else "", "ch_registered_name": chc["name"] if chc else "",
        "ch_registered_postcode": chc["postcode"] if chc else "", "ch_status": chc["status"] if chc else "", "ch_match": chconf,
        "direct_importer": status, "match_confidence": conf,
        "hmrc_trader_names": "; ".join(sorted({t["name"] + " (" + t["postcode"] + ")" for t, _, _ in counted})),
        "any_import_months_seen": len(months),
        "pilot_codes": " ".join(ins), "pilot_code_count": len(ins),
        "pilot_code_months": " ".join(f"{c}:{len(codes[c])}" for c in ins),
        "pilot_months_seen": len(set().union(*[codes[c] for c in ins])) if ins else 0,
        "olive_oil_1509_codes": " ".join(oo),
        "all_codes_count": len(codes), "all_codes": " ".join(sorted(codes)), "coverage_note": m["scope_note"],
        "source_urls": " | ".join(m["source_urls"]), "member_list_retrieved": "; ".join(m["retrieved_utc"])})
    for t, c, why in hits:
        if c in ("likely", "uncertain") or chconf in ("likely", "uncertain") or best == "likely":
            if c == "exact" and chconf == "exact": continue
            if c == "exact": c = best
            review.append({"group": m["group"], "member": m["member"], "member_postcodes": "; ".join(m["postcodes"]),
                "ch_company_number": chc["number"] if chc else "", "ch_registered_name": chc["name"] if chc else "", "ch_match": chconf,
                "hmrc_name": t["name"], "hmrc_postcode": t["postcode"], "hmrc_address": t["address"], "match_confidence": c,
                "counted_in_buyer_map": "yes" if any(t is x[0] for x in counted) else "no", "reason": why,
                "pilot_codes": " ".join(sorted(x for x in t["codes"] if IN_SCOPE(x))), "months_seen": len(t["months"]),
                "your_verdict (Y/N)": ""})
    if chconf in ("likely", "uncertain") and not hits:
        review.append({"group": m["group"], "member": m["member"], "member_postcodes": "; ".join(m["postcodes"]),
            "ch_company_number": chc["number"], "ch_registered_name": chc["name"], "ch_match": chconf,
            "hmrc_name": "", "hmrc_postcode": "", "hmrc_address": "", "match_confidence": "", "counted_in_buyer_map": "",
            "reason": "Companies House match only - check company identity", "pilot_codes": "", "months_seen": "", "your_verdict (Y/N)": ""})
    detail.append({"member": m, "ch": chc, "ch_conf": chconf, "hits": [(t["key"], c, why) for t, c, why in hits]})
for fn, data in (("buyer_map.csv", rows), ("review_matches.csv", review)):
    with open(os.path.join(outdir, fn), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
json.dump(detail, open(os.path.join(outdir, "match_detail.json"), "w"), indent=1, default=str)
from collections import Counter
print(Counter((r["group"], r["direct_importer"]) for r in rows)); print(Counter(r["ch_match"] for r in rows)); print(len(review), "review rows")
