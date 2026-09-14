#!/usr/bin/env python3
"""Install reviewed PDF candidates only after checking every receipt and source hash."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest', default=str(Path(__file__).with_name('pdf-manifest.json')))
parser.add_argument('--jobs', required=True)
parser.add_argument('--candidates', required=True)
parser.add_argument('--report', required=True)
parser.add_argument('--write', action='store_true')
parser.add_argument('--reviewed-exporter-sha256', action='append', default=[],
    help='Also accept a specifically reviewed earlier exporter version for unchanged sources')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
candidates = Path(args.candidates).resolve()
manifest = json.loads(Path(args.manifest).read_text())
jobs = {item['pdf']: item for item in json.loads(Path(args.jobs).read_text())}
exporter = Path(__file__).with_name('export_pdf.cjs')
exporter_hash = hashlib.sha256(exporter.read_bytes() + exporter.with_name('tag_pdf.py').read_bytes()).hexdigest()
reviewed_exporters = {exporter_hash, *args.reviewed_exporter_sha256}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def validated(report):
    values = [v for job in report['report']['jobs'] for v in job.get('validationResult', [])]
    return len(values) == 1 and values[0]['compliant']
records = []
replacements = []
for item in manifest['documents']:
    relative = Path(item['pdf'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Invalid manifest path: {relative}')
    source = root / relative
    if sha(source) != item['original_sha256']:
        raise ValueError(f'Source changed since inventory: {relative}')
    if item.get('retain_original'):
        records.append(dict(pdf=str(relative), status='retained historical archive', sha256=sha(source)))
        continue
    candidate = candidates / relative
    if not candidate.is_file():
        raise ValueError(f'Missing candidate: {relative}')
    if item.get('artwork'):
        result = subprocess.run(['verapdf', '--flavour', 'ua1', '--format', 'json', str(candidate)],
            check=True, text=True, capture_output=True)
        if not validated(json.loads(result.stdout)):
            raise ValueError(f'Artwork validation failed: {relative}')
        record = dict(pdf=str(relative), status='tagged artwork', pdfua1=True)
    else:
        job = jobs[relative.as_posix()]
        receipt = json.loads(Path(str(candidate) + '.receipt.json').read_text())
        if receipt.get('source_sha256') != job['source_sha256'] or receipt.get('exporter_sha256') not in reviewed_exporters:
            raise ValueError(f'Stale candidate: {relative}')
        if not validated(json.loads(Path(str(candidate) + '.validation.json').read_text())):
            raise ValueError(f'PDF/UA validation failed: {relative}')
        summary = json.loads(Path(str(candidate) + '.export.json').read_text())
        record = dict(pdf=str(relative), status='reflowed tagged document', pdfua1=True,
            formulas=summary['formulaCount'], figures=summary['figureCount'],
            source_urls=job['source_urls'], source_sha256=job['source_sha256'], exporter_sha256=receipt['exporter_sha256'])
    record['original_sha256'] = item['original_sha256']
    record['sha256'] = sha(candidate)
    records.append(record)
    replacements.append((candidate, source))
# The full catalog must validate before any source is changed.
if args.write:
    for candidate, source in replacements:
        shutil.copyfile(candidate, source)
report = dict(installed=args.write, documents=len(records), replaced=len(replacements),
    retained=len(records)-len(replacements), records=records)
Path(args.report).parent.mkdir(parents=True, exist_ok=True)
Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: value for key, value in report.items() if key != 'records'}))
