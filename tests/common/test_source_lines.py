"""Exact line extraction shares one boundary definition with review rendering."""
import pytest

from skillflow.common.source_evidence import extract_source_lines, source_lines


@pytest.mark.parametrize("text,expected", [
    ("", []), ("x", ["x"]), ("x\n", ["x\n"]), ("x\r\n", ["x\r\n"]),
    ("x\n\n", ["x\n", "\n"]), ("a\rb", ["a\r", "b"]),
    ("中文\r\n\r\n```python\nx=1\n\n```", ["中文\r\n", "\r\n", "```python\n", "x=1\n", "\n", "```"]),
    ("a\u2028b", ["a\u2028", "b"]),
])
def test_original_line_endings_and_no_synthetic_last_line(text, expected):
    assert source_lines(text) == expected
    assert "".join(expected) == text
    if expected:
        assert extract_source_lines(text, 1, len(expected)) == text
        for number, line in enumerate(expected, 1):
            assert extract_source_lines(text, number, number) == line


@pytest.mark.parametrize("start,end", [(True, 1), (1, False), (0, 1), (1, 0), (2, 1),
                                           (1, 3), ("1", 1), (1, 1.0)])
def test_invalid_direct_api_ranges_are_rejected(start, end):
    with pytest.raises(ValueError):
        extract_source_lines("a\nb", start, end)


def test_empty_source_and_non_text_are_rejected_for_spans():
    with pytest.raises(ValueError):
        extract_source_lines("", 1, 1)
    with pytest.raises(ValueError):
        source_lines(["line"])
