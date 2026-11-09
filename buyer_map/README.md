# buyer_map: which buying-group members import directly

Pilot: Unitas Wholesale and The Wholesale Group (TWG) members, matched against
HMRC importer details for Sep 2025 to Aug 2026. Results are in `SUMMARY.md`.
Internal only, not for publication.

## Files

| File | What it is |
|---|---|
| `members.csv` | One row per listed depot/location, with source URL and retrieval time |
| `buyer_map.csv` | One row per member company (depots merged) |
| `review_matches.csv` | Every likely or uncertain match, for checking by hand (fill in `your_verdict (Y/N)`) |
| `SUMMARY.md` | Half-page summary and target list |
| `raw/` | Untouched downloads, each folder with a `DOWNLOAD_LOG.tsv` (URL, UTC time, bytes, sha256) |
| `derived/` | Intermediate files: member entities, matched Companies House rows, per-member match detail |
| `scripts/` | Everything needed to rebuild the outputs |

### buyer_map.csv columns

- `direct_importer`:
  - `yes`: exact match
  - `yes - to confirm`: likely match
  - `no direct import found`
  - `outside HMRC data coverage`: Republic of Ireland, Jersey or Spain
- `match_confidence`: `exact`, `likely` or `no match`.
- `pilot_codes`: 8-digit codes under 1509, 07, 08, 20 or 21 seen in the 12 months.
- `pilot_code_months`: for each pilot code, the number of months it was seen.
- `pilot_months_seen`: months with at least one pilot code.
- `any_import_months_seen`: months with any import at all.
- `all_codes`: every code imported, in or out of the pilot.
- `ch_*`: Companies House company number, registered name, registered postcode, status and match strength.
- `coverage_note`: flags Northern Ireland members, because HMRC trader data omits NI imports from the EU.

## Sources and access route

**Member lists**

- **Unitas.** The public "Find a local Wholesaler" pages: <https://unitaswholesale.co.uk/retailer/wholesaler-search-2/>, pages 1 to 53. That gives 265 depots and 135 companies.
- **TWG.** No full member list is public. I used the "Where to buy" own-brand locator at <https://thewholesalegroup.co.uk/where-to-buy/>, which says it shows members. Its store list came from the site's public `wp-json/wp/v2/wpsl_stores` listing, plus the locator's own `store_search` calls for addresses. That gives 79 locations and 73 companies. The trade press reports about 225 TWG members, so this list is partial.
- Both lists were retrieved on 2026-11-09.

**HMRC trader data**

uktradeinfo offers two routes:

1. The OData API at <https://api.uktradeinfo.com>, using its `Trader` and `Import` entities. It is open, limited to 60 requests a minute, and returns at most 40,000 rows per response.
2. Monthly bulk "Importer details" ZIP files, listed on <https://www.uktradeinfo.com/trade-data/latest-bulk-data-sets/> and in its archive.

**I used the bulk files.** They are complete, raw and easy to archive: `importers2608.zip` plus the `jul-dec25`, `jan-jun26` and `jul-dec26` archives, downloaded 2026-11-09. I used the API only to confirm that Aug 2026 is the latest month. Code descriptions come from the SMKA12 control file for Aug 2026.

**Companies House**

The API key saved for this session was refused with "Invalid Authorization header". Companies House expects HTTP basic auth, with the key as the username and an empty password. I used the free bulk register instead: `BasicCompanyDataAsOneFile-2026-11-01.zip` from <https://download.companieshouse.gov.uk/en_output.html>, downloaded 2026-11-09. The file is 495 MB, so it is not committed; its URL and sha256 are in `raw/companies_house/DOWNLOAD_LOG.tsv`. The matched rows are kept in `derived/ch_matched_companies.json`.

## Matching rules

**Member to Companies House.** Names are normalised (case, punctuation, "Ltd/Limited", "&/and", initials). The match is:

- `exact`: the registered name is the same, or the same core name sits at a depot postcode or outward code.
- `likely`: the name is the same elsewhere, or very close at a matching postcode, or the member name is the initials of the registered name at the same postcode.
- `uncertain`: weaker than that.

**Member to HMRC trader.** The search covers the member's listed name, its trading names, and its Companies House current and previous names. It checks every depot postcode plus the registered-office postcode.

- `exact`: the same core name at one of those postcodes.
- `likely`: the same core name at a different postcode in the same outward code; a very close name at the same postcode; an initials match at the same postcode; or a hit found only through a Companies House name that is not itself an exact match.
- `uncertain`: shown in the review sheet but not counted. This covers:
  - the same name somewhere else;
  - a partly similar name at a depot postcode;
  - a parent company's own record (Kitwave).

## Rules followed

- No values or volumes are estimated. HMRC trader data has none.
- Absence is labelled "no direct import found", never as evidence of how a member buys.
- Nothing has been published. Any figure headed for a Forth publication needs a forth-report-canon check first.

## Re-run

Paths below are examples. The HMRC text files are extracted from the ZIPs into a scratch folder first.

```
python3 -I scripts/build_members.py .
python3 -I scripts/collapse_members.py . derived/member_entities.json
python3 -I scripts/hmrc_index.py <dir with importersYYMM.txt> <scratch>/hmrc_index.json
python3 -I scripts/ch_candidates.py <BasicCompanyDataAsOneFile zip> derived/member_entities.json <scratch>/ch_candidates.json
python3 -I scripts/match.py derived/member_entities.json <scratch>/ch_candidates.json <scratch>/hmrc_index.json <outdir>
python3 -I scripts/summary_stats.py buyer_map.csv members.csv <SMKA12 txt>
```

Requires `rapidfuzz`. `scripts/fetch_twg_locator.py` re-tiles the TWG locator.
