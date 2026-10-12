"""在独立临时副本验证 E3 参考补丁；不修改输入仓库。"""
import argparse
import difflib
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab-repo', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    repo = args.lab_repo.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv])
    revision = git('rev-parse', 'HEAD').decode().strip()
    report = json.loads(git('show', f'{revision}:oracle/mdfixer/md-report.json'))
    baseline = report['repository']['commit']
    assert git('rev-parse', 'e3-mdfixer-md-v1.0.0^{commit}').decode().strip() == baseline
    write_json(out / 'oracle-report.json', report)
    source = out / 'source'
    source.mkdir()
    for name in ('Makefile', 'main.c', 'config.h'):
        (source / name).write_bytes(git('show', f'{baseline}:{name}'))
    patches = out / 'patches'
    patches.mkdir()
    for style in ('target', 'macro', 'hybrid', 'implicit'):
        (patches / f'{style}.patch').write_bytes(git('show', f'{revision}:oracle/mdfixer/reference/{style}.patch'))
    def version(cmd):
        return subprocess.check_output(cmd, text=True).splitlines()[0]
    summary = {'source_repository': report['repository']['url'], 'lab_commit': revision,
               'source_commit': baseline, 'kind': 'ACTUAL_LOCAL_RUN',
               'environment': {'os_release': Path('/etc/os-release').read_text(),
                               'architecture': platform.machine(), 'gcc': version(['gcc', '--version']),
                               'make': version(['make', '--version']), 'git': version(['git', '--version'])},
               'note': 'Independent environment; not the original cfg-ubuntu24-gcc13-debug-v1 run.',
               'results': {}}
    for style in ('target', 'macro', 'hybrid', 'implicit'):
        evidence = out / style
        evidence.mkdir()
        steps = []
        result = {'passed': False}
        with tempfile.TemporaryDirectory(prefix='e3-mdfixer-') as tmp:
            work = Path(tmp)
            for p in source.iterdir(): shutil.copy2(p, work / p.name)
            def run(label, cmd, expected_code=0, stdout=None):
                p = subprocess.run(cmd, cwd=work, text=True, capture_output=True, timeout=30)
                (evidence / f'{label}.stdout.log').write_text(p.stdout)
                (evidence / f'{label}.stderr.log').write_text(p.stderr)
                steps.append({'label': label, 'command': cmd, 'exit_code': p.returncode,
                              'expected_exit_code': expected_code, 'expected_stdout': stdout})
                write_json(evidence / 'commands.json', steps)
                assert (p.returncode != 0 if expected_code == 'nonzero' else p.returncode == expected_code), label
                if stdout is not None: assert p.stdout.strip() == stdout, label
                return p
            def header(value, label):
                # 等待真实时钟跨过旧产物时间，避免快速写入导致时间戳相等。
                time.sleep(1.1)
                (work / 'config.h').write_text((source / 'config.h').read_text().replace('VALUE 1', f'VALUE {value}'))
                state = {'value': value, 'config_h_mtime_ns': (work / 'config.h').stat().st_mtime_ns,
                         'main_o_mtime_ns': (work / 'main.o').stat().st_mtime_ns}
                assert state['config_h_mtime_ns'] > state['main_o_mtime_ns']
                write_json(evidence / f'{label}.json', state)
            try:
                run('01-baseline-build', ['make'])
                run('02-baseline-run', ['./app'], stdout='1')
                header(2, '03-change-header')
                before = (work / 'main.o').stat().st_mtime_ns
                run('04-stale-make', ['make'])
                run('05-stale-run', ['./app'], stdout='1')
                assert (work / 'main.o').stat().st_mtime_ns == before
                patch = str(patches / f'{style}.patch')
                run('06-check-patch', ['git', 'apply', '--check', patch])
                run('07-apply-patch', ['git', 'apply', patch])
                shutil.copy2(work / 'Makefile', evidence / 'Makefile.accepted')
                run('08-clean', ['make', 'clean'])
                run('09-fixed-build', ['make'])
                run('10-fixed-run', ['./app'], stdout='2')
                header(3, '11-change-header')
                before = (work / 'main.o').stat().st_mtime_ns
                run('12-incremental-make', ['make'])
                run('13-incremental-run', ['./app'], stdout='3')
                assert (work / 'main.o').stat().st_mtime_ns > before
                if style == 'implicit':
                    dep = (work / 'main.d').read_text()
                    assert 'main.o:' in dep and 'config.h' in dep
                    (evidence / 'main.d').write_text(dep)
                # 独立拒绝案例：恢复原始 Makefile 后注入必定失败的 all recipe。
                original = (source / 'Makefile').read_text()
                (work / 'Makefile').write_text(original)
                run('14-before-rejection-clean', ['make', 'clean'])
                invalid = original.replace('all: app', 'all: app\n\tfalse')
                assert invalid != original
                # 基线末行没有换行，统一补丁输入末尾换行。
                badpatch = ''.join(difflib.unified_diff((original+'\n').splitlines(True), (invalid+'\n').splitlines(True), fromfile='a/Makefile', tofile='b/Makefile'))
                (evidence / 'invalid.patch').write_text(badpatch)
                (work / 'Makefile').write_text(original+'\n')
                run('15-invalid-check', ['git', 'apply', '--check', str(evidence / 'invalid.patch')])
                run('16-invalid-apply', ['git', 'apply', str(evidence / 'invalid.patch')])
                run('17-invalid-build', ['make'], expected_code='nonzero')
                (work / 'Makefile').write_bytes((source / 'Makefile').read_bytes())
                assert (work / 'Makefile').read_bytes() == (source / 'Makefile').read_bytes()
                run('18-restored-clean', ['make', 'clean'])
                run('19-restored-build', ['make'])
                run('20-restored-run', ['./app'], stdout='3')
                result.update(passed=True, stale_output='1', fixed_clean_output='2', fixed_incremental_output='3',
                              invalid_candidate_accepted=False, restored_original_makefile=True, restored_output='3')
            except (AssertionError, subprocess.TimeoutExpired) as exc:
                result['failure'] = str(exc)
            summary['results'][style] = result
            write_json(out / 'summary.json', summary)
    files = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
    write_json(out / 'sha256.json', files)
    print(json.dumps(summary['results'], ensure_ascii=False, indent=2))
    return 0 if all(r['passed'] for r in summary['results'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
