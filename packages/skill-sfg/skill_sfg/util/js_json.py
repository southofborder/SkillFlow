"""JS-compatible JSON serialization — the single authority for byte-parity with
Node's ``JSON.stringify``.

This exists because several load-bearing hash keys are computed as
``shortHash(... JSON.stringify(obj) ...)`` (e.g. flow-instance-filter.js:412's
``event_id``). If Python's serialization diverges from Node by a single byte the
resulting hash differs, and the FCG↔DOE join keyed on that id silently breaks.

Verified byte-identical to Node ``JSON.stringify`` for: non-ASCII (emitted raw,
NOT ``\\uXXXX`` — matches Node), control chars, quote/backslash/tab/newline
escaping, and the ``/`` ``<`` ``&`` characters (unescaped in both). The two JS
behaviors that have no direct Python analogue:

  * object key whose value is ``undefined`` → dropped. In Python you simply do
    not put the key in the dict (the callers already follow this convention).
  * array element ``undefined`` → serialized as ``null``. ``None`` in a Python
    list already serializes to ``null``, so this matches when the caller maps a
    JS ``undefined`` slot to ``None``.
"""

import json


def js_json_stringify(value):
    """Equivalent of ``JSON.stringify(value)`` (default separators, no spaces).

    ``ensure_ascii=False`` reproduces Node's raw-Unicode output;
    ``separators=(",", ":")`` reproduces the space-free default; Python's dict
    insertion order matches Node's object key order for dicts we build directly.
    """
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
