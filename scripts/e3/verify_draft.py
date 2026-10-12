"""从固定提交导出 DRAFT 输入，实际构建并保存命令、环境和验证证据。"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


SOURCE_COMMIT = '4ddc1f9db7c23d0ee580bdde9758bc8cb024b1a3'
SOURCE_PATH = 'E3实验包/fixtures/draft'
SOURCE_FILES = ('main.c', 'Makefile', 'Dockerfile.broken', 'Dockerfile.reference')
BASE_IMAGE = 'python:3.13-slim'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--build-network', choices=('default', 'host'), default='default')
    parser.add_argument('--build-proxy', help='构建时使用的无认证代理地址；不接受包含凭据的 URL')
    args = parser.parse_args()
    if args.build_proxy:
        proxy = urlsplit(args.build_proxy)
        if proxy.scheme not in ('http', 'https') or not proxy.hostname or proxy.username or proxy.password:
            parser.error('--build-proxy must be an HTTP(S) URL without credentials')
    repo = Path(__file__).resolve().parents[2]
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'runner.py').write_bytes(Path(__file__).read_bytes())
    source = out / 'source'
    source.mkdir()
    logs = out / 'logs'
    logs.mkdir()
    commands = []
    summary = {
        'kind': 'ACTUAL_LOCAL_RUN',
        'source_repository': 'https://github.com/laolvfan/devops.git',
        'source_commit': SOURCE_COMMIT,
        'source_path': SOURCE_PATH,
        'input_method': 'git show from fixed commit; build context contains only the four exported files',
        'base_image_tag': BASE_IMAGE,
        'build_network': args.build_network,
        'build_proxy': args.build_proxy,
        'passed': False,
    }

    def run(label, argv, cwd=repo, expected_code=0, expected_stdout=None, timeout=600):
        print(label, flush=True)
        command = {'label': label, 'argv': argv, 'cwd': str(cwd),
                   'expected_exit_code': expected_code}
        commands.append(command)
        write_json(out / 'commands.json', commands)
        try:
            with (logs / f'{label}.stdout.log').open('wb') as stdout, (logs / f'{label}.stderr.log').open('wb') as stderr:
                process = subprocess.run(argv, cwd=cwd, stdout=stdout, stderr=stderr, timeout=timeout)
            result = subprocess.CompletedProcess(argv, process.returncode,
                                                 (logs / f'{label}.stdout.log').read_bytes(),
                                                 (logs / f'{label}.stderr.log').read_bytes())
        except subprocess.TimeoutExpired as exc:
            command.update(exit_code=None, timed_out=True)
            write_json(out / 'commands.json', commands)
            raise RuntimeError(f'{label}: exceeded {timeout} seconds') from exc
        command['exit_code'] = result.returncode
        if expected_stdout is not None:
            command['expected_stdout'] = expected_stdout
        write_json(out / 'commands.json', commands)
        ok = result.returncode != 0 if expected_code == 'nonzero' else result.returncode == expected_code
        if not ok:
            raise RuntimeError(f'{label}: unexpected exit code {result.returncode}; see logs')
        if expected_stdout is not None and result.stdout.decode().strip() != expected_stdout:
            raise RuntimeError(f'{label}: unexpected output; see logs')
        return result

    try:
        run('host-os', ['cat', '/etc/os-release'])
        run('host-kernel-architecture', ['uname', '-srm'])
        run('host-git-version', ['git', '--version'])
        run('host-python-version', ['python3', '--version'])
        summary['materials_commit'] = run('materials-commit', ['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
        run('materials-worktree', ['git', 'status', '--short'])
        run('docker-version', ['docker', 'version'])
        run('docker-daemon', ['docker', 'info', '--format',
                             'OS={{.OperatingSystem}}\nArchitecture={{.Architecture}}\nKernel={{.KernelVersion}}\nStorage={{.Driver}}'])
        for name in SOURCE_FILES:
            data = run(f'export-{name}', ['git', 'show', f'{SOURCE_COMMIT}:{SOURCE_PATH}/{name}']).stdout
            (source / name).write_bytes(data)
        summary['input_sha256'] = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                   for name in SOURCE_FILES}
        run('base-pull', ['docker', 'pull', BASE_IMAGE])
        base = json.loads(run('base-inspect', ['docker', 'image', 'inspect', BASE_IMAGE]).stdout)[0]
        summary['base_image_id'] = base['Id']
        summary['base_repo_digests'] = base['RepoDigests']
        with tempfile.TemporaryDirectory(prefix='b11-e3-draft-') as tmp:
            context = Path(tmp)
            for name in SOURCE_FILES:
                (context / name).write_bytes((source / name).read_bytes())
            summary['build_context'] = str(context)
            tag = f'b11-e3-draft-reference:{context.name}'
            build_options = ['docker', 'build', '--no-cache', '--force-rm', '--pull=false', '--network', args.build_network]
            if args.build_proxy:
                build_options += ['--build-arg', f'http_proxy={args.build_proxy}', '--build-arg', f'https_proxy={args.build_proxy}']
            broken = run('broken-build', build_options + [
                                         '-f', 'Dockerfile.broken', '.'], cwd=context, expected_code='nonzero')
            broken_log = (broken.stdout + broken.stderr).decode(errors='replace')
            if not re.search(r'make: (?:not found|command not found)', broken_log):
                raise RuntimeError('broken-build: failure was not the expected missing make error')
            summary['broken_build'] = {'exit_code': broken.returncode, 'missing_make_confirmed': True}
            build = run('reference-build', build_options + [
                                           '--iidfile', str(out / 'image_id.txt'), '-t', tag,
                                           '-f', 'Dockerfile.reference', '.'], cwd=context)
            image_id = (out / 'image_id.txt').read_text().strip()
            inspected = json.loads(run('reference-inspect', ['docker', 'image', 'inspect', image_id]).stdout)[0]
            if inspected['Id'] != image_id:
                raise RuntimeError('reference-inspect: image ID differs from build --iidfile')
            base_after = json.loads(run('base-inspect-after', ['docker', 'image', 'inspect', BASE_IMAGE]).stdout)[0]
            if base_after['Id'] != base['Id']:
                raise RuntimeError('base-inspect-after: base tag changed during the experiment')
            run('container-os', ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'cat', image_id, '/etc/os-release'])
            run('container-architecture', ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'uname', image_id, '-m'])
            run('container-compiler', ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'cc', image_id, '--version'])
            run('container-make', ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'make', image_id, '--version'])
            run('container-packages', ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'dpkg-query', image_id,
                                       '-W', '-f=${Package}\t${Version}\n', 'gcc', 'make', 'libc6-dev'])
            result = run('reference-run', ['docker', 'run', '--rm', '--network', 'none', image_id], expected_stdout='hello E3')
            if {name: hashlib.sha256((context / name).read_bytes()).hexdigest() for name in SOURCE_FILES} != summary['input_sha256']:
                raise RuntimeError('build inputs changed during the experiment')
            summary.update(passed=True, input_unchanged=True, base_image_unchanged=True,
                           reference_image_id=image_id, reference_image_tag=tag,
                           reference_build_exit_code=build.returncode,
                           reference_run_exit_code=result.returncode,
                           reference_stdout=result.stdout.decode())
    except (OSError, RuntimeError, ValueError) as exc:
        summary['failure'] = str(exc)
    finally:
        write_json(out / 'summary.json', summary)
        write_json(out / 'sha256.json', {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'sha256.json'})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
