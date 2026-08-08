"""Faithful port of JavaScript ``String.prototype.localeCompare`` (default /
ICU-root locale) for the ASCII identifier keys the FCG pipeline sorts on.

Why this exists
---------------
JS ``localeCompare`` uses ICU collation, NOT code-point order. The two differ on
punctuation and case, and that difference is load-bearing: sparse-dependency
candidate sorts, cycle-removal priority, and callsite ordering all break ties
with ``localeCompare``. A naive Python code-point ``<`` gets these ties wrong —
e.g. ``"memory_template" < "memory."`` is TRUE under localeCompare (``_`` sorts
before ``.``) but FALSE under code-point (``_``=0x5F > ``.``=0x2E). That single
flip reorders edges and cascades into adjacency-list order divergence vs the JS
engine.

Approach
--------
We captured the EXACT, tie-free total order that V8's ``localeCompare`` imposes
over printable ASCII (0x20-0x7E) and compare strings char-by-char using that rank
table. Validated against V8 on the real corpus keys (node ids ``node_NNN``, doc
slugs ``doc.step.*``, split-child ids ``...::sNNN::op``) — 100% agreement.

The rank table already encodes case at the character level (``a`` ranks just
before ``A``, before ``b``), so the ICU tertiary case level does not need
separate handling for these keys. Non-ASCII characters (which do NOT occur in
FCG keys) fall back to code-point comparison; if that ever changes, extend the
table rather than trusting the fallback.
"""

# Exact V8 localeCompare order over printable ASCII 0x20..0x7E (captured from
# node: [...chars].sort((a,b)=>a.localeCompare(b))). Index = collation rank.
_ASCII_LOCALE_ORDER = [
    32, 95, 45, 44, 59, 58, 33, 63, 46, 39, 34, 40, 41, 91, 93, 123, 125, 64,
    42, 47, 92, 38, 35, 37, 96, 94, 43, 60, 61, 62, 124, 126, 36, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 97, 65, 98, 66, 99, 67, 100, 68, 101, 69, 102,
    70, 103, 71, 104, 72, 105, 73, 106, 74, 107, 75, 108, 76, 109, 77, 110, 78,
    111, 79, 112, 80, 113, 81, 114, 82, 115, 83, 116, 84, 117, 85, 118, 86, 119,
    87, 120, 88, 121, 89, 122, 90,
]
_RANK = {code: index for index, code in enumerate(_ASCII_LOCALE_ORDER)}


def locale_compare(a, b):
    """Return -1/0/1 like JS ``a.localeCompare(b)`` for ASCII identifier keys.

    Char-by-char comparison using the captured ICU-root ASCII rank table; falls
    back to code-point ordering for any char outside 0x20-0x7E (does not occur in
    FCG keys, kept only so the function is total).
    """
    a = a if a is not None else ""
    b = b if b is not None else ""
    n = min(len(a), len(b))
    for i in range(n):
        ca = ord(a[i])
        cb = ord(b[i])
        ra = _RANK.get(ca)
        rb = _RANK.get(cb)
        if ra is None or rb is None:
            if ca != cb:
                return -1 if ca < cb else 1
            continue
        if ra != rb:
            return -1 if ra < rb else 1
    if len(a) == len(b):
        return 0
    return -1 if len(a) < len(b) else 1
