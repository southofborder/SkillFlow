import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path('D:/projects/SkillFlow')
RUN = ROOT / 'packages/skill-ir/experiments/propagation/runs/abstract-runtime-v1-20260928-143306'
before = json.loads((ROOT / 'tmp/abstract-runtime-v1-verification/protected-before.json').read_text(encoding='utf-8-sig'))
changed = [name for name, digest in before.items()
           if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
protected = {'checked_files': len(before), 'changed_count': len(changed), 'changed_files': changed}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.duplicates = [], set(), []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicates.append(attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])

pages, bad = {}, []
for page in sorted(RUN.rglob('*.html')):
    parser = Links()
    text = page.read_text(encoding='utf-8')
    parser.feed(text)
    pages[page] = parser
    if parser.duplicates:
        bad.append({'page': str(page.relative_to(RUN)), 'duplicate_ids': parser.duplicates})
for page, parser in pages.items():
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            continue
        target = (page.parent / unquote(url.path)).resolve() if url.path else page
        if not target.is_file():
            bad.append({'page': str(page.relative_to(RUN)), 'missing_link': href})
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            bad.append({'page': str(page.relative_to(RUN)), 'missing_anchor': href})

# Compare only actual configured credentials; never print or save their values.
env_text = (ROOT / '.env').read_text(encoding='utf-8-sig')
secrets = []
for line in env_text.splitlines():
    match = re.match(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)', line)
    if match and any(word in match[1].upper() for word in ('API_KEY', 'TOKEN', 'PASSWORD', 'SECRET')):
        value = match[2].strip().strip('\"\'')
        if len(value) >= 16:
            secrets.append(value.encode())
leaked = []
for path in RUN.rglob('*'):
    if path.is_file() and any(secret in path.read_bytes() for secret in secrets):
        leaked.append(str(path.relative_to(RUN)))
result = {'protected': protected,
          'html_static_check': {'pages': len(pages), 'links': sum(len(p.links) for p in pages.values()), 'errors': bad,
                                'visual_check': 'blocked: browser disallows file://; no visual inspection claimed'},
          'credential_scan': {'configured_credentials_found': bool(secrets), 'files_containing_credentials': leaked}}
(RUN / 'verification/final-checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
assert not changed and not bad and not leaked
