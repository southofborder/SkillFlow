"""Cross-engine parity: gray-matter vs the Python front-matter split.

Locks two things that feed node identity: (1) the body ``content`` slice
(line numbers downstream depend on it) and (2) the parsed scalar keys
(name/description/version). Skipped when Node/gray-matter are unavailable.
"""

import json
import os

import pytest

from skill_sfg.parser.skill_parser import _split_front_matter

_HERE = os.path.dirname(__file__)
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "frontmatter.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)

_INPUTS = [
    "---\nname: demo\ndescription: A demo skill\nversion: 2.1.0\n---\n# Intro\nhello\n",
    "---\nname: n\ndescription: d\n---\nbody line 1\nbody line 2\n",
    "---\nname: quoted\ndescription: \"has: colon\"\n---\n## Section\ntext\n",
    "no front matter here\n# Heading\nbody\n",
    "---\nname: crlf\ndescription: windows\r\n---\r\n# H\r\nbody\r\n",
    "---\nname: multi\ndescription: >\n  folded description\n  spanning lines\n---\ncontent\n",
]


def test_frontmatter_split_matches_gray_matter():
    js_out = _GOLDEN

    for idx, (raw, js) in enumerate(zip(_INPUTS, js_out)):
        data, content = _split_front_matter(raw)
        assert content == js["content"], f"input[{idx}] body diverged:\nJS ={js['content']!r}\nPY ={content!r}"
        for key in ("name", "description", "version"):
            if key in js["data"]:
                assert data.get(key) == js["data"][key], f"input[{idx}].{key} diverged"
