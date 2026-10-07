# Product code OAP: FDA 510(k) clearance records and brand disclosure audit

Frozen public extracts and analysis code for US FDA product code OAP ("Laser, Comb, Hair", 21 CFR 890.5500), plus a companion audit of what consumer brands publish about their own clearance.

- Dataset (DOI): https://doi.org/10.5281/zenodo.23103200
- Report: https://luxuel.com/pages/at-home-laser-device-transparency-report
- Maintainer: Dominic Onwuamaegbu, founder of Luxuel (luxuel.com)

## Competing interest

The maintainer founded Luxuel, which sells a device in this product code. The clearance it is sold under is excluded from the dataset analysis, and Luxuel's own rows are excluded from every competitor count in the report. The report contains no efficacy ranking.

## What is in the data

openFDA 510(k) records (report v1.1 figures)
- 112 clearance records under product code OAP
- Decision dates from 18 January 2007 to 17 July 2026
- 59 distinct applicants
- 43 records dated 2021 or later; 22 dated 2024 or later
- 97 Traditional 510(k) and 15 Special 510(k)
- A clearance record is not a product: one clearance can cover several models, and counting records is not counting devices.

Brand disclosure audit (report v1.1)
- 24 consumer brands checked on their own websites (product page, FDA or clearance page, site search); first checked 19-22 August 2026, re-checked 16 September 2026
- 3 of the 24 published a specific 510(k) number
- 46 competitor product rows checked; 41 had no published number
- This is a disclosure finding, not a clearance finding. A brand that does not print its number may still hold one.

Zenodo deposit contents (v1.0, 2 October 2026)
- openFDA 510(k) records for the product code (snapshot pulled 24 September 2026)
- openFDA UDI (GUDID) records listing the code (151 records, pulled 24 September 2026)
- AccessGUDID published version history for each primary device identifier (pulled 29 September 2026), reduced to publication date, premarket submission numbers and exemption flag
- SHA-256 hashes, per-record query URLs, a data dictionary, verification notes and tests

Note on dates: the report page records an openFDA snapshot taken 16 September 2026 (identical to a first snapshot of 21 August 2026); the Zenodo deposit records its own pulls on 24 and 29 September 2026. Both pulls return the same 112 K-numbers and decision dates (checked 2026-10-07). Use the dates stated in each source.

## Method

- Source: the openFDA device 510(k) endpoint, queried for product_code:OAP.
- Build check: the build fails rather than publishes if the returned record count does not equal the total the API reports.
- Freezing: results are written to a dated file and a SHA-256 hash is recorded. Every figure is computed from the frozen file, not a live call.
- Reproduction: a standard-library Python script recomputes every descriptive figure.
- Applicant means the entity that filed the 510(k), which is often not the consumer brand. Applicant geography is omitted for all records.

## Limitations

- The 24 brands are a working census, not the whole market.
- A website audit is a point-in-time observation.
- Some audited devices may sit under a product code other than OAP.
- Counts are clearance records, not products, and are not an efficacy or quality signal.

## Licence

- Source data: US public-domain government records
- Code: MIT
- Documentation and derived results: CC BY 4.0

## How to cite

Luxuel. (2026). The 2026 At-Home Laser Hair Device Transparency Report (Version 1.1) [Data set]. Brand-site audit 16 September 2026; openFDA snapshot 16 September 2026. https://luxuel.com/pages/at-home-laser-device-transparency-report

Dataset: Onwuamaegbu, D. (2026). Product code OAP device records: frozen openFDA 510(k), openFDA UDI and AccessGUDID history extracts with reproducible figures (v1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23103200

## Repository layout

- `data/` the three frozen JSON extracts exactly as deposited on Zenodo (SHA-256 in `MANIFEST-SHA256.txt`)
- `code/` and `tests/` the standard-library script and tests
- `DEPOSIT-README.md` the original deposit README (provenance notes and verification status)
- `LICENSE` CC BY 4.0 (documentation and derived results); `LICENSE-CODE-MIT` MIT (code); `LICENSE-DATA.md` data status
