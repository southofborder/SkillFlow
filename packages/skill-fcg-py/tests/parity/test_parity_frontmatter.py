"""Cross-engine parity: gray-matter vs the Python front-matter split.

Locks two things that feed node identity: (1) the body ``content`` slice
(line numbers downstream depend on it) and (2) the parsed scalar keys
(name/description/version). Skipped when Node/gray-matter are unavailable.
"""

import json
import os
import shutil
import subprocess

import pytest

from skill_fcg.parser.skill_parser import _split_front_matter

_HERE = os.path.dirname(__file__)
_JS_DRIVER = os.path.join(_HERE, "js_frontmatter.cjs")

_INPUTS = [
    "---\nname: demo\ndescription: A demo skill\nversion: 2.1.0\n---\n# Intro\nhello\n",
    "---\nname: n\ndescription: d\n---\nbody line 1\nbody line 2\n",
    "---\nname: quoted\ndescription: \"has: colon\"\n---\n## Section\ntext\n",
    "no front matter here\n# Heading\nbody\n",
    "---\nname: crlf\ndescription: windows\r\n---\r\n# H\r\nbody\r\n",
    "---\nname: multi\ndescription: >\n  folded description\n  spanning lines\n---\ncontent\n",
]


def _run_js(inputs):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    spec_path = os.path.join(_HERE, "_frontmatter_inputs.json")
    with open(spec_path, "w", encoding="utf-8") as handle:
        json.dump(inputs, handle)
    proc = subprocess.run([node, _JS_DRIVER, spec_path], capture_output=True, text=True, cwd=_HERE)
    if proc.returncode != 0:
        pytest.skip(f"gray-matter driver failed: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


def test_frontmatter_split_matches_gray_matter():
    js_out = _run_js(_INPUTS)

    for idx, (raw, js) in enumerate(zip(_INPUTS, js_out)):
        data, content = _split_front_matter(raw)
        assert content == js["content"], f"input[{idx}] body diverged:\nJS ={js['content']!r}\nPY ={content!r}"
        for key in ("name", "description", "version"):
            if key in js["data"]:
                assert data.get(key) == js["data"][key], f"input[{idx}].{key} diverged"
