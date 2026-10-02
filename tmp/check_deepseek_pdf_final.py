"""Offline final PDF checks; never print any credential value."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/skill-ir-semantics-baseline-deepseek'
build = json.loads((OUT / 'build_manifest.json').read_text(encoding='utf-8'))
first = json.loads((ROOT / 'tmp/deepseek-final-first-build.json').read_text(encoding='utf-8'))
pdf = OUT / build['pdf']
digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
assert digest == build['pdf_sha256'] == first['pdf_sha256'], 'PDF is not byte-reproducible'
assert build['source_sha256'] == first['source_sha256'], 'Build sources changed'
reader = PdfReader(pdf)
assert len(reader.pages) == build['pages'] == 730
texts = [page.extract_text() for page in reader.pages]
assert all(text.strip() for text in texts)
all_text = '\n'.join(texts)
assert '\ufffd' not in all_text
for expected in ('语义基线', '待共同复核', '目录', 'deepseek-v4-flash', 'deepseek-flash'):
    assert expected in all_text
for number, text in enumerate(texts, 1):
    assert str(number) in text.splitlines()[-2:], f'Bad page footer: {number}'
for sample_id, number in build['page_index'].items():
    if len(sample_id) == 3 and sample_id[0] in 'NQFDR':
        assert sample_id in texts[number - 1], f'Bad sample page: {sample_id}'
trial_starts = sorted((number, key) for key, number in build['page_index'].items() if '/run-' in key)
assert len(trial_starts) == 90
for index, (start, key) in enumerate(trial_starts):
    stop = trial_starts[index + 1][0] if index + 1 < len(trial_starts) else len(texts) + 1
    sample_id, repetition = key.split('/run-')
    expected = f'{sample_id} / R{repetition}'
    for number in range(start, stop):
        assert expected in texts[number - 1], f'Wrong trial header: {key}, page {number}'
secret_values = []
for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
    if line.startswith('LLM_API_KEY='):
        value = line.split('=', 1)[1].strip().strip('\"\'')
        if value:
            secret_values.append(value)
assert secret_values, 'Expected local credential for leak check'
assert all(value not in all_text for value in secret_values), 'Credential found in PDF text'
result = {'schema_version': 1, 'pdf_sha256': digest, 'pages': len(texts),
          'deterministic_rebuild': {'passed': True, 'builds': 2, 'byte_identical_pdf': True,
                                    'identical_source_hash_manifest': True},
          'all_page_numbers_checked': True, 'all_pages_have_text': True,
          'chinese_searchable': True, 'replacement_character_count': 0,
          'sample_page_index_checked': True, 'credential_matches_in_pdf_text': 0,
          'all_90_trial_page_headers_checked': True,
          'content_verification': build['content_verification']}
(OUT / 'content_qa.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
