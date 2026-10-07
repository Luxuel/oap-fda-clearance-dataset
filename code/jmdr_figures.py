"""Recompute figures from the three frozen JSON files in this package.

Run from the package root: python code/jmdr_figures.py [--json]
--json additionally writes figures.json; stdout is unchanged.
"""
import argparse
import collections
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--json', action='store_true', help='write figures.json in the package root')
args = parser.parse_args()

ROOT = Path(__file__).resolve().parent.parent
udi = json.loads((ROOT / "data/openfda-udi-oap-2026-09-24.json").read_text("utf-8"))["results"]
k510 = json.loads((ROOT / "data/openfda-510k-oap-2026-09-24.json").read_text("utf-8"))["results"]
hist = json.loads((ROOT / "data/accessgudid-history-oap-2026-09-29.json").read_text("utf-8"))

# K261253 is excluded under the analysis scope fixed on 2026-09-24.
# No GUDID record cites it, so no GUDID figure changes.
EXCLUDED = {"K261253"}
assert not any(s.get("submission_number") in EXCLUDED for r in udi for s in r.get("premarket_submissions", []))
k510 = [r for r in k510 if r["k_number"] not in EXCLUDED]
oap = {r["k_number"]: r for r in k510}
dates = sorted(r["decision_date"] for r in k510)
print(f"510(k): {len(k510)} clearances, {len({r['applicant'] for r in k510})} applicants, {dates[0]} to {dates[-1]}")
print(f"GUDID: {len(udi)} records, {len({r['company_name'] for r in udi})} labelers, {len({r['brand_name'] for r in udi})} brand names")


def subs(rec):
    return [s["submission_number"] for s in rec.get("premarket_submissions", []) if s.get("submission_number")]


with_num = [r for r in udi if subs(r)]
exempt = [r for r in udi if r["is_pm_exempt"] == "true"]
neither = [r for r in udi if not subs(r) and r["is_pm_exempt"] != "true"]
print(f"with number {len(with_num)}, exempt {len(exempt)}, neither {len(neither)}")

# openFDA vs AccessGUDID latest published version
mismatch = 0
for r in udi:
    di = next(i["id"] for i in r["identifiers"] if i["type"] == "Primary")
    last = hist[di]["versions"][-1]
    if sorted(last["subs"]) != sorted(subs(r)) or last["exempt"] != [r["is_pm_exempt"]]:
        mismatch += 1
print(f"openFDA vs AccessGUDID latest version: {mismatch} mismatches of {len(udi)}")

# version history of the submission-number field
multi = changed = lost_now = lost_regained = gained = 0
same_day = collections.Counter()
for di, h in hist.items():
    v = h["versions"]
    had = [bool(x["subs"]) for x in v]
    multi += len(v) > 1
    changed += len({tuple(sorted(x["subs"])) for x in v}) > 1
    if not had[-1] and any(had):
        lost_now += 1
        for a, b in zip(v, v[1:]):
            if a["subs"] and not b["subs"]:
                same_day[(b["date"], h["company"])] += 1
    if had[-1] and any(a and not b for a, b in zip(had, had[1:])):
        lost_regained += 1
    if had[-1] and not had[0]:
        gained += 1
print(f"multi-version {multi}; submission field changed {changed}; lost and still missing {lost_now}; "
      f"lost then regained {lost_regained}; first version lacked, now present {gained}")
by_date = collections.defaultdict(list)
for (d, co), n in same_day.items():
    by_date[d].append((co, n))
for d, rows in sorted(by_date.items()):
    print(f"  loss published {d}: {sum(n for _, n in rows)} records, {len(rows)} labeler(s)")

# which clearances GUDID cites
cited = collections.Counter(s for r in udi for s in subs(r))
in_oap = [s for s in cited if s in oap]
print(f"distinct submissions cited {len(cited)}; OAP {len(in_oap)}; other codes {len(cited) - len(in_oap)}; "
      f"OAP clearances cited by no GUDID record {len(oap) - len(in_oap)}")

# labeler vs applicant pairs (classification is a documented manual judgement)
pairs = collections.Counter()
for r in udi:
    for s in subs(r):
        pairs[(r["company_name"], s)] += 1
print(f"distinct labeler-clearance pairs {len(pairs)}")
DIFFERENT_FIRM = {  # hand-checked 2026-09-29; applicant name is not a variant of the labeler name
    ("BLISSCO MEDICAL DEVICE LIMITED", "K192627"),
    ("Revian, Inc.", "K173729"),
    ("Xtrallux, LLC", "K230134"),
}
VARIANT = {  # plausible same firm, spelling or corporate-form difference; needs a documented rule
    ("Shang Far Biotechnology Co.", "K192627"),
    ("Shenzhen Slinph Technology Co., Ltd.", "K162782"),
    ("Hubei YJT Intelligent Technology Group Co., Ltd.", "K232356"),
    ("Foreo AB", "K242747"),
}
print(f"  different firm {len(DIFFERENT_FIRM)} pairs / {sum(pairs[p] for p in DIFFERENT_FIRM)} records; "
      f"variant {len(VARIANT)}; same firm {len(pairs) - len(DIFFERENT_FIRM) - len(VARIANT)}")


if args.json:
    figures = {
        "clearances": len(k510),
        "applicants": len({r["applicant"] for r in k510}),
        "decision_date_first": dates[0],
        "decision_date_last": dates[-1],
        "gudid_records": len(udi),
        "labelers": len({r["company_name"] for r in udi}),
        "brand_names": len({r["brand_name"] for r in udi}),
        "with_submission_number": len(with_num),
        "premarket_exempt": len(exempt),
        "neither_number_nor_exemption": len(neither),
        "latest_version_mismatches": mismatch,
        "latest_version_records_compared": len(udi),
        "multi_version_records": multi,
        "submission_field_changed": changed,
        "lost_and_still_missing": lost_now,
        "lost_then_regained": lost_regained,
        "first_version_lacked_now_present": gained,
        "loss_published": {
            d: {"records": sum(n for _, n in rows), "labelers": len(rows)}
            for d, rows in sorted(by_date.items())
        },
        "distinct_submissions_cited": len(cited),
        "oap_submissions_cited": len(in_oap),
        "other_code_submissions_cited": len(cited) - len(in_oap),
        "oap_clearances_not_cited": len(oap) - len(in_oap),
        "labeler_clearance_pairs": len(pairs),
        "different_firm_pairs": len(DIFFERENT_FIRM),
        "different_firm_records": sum(pairs[p] for p in DIFFERENT_FIRM),
        "variant_pairs": len(VARIANT),
        "same_firm_pairs": len(pairs) - len(DIFFERENT_FIRM) - len(VARIANT),
    }
    (ROOT / "figures.json").write_text(json.dumps(figures, indent=2) + "\n", encoding="utf-8")
