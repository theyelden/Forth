# Who imports directly: Unitas and TWG members (pilot)

**Internal working note. Not for publication.** None of these numbers has been
checked against the forth-report-canon rules.

**Window:** HMRC importer details, Sep 2025 to Aug 2026 (12 months; Aug 2026 is the latest month published).
**Pilot codes:** HS 1509 (olive oil) and chapters 07, 08, 20 and 21. HMRC trader data has no values or volumes, so this shows only *whether* a member imported under a code, not how much.

## Direct importers per group

| | Unitas Wholesale | The Wholesale Group* |
|---|---|---|
| Members found (one per company, depots merged) | 135 | 73 |
| Outside HMRC coverage (Republic of Ireland, Jersey, Spain) | 3 | 3 |
| Imports anything directly: exact match | 60 | 25 |
| Imports anything directly: likely match (needs your check) | 19 | 6 |
| No direct import found | 53 | 39 |
| Imports at least one pilot code (exact + likely) | 31 | 13 |
| Imports olive oil (1509) | 5 | 3 |

\*TWG does not publish a full member list. Its "Where to buy" locator lists 79 locations it calls members (73 companies). The trade press reports about 225 members, so TWG figures cover about a third of the group.

Olive oil importers: Albion Fine Foods, John Mower & Co, Lioncroft Wholesale, Top Op Foods, Wanis (likely match), Extra Cash & Carry, Holland Bazaar, Foods of Europe. Nearly all import extra virgin oil (15092000).

## Most common pilot codes among member importers

Counted as the number of members importing under each code.

1. 21039090 Sauces, mixed condiments and seasonings: 22
2. 21069098 Food preparations n.e.s. (with milkfat/sugar): 20
3. 20059980 Other preserved vegetables (not in vinegar): 17
4. 20019097 Vegetables and fruit preserved in vinegar: 13
5. 20081999 Preserved nuts and seeds: 12
6. Joint 6th, 11 members each: 20089963 (preserved tropical fruit), 21041000 (soups), 07132000 (dried chickpeas), 07134000 (dried lentils), 21069092 (food preparations)

## 10 strongest targets for olive oil and preserved food

How I picked them: food or foodservice wholesalers in Great Britain, with an exact Companies House match. None has any import record under a pilot code in 12 months. I ranked by depot count from the groups' own listings. I have no turnover data, so treat the order as rough.

| # | Member (group) | Depots | Direct import record |
|---|---|---|---|
| 1 | Dhamecha Foods Ltd (Unitas) | 13 | Wine and spirits only |
| 2 | A G Parfett & Sons Ltd (Unitas) | 8 | EU wine and beer only |
| 3 | Friars Pride Ltd (Unitas) | 7 | Frozen fish and groundnut oil, but no olive oil |
| 4 | United Wholesale (Scotland) Ltd (Unitas) | 3 | Non-pilot goods only |
| 5 | United Wholesale Grocers Ltd (Unitas) | 3 | Drinks and bakery only |
| 6 | Thames Wholesalers Ltd (Unitas) | 1 | No direct import found |
| 7 | South Eastern Foods Ltd, t/a Bradleys (Unitas) | 1 | No direct import found |
| 8 | All Shires Foods (TWG) | 1 | No direct import found |
| 9 | J Kellett Foods (TWG) | 1 | No direct import found |
| 10 | Merlin Food Service (TWG) | 1 | No direct import found |

Numbers 1 to 5 already run their own import paperwork for other goods, but not for these food lines. Numbers 6 to 10 show no direct imports at all.

Next in line: Lion Catering, Premier Quality Foods, Youngs Foods, Anglia Culinary Suppliers, H N Nuttall, William Yule & Son, Stax Trade Centres.

**Left off on purpose:**
- Kitwave subsidiaries such as Westcountry Fruit Sales and M.J. Baker. Their parent, Kitwave Limited, imports pilot codes itself.
- Northern Ireland members. HMRC trader data leaves out NI imports from the EU, so "no direct import found" means little for them.

## Caveats

- "No direct import found" does not prove a member buys from UK suppliers. Traders can ask HMRC to withhold their details, and a customs agent or group company may be named on the declaration instead.
- The Companies House API key was rejected ("Invalid Authorization header"). I used the Companies House bulk register (snapshot of 1 Nov 2026) instead, which holds the same names, numbers and registered postcodes.
- The 25 likely matches and every uncertain candidate are in `review_matches.csv` for checking by hand.
