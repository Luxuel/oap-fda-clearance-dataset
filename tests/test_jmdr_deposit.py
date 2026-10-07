"""Offline deposit checks; run with unittest or pytest, without repo inputs."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / 'code/jmdr_figures.py').is_file():
    ROOT = ROOT / 'Luxuel/data/jmdr-deposit-2026-10'

HASHES = {
    'openfda-udi-oap-2026-09-24.json': 'd5f41532ef6afeb6d1aaf76bd09c5fdf1ca17b906d63318db94713b1ca424ee3',
    'accessgudid-history-oap-2026-09-29.json': '5a7bdc6c4e6ae70a3ad45b6145b82a5f4a09dcf69a3d0ddd9c6978b3a92f89b0',
    # Observed copy-integrity baseline only: source README hash unavailable.
    'openfda-510k-oap-2026-09-24.json': '43a3e891e0b43e3e4445d8652c20951f088a86b6183cdb1dd0d114b1d699bb7a',
}


def parse_figures(text):
    """Independently map the complete original print format to typed metrics."""
    patterns = [
        (r'510\(k\): (\d+) clearances, (\d+) applicants, (\S+) to (\S+)',
         ['clearances', 'applicants', 'decision_date_first', 'decision_date_last']),
        (r'GUDID: (\d+) records, (\d+) labelers, (\d+) brand names',
         ['gudid_records', 'labelers', 'brand_names']),
        (r'with number (\d+), exempt (\d+), neither (\d+)',
         ['with_submission_number', 'premarket_exempt', 'neither_number_nor_exemption']),
        (r'openFDA vs AccessGUDID latest version: (\d+) mismatches of (\d+)',
         ['latest_version_mismatches', 'latest_version_records_compared']),
        (r'multi-version (\d+); submission field changed (\d+); lost and still missing (\d+); lost then regained (\d+); first version lacked, now present (\d+)',
         ['multi_version_records', 'submission_field_changed', 'lost_and_still_missing', 'lost_then_regained', 'first_version_lacked_now_present']),
        (r'distinct submissions cited (\d+); OAP (\d+); other codes (\d+); OAP clearances cited by no GUDID record (\d+)',
         ['distinct_submissions_cited', 'oap_submissions_cited', 'other_code_submissions_cited', 'oap_clearances_not_cited']),
        (r'distinct labeler-clearance pairs (\d+)', ['labeler_clearance_pairs']),
        (r'  different firm (\d+) pairs / (\d+) records; variant (\d+); same firm (\d+)',
         ['different_firm_pairs', 'different_firm_records', 'variant_pairs', 'same_firm_pairs']),
    ]
    metrics = {'loss_published': {}}
    seen = set()
    for line in text.splitlines():
        loss = re.fullmatch(r'  loss published (\S+): (\d+) records, (\d+) labeler\(s\)', line)
        if loss:
            date, records, labelers = loss.groups()
            if date in metrics['loss_published']:
                raise AssertionError('duplicate loss date')
            metrics['loss_published'][date] = {'records': int(records), 'labelers': int(labelers)}
            continue
        for i, (pattern, keys) in enumerate(patterns):
            match = re.fullmatch(pattern, line)
            if match:
                if i in seen:
                    raise AssertionError('duplicate metric line')
                seen.add(i)
                for key, value in zip(keys, match.groups()):
                    metrics[key] = value if key.startswith('decision_date_') else int(value)
                break
        else:
            raise AssertionError(f'unmapped output: {line!r}')
    if seen != set(range(len(patterns))):
        raise AssertionError('missing printed metrics')
    return metrics


class DepositTests(unittest.TestCase):
    def test_input_hashes(self):
        for name, expected in HASHES.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((ROOT / 'data' / name).read_bytes()).hexdigest(), expected)

    def test_saved_json_covers_every_printed_figure(self):
        parsed = parse_figures((ROOT / 'figures.txt').read_text('utf-8'))
        saved = json.loads((ROOT / 'figures.json').read_text('utf-8'))
        self.assertEqual(set(parsed), set(saved))
        self.assertEqual(parsed, saved)

    def test_standalone_root_runs_and_regenerates(self):
        with tempfile.TemporaryDirectory(prefix='jmdr-deposit-') as tmp:
            standalone = Path(tmp) / 'package'
            shutil.copytree(ROOT, standalone, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
            (standalone / 'figures.json').unlink()
            command = [sys.executable, 'code/jmdr_figures.py']
            plain = subprocess.run(command, cwd=standalone, capture_output=True, check=True)
            self.assertEqual(plain.stderr, b'')
            self.assertFalse((standalone / 'figures.json').exists())
            flagged = subprocess.run(command + ['--json'], cwd=standalone, capture_output=True, check=True)
            self.assertEqual(flagged.stderr, b'')
            self.assertEqual(plain.stdout, flagged.stdout)
            # Universal newline comparison makes the package test portable;
            # original-vs-package raw-byte comparison is recorded in VERIFY.md.
            stdout = flagged.stdout.decode('utf-8').replace('\r\n', '\n')
            self.assertEqual(stdout, (ROOT / 'figures.txt').read_text('utf-8'))
            regenerated = json.loads((standalone / 'figures.json').read_text('utf-8'))
            self.assertEqual(regenerated, parse_figures(stdout))
            self.assertEqual(regenerated, json.loads((ROOT / 'figures.json').read_text('utf-8')))

    def test_fixed_exclusion(self):
        code = (ROOT / 'code/jmdr_figures.py').read_text('utf-8')
        self.assertIn('EXCLUDED = {"K261253"}', code)
        records = json.loads((ROOT / 'data/openfda-510k-oap-2026-09-24.json').read_text('utf-8'))['results']
        retained = [r for r in records if r['k_number'] != 'K261253']
        figures = json.loads((ROOT / 'figures.json').read_text('utf-8'))
        self.assertEqual(len(retained), figures['clearances'])
        udi = json.loads((ROOT / 'data/openfda-udi-oap-2026-09-24.json').read_text('utf-8'))['results']
        self.assertFalse(any(s.get('submission_number') == 'K261253'
                             for r in udi for s in r.get('premarket_submissions', [])))


if __name__ == '__main__':
    unittest.main()
