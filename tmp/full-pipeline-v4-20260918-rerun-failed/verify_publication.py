"""Check the published bytes and all previously frozen provenance boundaries."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed'
FOLDERS = ('ir-IPP', 'suggestions', 'security-profiles', 'review')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_inventory(base: Path, files: dict[str, str]) -> None:
    for relative, expected in files.items():
        path = base / relative
        assert path.is_file(), f'Missing file: {path}'
        assert digest(path) == expected, f'Changed bytes: {path}'


def main() -> None:
    verification = read(ROOT / 'result/review/verification.json')
    before = read(HERE / 'replay-acceptance/before.json')
    expected = dict(verification['files'])
    expected['review/verification.json'] = digest(HERE / 'staging/review/verification.json')
    actual = {
        p.relative_to(ROOT / 'result').as_posix()
        for folder in FOLDERS
        for p in (ROOT / 'result' / folder).rglob('*') if p.is_file()
    }
    assert actual == set(expected), 'Unexpected published file set'
    check_inventory(ROOT / 'result', expected)
    check_inventory(HERE / 'staging', expected)

    inputs = list((ROOT / 'dataset/skills').iterdir())
    names = {p.stem for p in inputs}
    assert len(inputs) == len(names) == 30
    assert all(p.is_file() and p.suffix == '.zip' for p in inputs)
    assert sorted(int(n[:3]) for n in names) == list(range(1, 31))
    for folder, suffix in [('ir-IPP', '.png'), ('suggestions', '.md'), ('security-profiles', '.json')]:
        paths = list((ROOT / 'result' / folder).iterdir())
        assert len(paths) == 30 and {p.stem for p in paths} == names
        assert all(p.is_file() and p.suffix == suffix for p in paths)

    unchanged = {}
    archived = {}
    for relative, expected_sha in before['protected_files'].items():
        parts = Path(relative).parts
        if parts[0] == 'result' and parts[1] in FOLDERS:
            archived[Path(*parts[1:]).as_posix()] = expected_sha
        else:
            unchanged[relative] = expected_sha
    check_inventory(ROOT, unchanged)
    check_inventory(HERE / 'published-prior', archived)
    check_inventory(Path(before['parent_path']), before['parent_files'])
    check_inventory(RUN, before['call_files'])
    check_inventory(RUN, before['terminal_result_files'])
    assert digest(RUN / 'experiment-result.json') == before['root_result_sha256']
    assert verification['summary'] == read(RUN / 'experiment-result.json')['summary']
    assert verification['status'] == 'passed' and verification['cases'] == 30
    assert (ROOT / 'result/review/report.md').read_bytes() == (RUN / 'acceptance-report.md').read_bytes()

    report = {
        'schema_version': 1,
        'identity': 'skill-ir-publication-postcheck-v1',
        'status': 'passed',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'run_id': RUN.name,
        'scope': '发布字节、数量配对、输入保护和历史记录不变；不等于语义全部通过',
        'published_files': len(actual),
        'paired_inputs_and_outputs': 30,
        'unchanged_protected_files': len(unchanged),
        'prior_delivery_files_verified_in_backup': len(archived),
        'unchanged_parent_files': len(before['parent_files']),
        'unchanged_call_files': len(before['call_files']),
        'unchanged_terminal_results': len(before['terminal_result_files']),
        'verification_sha256': digest(ROOT / 'result/review/verification.json'),
        'backup_path': (HERE / 'published-prior').relative_to(ROOT).as_posix(),
        'summary': verification['summary'],
        'api_calls': 0,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    (HERE / 'publication-verification.json').write_text(payload, encoding='utf-8')
    (RUN / 'delivery-acceptance/publication.json').write_text(payload, encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
