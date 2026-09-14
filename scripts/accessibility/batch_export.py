#!/usr/bin/env python3
"""Stage validated PDF candidates. This command never replaces source documents."""
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jobs', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--python', default=os.environ.get('PDF_PYTHON'))
parser.add_argument('--workers', type=int, default=3)
parser.add_argument('--only', help='Regular expression selecting PDF paths')
args = parser.parse_args()
output = Path(args.output).resolve()
output.mkdir(parents=True, exist_ok=True)
jobs = json.loads(Path(args.jobs).read_text())
if args.only:
    jobs = [job for job in jobs if re.search(args.only, job['pdf'])]
exporter = Path(__file__).with_name('export_pdf.cjs')
exporter_sha256 = hashlib.sha256(exporter.read_bytes() +
    exporter.with_name('tag_pdf.py').read_bytes()).hexdigest()

def export(job):
    destination = output / job['pdf']
    destination.parent.mkdir(parents=True, exist_ok=True)
    receipt_path = Path(str(destination) + '.receipt.json')
    if destination.exists() and receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('source_sha256') == job['source_sha256'] and receipt.get('exporter_sha256') == exporter_sha256:
            return dict(job, status='cached')
    command = ['node', str(exporter), '--url', job['url'], '--output', str(destination)]
    if args.python:
        command += ['--python', args.python]
    if job.get('landscape'):
        command.append('--landscape')
    result = subprocess.run(command, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    Path(str(destination) + '.log').write_text(result.stdout)
    if result.returncode == 0:
        receipt_path.write_text(json.dumps(dict(job, exporter_sha256=exporter_sha256), indent=2) + '\n')
    return dict(job, status='passed' if result.returncode == 0 else 'failed',
                log=str(destination) + '.log')

results = []
with ThreadPoolExecutor(max_workers=args.workers) as pool:
    futures = {pool.submit(export, job): job for job in jobs}
    for future in as_completed(futures):
        job = futures[future]
        try:
            result = future.result()
        except Exception as error:
            result = dict(job, status='failed', error=str(error))
        results.append(result)
        print(f"{len(results)}/{len(jobs)} {result['status']}: {job['pdf']}", flush=True)
        (output / 'batch-report.json').write_text(json.dumps(results, indent=2) + '\n')
raise SystemExit(1 if any(result['status'] == 'failed' for result in results) else 0)
