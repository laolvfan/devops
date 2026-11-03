from pathlib import Path
import sys
from lab import fixture, scan, patch, save, commit, validate

out = Path(sys.argv[1])
project = out / 'compile-failure-project'

# 创建独立样例，并有意引入 C 语法错误。
fixture(project)
(project / 'main.c').write_text(
    '#include "config.h"\n'
    'int main(void) { invalid syntax; }\n'
)
commit(project, 'study: introduce compile failure')

# 根据该样例版本生成合法候选补丁。
report = scan(project)
save(out / 'compile-failure-report.json', report)

diff, plan = patch(project, report)
candidate = out / 'compile-failure.patch'
candidate.write_text(diff)
save(out / 'compile-failure-plan.json', plan)

before = (project / 'Makefile').read_bytes()
(out / 'compile-failure-before.Makefile').write_bytes(before)

# 补丁可应用，但构建失败时不得接受。
result = validate(project, candidate, out / 'reject-compile')

assert result['checks']['patch_applies'] is True
assert result['checks'].get('build', False) is False
assert result['accepted'] is False
assert result['rollback'] is True
assert result['source_unchanged'] is True
assert result['error'] and 'COMMAND_FAILED' in result['error']
assert (project / 'Makefile').read_bytes() == before

print('EXPECTED_COMPILE_REJECTION', result)
print('COMPILE_FAILURE_STUDY_PASS')
