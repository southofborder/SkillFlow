"""Write fresh-run lifecycle scripts only; do not prepare or launch a model run."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "output/verification/online-ga4-review-shared-v2-20261112"
TARGET = ROOT / "output/verification/online-ga4-source-review-locality-20261113"
TARGET.mkdir(exist_ok=True)


def write(name, text):
    with (TARGET / name).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


prepare = (PRIOR / "prepare_run.py").read_text(encoding="utf-8")
prepare = prepare.replace('"review-input-size-20261112"', '"source-review-locality-20261113"')
prepare = prepare.replace('"online-ga4-input-necessity-corrected-r2-20261112"', '"online-ga4-review-shared-v2-20261112"')
prepare = prepare.replace('document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209',
                          'document-guided-ga4-review-shared-v2-high-20261112-221242')
start = prepare.index('AUTHORIZATION = (')
end = prepare.index('\n\n\ndef read', start)
prepare = prepare[:start] + '''AUTHORIZATION = ("User requested diagnosis and a general strict fix for three failed missing-field locators and whole-review invalidation; "
                 "keep complete source and every contract, seven normal requests, two workers and existing budgets. "
                 "After offline acceptance root alone may run exactly one fresh GA4 and its sole zero-call replay.")''' + prepare[end:]
prepare = prepare.replace('skillflow-document-guided-run-v12', 'skillflow-document-guided-run-v13')
prepare = prepare.replace('document-guided-ga4-review-shared-v2-high-{tag}', 'document-guided-ga4-source-review-locality-high-{tag}')
prepare = prepare.replace('generic_lossless_source_review_shared_v2', 'strict_source_review_record_isolation_v1')
prepare = prepare.replace('Current review identity differs from accepted generic display', 'Current review identity differs from accepted strict record isolation')
prepare = prepare.replace('"guided_run_identity": IDENTITY, "review_protocol": "shared-v2",',
    '"guided_run_identity": IDENTITY, "review_protocol": "shared-v2",\n        "review_validation": "strict-record-isolation-v1",')
write('prepare_run.py', prepare)
for name in ('controller-template.py', 'local_timing.py', 'observe_run.py', 'audit_cost_provenance.py'):
    text = (PRIOR / name).read_text(encoding='utf-8')
    text = text.replace('document-guided-ga4-review-shared-v2-high-', 'document-guided-ga4-source-review-locality-high-')
    text = text.replace('skillflow-document-guided-run-v12', 'skillflow-document-guided-run-v13')
    text = text.replace('fresh shared-v2 GA4', 'fresh source-review-locality GA4')
    text = text.replace('prepared shared-v2 GA4', 'prepared source-review-locality GA4')
    write(name, text)
dispatch = (PRIOR / 'dispatch_once.ps1').read_text(encoding='utf-8')
old_line = "if ((Split-Path -Leaf $runPath) -ne 'document-guided-ga4-review-shared-v2-high-20261112-221242') { throw 'This dispatch belongs to the sole prepared fresh run' }"
new_lines = """$intent = Get-Content -LiteralPath (Join-Path $verifyPath 'preparation-intent.json') -Raw | ConvertFrom-Json
if ($runPath -ne [IO.Path]::GetFullPath($intent.run_directory)) { throw 'Prepared run differs from its sole recorded preparation intent' }
if ((Split-Path -Leaf $runPath) -notmatch '^document-guided-ga4-source-review-locality-high-[0-9]{8}-[0-9]{6}$') { throw 'This dispatch belongs only to the fresh source-review-locality GA4 namespace' }"""
assert old_line in dispatch
write('dispatch_once.ps1', dispatch.replace(old_line, new_lines))
print('Fresh lifecycle scripts written; no run prepared or model launched.')
