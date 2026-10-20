#!/usr/bin/env bash
# Archive the verified E7 delivery after PR #3 has merged. No files are deleted.
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
submit_dir=/root/submit/E7
server_repo=/root/devops-e7.d149Jj
gate_dir=work/e7-gate-20261020-112209
build_dir=work/e7-build-20261020-112001
cd "$repo_dir"

merge_record=$(mktemp)
curl --http1.1 --fail --silent --show-error --retry 2 \
  https://api.github.com/repos/laolvfan/devops/pulls/3 -o "$merge_record"

python3 - "$merge_record" "$repo_dir" "$server_repo" "$gate_dir" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
record = json.loads(Path(sys.argv[1]).read_text())
assert record.get('merged') is True, 'PR #3 must be merged before final archiving'
assert record['base']['repo']['full_name'] == 'laolvfan/devops'
head = subprocess.check_output(['git', '-C', sys.argv[2], 'rev-parse', 'HEAD'], text=True).strip()
assert head == record['merge_commit_sha'], 'Check out the PR #3 merge commit before archiving'
gate = json.loads((Path(sys.argv[3]) / sys.argv[4] / 'gate/gate-result.json').read_text())
assert gate['passed'] and len(gate['cases']) == 6 and all(c['passed'] for c in gate['cases'])
print('Verified final source revision and successful original server gate')
PY

mkdir -p "$submit_dir/reports" "$submit_dir/evidence/local" \
  "$submit_dir/evidence/environment" "$submit_dir/merge"
cp -a "$server_repo/$gate_dir" "$server_repo/$build_dir" "$submit_dir/evidence/local/"
cp "$server_repo/work/e7-env-241880326.json" "$submit_dir/evidence/environment/"
cp -a docs/E7/. "$submit_dir/reports/"
cp "$merge_record" "$submit_dir/merge/PR3-merged.json"
cp docs/E7/ci-evidence/protection-observed.json "$submit_dir/merge/protection-observed.json"
cp docs/E7/ci-evidence/rejection/merge-attempt.json "$submit_dir/merge/merge-rejection.json"
git rev-parse HEAD > "$submit_dir/source-commit.txt"
git archive --format=tar.gz --output="$submit_dir/source-code-$(git rev-parse --short HEAD).tar.gz" HEAD

python3 - "$submit_dir" "$server_repo/$build_dir" <<'PY'
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
output, build = Path(sys.argv[1]), Path(sys.argv[2])
metadata_by_phase = {}
for phase in ('normal', 'rejection', 'recovery'):
    source = Path('docs/E7/ci-evidence') / phase
    metadata = json.loads((source / 'run.json').read_text())
    expected = 'failure' if phase == 'rejection' else 'success'
    assert metadata['conclusion'] == expected, f'{phase}: unexpected CI conclusion'
    metadata_by_phase[phase] = metadata
    archive = source / 'artifact.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == metadata['artifact_sha256']
    destination = (output / 'evidence/ci' / phase).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        assert all(destination in (destination / n).resolve().parents for n in package.namelist() if n)
        package.extractall(destination)
    gate = json.loads((destination / 'gate/gate-result.json').read_text())
    if phase == 'rejection':
        assert gate['passed'] is False
        assert 'assert 0 == 1' in (destination / 'gate/unit-tests/stdout.log').read_text()
    else:
        assert gate['passed'] and len(gate['cases']) == 6 and all(c['passed'] for c in gate['cases'])
record = json.loads((output / 'merge/PR3-merged.json').read_text())
recovery = metadata_by_phase['recovery']
# Evidence is committed after the observed recovery run. Permit that reporting
# commit only when it descends from the tested head and all runtime inputs match.
subprocess.run(['git', 'merge-base', '--is-ancestor', recovery['head_sha'], record['head']['sha']], check=True)
runtime_paths = ['.github/workflows/e7-quality-gate.yml', 'services/draft', 'fixtures',
                 'requirements-dev.in', 'requirements-dev.lock', 'scripts/run_e7_b_gate.py',
                 'scripts/lab_cloud.py', 'scripts/secret_scan.py', 'tests/e7',
                 'work/candidate/error-mirror/Dockerfile']
subprocess.run(['git', 'diff', '--quiet', recovery['head_sha'], record['head']['sha'], '--', *runtime_paths], check=True)
table = output / 'reports/evidence-index.csv'
rows = list(csv.DictReader(table.open()))
for row in rows:
    if row['phase'] == 'ci' and row['case'] == 'recovery':
        row.update(status='PASS', actual='Full recovered CI gate passed', source_commit=recovery['head_sha'],
                   evidence_path_or_url=recovery['url'], notes='Original ZIP verified; final runtime inputs unchanged')
    if row['phase'] == 'ci' and row['case'] == 'merged':
        row.update(status='PASS', actual='MERGED', source_commit=record['merge_commit_sha'],
                   evidence_path_or_url=str(output / 'merge/PR3-merged.json'), notes=record['html_url'])
with table.open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
handoff = output / 'reports/handoff.json'
data = json.loads(handoff.read_text())
data['status'] = 'E7_COMPLETED_AND_ARCHIVED'
data['submission'].update(status='ARCHIVED', merge_commit=record['merge_commit_sha'])
handoff.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
images = json.loads((build / 'image/stdout.log').read_text())
(output / 'service-image-id.txt').write_text(images[0]['Id'] + '\n')
with (output / 'reports/report.md').open('a') as stream:
    stream.write('\n最终归档：PR #3 已合并，提交 ' + record['merge_commit_sha'] +
                 '。实际合并 JSON 与完整证据已保存到 /root/submit/E7。\n')
print('ARCHIVE_COMPLETE=/root/submit/E7')
print('All CI archives verified; final merge and submission records completed')
PY
