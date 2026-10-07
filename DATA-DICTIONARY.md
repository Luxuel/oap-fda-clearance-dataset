# Data dictionary

Paths below use `[]` for array elements and `<DI>` for a primary-DI object key. Strings are used exactly as stored unless a specific sorting/filtering rule is stated. Input files retain additional public-record fields; the table enumerates every field read by the calculation script, plus provenance/context fields discussed in the documentation.

| Input / field | Source field path in frozen file | Type / use |
|---|---|---|
| 510(k) result array | `results[]` | Array; scope before exclusion |
| Clearance number | `results[].k_number` | String; exclusion, table key, citation lookup |
| Applicant | `results[].applicant` | String; distinct applicants; manual judgement context |
| Decision date | `results[].decision_date` | ISO date string; sorted minimum/maximum |
| Product code (provenance) | `results[].product_code` | String; OAP snapshot selection, not recalculated |
| Query limit (provenance) | `meta.results.limit` | Integer; query specification |
| Total (provenance) | `meta.results.total` | Integer; reported source total |
| Snapshot update (provenance) | `meta.last_updated` | String; source update date, not pull date |
| UDI result array | `results[]` | Array; UDI denominator |
| Labeler | `results[].company_name` | String; distinct labelers and pair grouping |
| Brand | `results[].brand_name` | String; distinct brands |
| Exempt flag | `results[].is_pm_exempt` | String; only literal `true` satisfies exempt predicate |
| Submission list | `results[].premarket_submissions[]` | Optional array, defaults to empty |
| Submission number | `results[].premarket_submissions[].submission_number` | String; truthy entries retained; exclusion assertion checks original entries |
| Identifier list | `results[].identifiers[]` | Array; primary-DI lookup |
| Identifier type | `results[].identifiers[].type` | String; first literal `Primary` selected |
| Identifier value | `results[].identifiers[].id` | String; key into history object |
| History DI | `<DI>` (top-level object key) | String; joins UDI to AccessGUDID history |
| History labeler | `<DI>.company` | String; groups loss events by date and labeler; openFDA context |
| Version list | `<DI>.versions[]` | Ordered array; last element treated as latest; order preserved |
| Published date | `<DI>.versions[].date` | String; loss-event grouping; reduced published-version date |
| Historical submissions | `<DI>.versions[].subs[]` | Strings; reduced published-XML submission numbers; sorted for equality; list truthiness for transitions |
| Historical exemption | `<DI>.versions[].exempt[]` | Strings; reduced published-XML `premarketExempt`; compared to one-element list of UDI flag |
| Version number (context only) | `<DI>.versions[].v` | Integer; retained, not used in calculations |
| History brand (context only) | `<DI>.brand` | String; openFDA `results[].brand_name` context |
| Original submissions (context only) | `<DI>.openfda_subs[]` | Strings; openFDA submission-number context |
| Original exemption (context only) | `<DI>.openfda_exempt` | String; openFDA exemption context |

The AccessGUDID source README supplies the reduction rule (published date, submission numbers, `premarketExempt`), but not full original XML XPaths or namespace/extraction code. The retained JSON paths above are exact; unavailable XML mappings have not been invented.

## Output fields

`figures.txt` is unchanged human-readable stdout. `figures.json` uses these named keys; counts are integers and dates are ISO strings.

| JSON keys | Printed figures / definition |
|---|---|
| `clearances`, `applicants`, `decision_date_first`, `decision_date_last` | First line; retained 510(k) counts and decision-date range |
| `gudid_records`, `labelers`, `brand_names` | Second line; UDI counts |
| `with_submission_number`, `premarket_exempt`, `neither_number_nor_exemption` | Third line; original predicates |
| `latest_version_mismatches`, `latest_version_records_compared` | Latest-history comparison numerator and denominator |
| `multi_version_records`, `submission_field_changed`, `lost_and_still_missing`, `lost_then_regained`, `first_version_lacked_now_present` | Version-history summary; consecutive versions checked for loss/regain |
| `loss_published.<date>.records`, `loss_published.<date>.labelers` | Each printed loss date and its counts; loss transitions for records still missing a number, grouped by date/company |
| `distinct_submissions_cited`, `oap_submissions_cited`, `other_code_submissions_cited`, `oap_clearances_not_cited` | Distinct cited-number membership counts |
| `labeler_clearance_pairs` | Distinct `(company_name, submission_number)` pairs |
| `different_firm_pairs`, `different_firm_records`, `variant_pairs`, `same_firm_pairs` | Fixed manual classification and residual count |

## Analysis constants

`EXCLUDED = {K261253}` fixes the analysis scope. `DIFFERENT_FIRM` and `VARIANT` are the explicit manual pair sets in `code/jmdr_figures.py`; they are judgements rather than source fields. The spelling/corporate-form rule and residual handling are described in `README.md`.
