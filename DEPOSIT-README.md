# OAP device-record analysis: frozen data and reproducible figures

This package reproduces descriptive counts from frozen openFDA 510(k), openFDA UDI, and AccessGUDID history extracts for product code OAP. It contains the three input JSON files, a standard-library Python script, text and JSON results, tests, a data dictionary, and verification evidence. Author: Dominic Onwuamaegbu. Prepared as the data and code supplement to an article submitted to the Journal of Medical Device Regulation; see `CITATION.cff`.

## Sources and query URLs

| Input | Source / query | Pull date |
|---|---|---|
| `openfda-udi-oap-2026-09-24.json` | `https://api.fda.gov/device/udi.json?search=product_codes.code:OAP&limit=1000` | 2026-09-24 |
| `openfda-510k-oap-2026-09-24.json` | `https://api.fda.gov/device/510k.json?search=product_code:OAP&limit=1000` | 2026-09-24 (snapshot filename) |
| `accessgudid-history-oap-2026-09-29.json` | `https://accessgudid.nlm.nih.gov/api/v3/devices/history.json?di=<primary DI>` for each of the 151 primary DIs | 2026-09-29 |

The UDI query and both GUDID pull dates are recorded in the source README. The 510(k) query above is reconstructed from product code OAP and the stored `meta.results.limit = 1000`; its original request log and README were not supplied. It is a reproducible query specification, not a verified historical request URL. The AccessGUDID template is expanded in `SOURCE-QUERIES.txt`, one literal URL per DI. No API was refetched to build this package. Querying these URLs now may return different records.

## Input integrity

Hashes are SHA-256 over raw bytes, without newline normalization. Copies match the source files byte for byte.

| File under `data/` | SHA-256 | Provenance check |
|---|---|---|
| `openfda-udi-oap-2026-09-24.json` | `d5f41532ef6afeb6d1aaf76bd09c5fdf1ca17b906d63318db94713b1ca424ee3` | README match |
| `accessgudid-history-oap-2026-09-29.json` | `5a7bdc6c4e6ae70a3ad45b6145b82a5f4a09dcf69a3d0ddd9c6978b3a92f89b0` | README match |
| `openfda-510k-oap-2026-09-24.json` | `43a3e891e0b43e3e4445d8652c20951f088a86b6183cdb1dd0d114b1d699bb7a` | Observed only; prior README hash absent |

**Open provenance requirement:** no README exists in the supplied 510(k) snapshot directory, and no baseline hash for that file appears in the supplied data READMEs. Its observed hash is recorded for copy integrity only. A trusted historical hash and original request log must be supplied before claiming all three snapshots were verified against source READMEs. See `VERIFY.md`.

## AccessGUDID reduction

The source README states that the history endpoint was queried for every primary DI and each version's published XML was reduced to its date, submission numbers, and `premarketExempt`. The frozen JSON preserves version order in `versions`; `date`, `subs`, and `exempt` are the retained analytical values. It also contains version numbers and openFDA labeler/brand/submission/exemption context. Empty `subs` lists represent no retained submission numbers; exemption values remain strings in lists, not Python booleans.

The source README does not specify complete XML XPaths, namespace handling, whitespace normalization, or the XML extraction implementation. This package reproduces calculations from the reduced JSON; it cannot reconstruct the original published XML. The dictionary distinguishes retained JSON paths from unavailable XML mapping details.

## Analysis scope and interpretation

The 510(k) snapshot contains 112 records. The analysis excludes `K261253`, keeping the original scope and calculations unchanged. The script asserts that no UDI record cites the excluded number. Counts of applicants, labelers, and brands use distinct source strings without name normalization. `with number`, `exempt`, and `neither` follow their original independent predicates; the first two are not defined as mutually exclusive categories. A cited number absent from the retained OAP table is counted under `other codes` as in the original script; this is a lookup result, not an independent product-code validation.

The labeler/applicant classification is a **manual judgement**, recorded on 2026-09-29, not a verified corporate-ownership finding. Its fixed rule is: the three explicit `DIFFERENT_FIRM` pairs have applicant names judged not to be variants of labeler names; the four explicit `VARIANT` pairs are plausible matches with spelling or corporate-form differences; every other observed labeler/clearance pair is counted in the residual `same firm` category. Those exact sets are preserved in the script. The residual category does not independently establish corporate identity. One record may cite multiple clearances, so pair-weighted record counts need not mean distinct devices.

## Rerun offline

Verified with Python 3.12.10; no third-party dependencies are needed for the package script or its unittest suite. From this folder:

```text
python code/jmdr_figures.py
python code/jmdr_figures.py --json > figures.txt
python -m unittest discover -s tests -v
```

`--json` writes `figures.json` in the package root and leaves printed output unchanged. `figures.txt` is stdout captured as bytes on Windows; a shell may transcode redirected text. For an exact byte capture on any platform:

```text
python -c "import pathlib,subprocess,sys; pathlib.Path('figures.txt').write_bytes(subprocess.check_output([sys.executable,'code/jmdr_figures.py','--json']))"
```

The tests copy the entire package to a temporary standalone folder before executing it and compare all JSON metric names and values against independently parsed stdout. They also check the frozen input hashes and the exclusion. See `LICENSE-DATA.md` for data status and the unresolved code licence.
