"""Only explicit candidate diagnostics are eligible for mechanical correction."""
import pytest

from skillflow.common.validation import StructuralValidationError, structural_error, validation_at


def test_diagnostics_are_isolated_and_located_without_reclassifying_errors():
    rows = [{"code": "scope", "path": "/value", "message": "outside scope", "context": {"locals": ["a"]}}]
    error = StructuralValidationError(rows)
    rows[0]["context"]["locals"].append("b")
    assert error.diagnostics[0]["context"]["locals"] == ["a"]
    with pytest.raises(StructuralValidationError) as caught:
        with validation_at("/candidate"):
            raise error
    assert caught.value.diagnostics[0]["path"] == "/candidate/value"
    original = ValueError("implementation invariant")
    with pytest.raises(ValueError) as caught:
        with validation_at("/candidate"):
            raise original
    assert caught.value is original
    assert not isinstance(caught.value, StructuralValidationError)


def test_helper_has_stable_json_fields():
    error = structural_error("target", "/goals/0", "wrong target", allowed=["input", "output"])
    assert error.diagnostics == [{"code": "target", "path": "/goals/0", "message": "wrong target",
                                  "context": {"allowed": ["input", "output"]}}]


@pytest.mark.parametrize("value", [[], {}, [{"code": "x", "path": "bad", "message": "x"}],
                                  [{"path": "", "message": "x"}]])
def test_bad_diagnostic_is_a_program_error(value):
    with pytest.raises(TypeError):
        StructuralValidationError(value)
