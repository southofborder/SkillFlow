"""Joint annotation opts into JSON Output without changing other stages."""
from copy import deepcopy
from dataclasses import asdict

import pytest

from skillflow.common.llm.config import LlmConfig
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.config import annotation_public_config


def test_annotation_derives_immutable_llm_config_and_public_fields():
    base = LlmConfig(api_key="injected-secret", model="fixture-model")
    derived = annotation_config(base)
    assert base.response_format is None and derived.response_format == "json_object"
    assert derived is not base
    assert {k: v for k, v in asdict(derived).items() if k != "response_format"} == {
        k: v for k, v in asdict(base).items() if k != "response_format"}
    public = annotation_public_config(base)
    assert public["response_format"] == "json_object" and "api_key" not in public


@pytest.mark.parametrize("base", [{}, {"model": "fixture", "response_format": None},
                                  {"response_format": "json_object"}])
def test_mapping_derivation_is_explicit_and_non_mutating(base):
    before = deepcopy(base)
    derived = annotation_config(base)
    assert derived["response_format"] == "json_object"
    assert base == before and derived is not base


@pytest.mark.parametrize("bad", ["text", "json_schema", {}, False])
def test_existing_conflicting_config_is_rejected(bad):
    with pytest.raises(ValueError, match="requires response_format"):
        annotation_config({"response_format": bad})


def test_environment_does_not_globally_enable_json_output():
    config = LlmConfig.from_env({"LLM_API_KEY": "fixture", "LLM_RESPONSE_FORMAT": "json_object"})
    assert config.response_format is None


def test_annotation_and_review_accept_the_same_public_request_configuration():
    from skillflow.propagation.annotation.runner import _config as annotation_run_config
    from skillflow.propagation.review.runner import _config as review_run_config
    public = annotation_public_config(LlmConfig(api_key="test-only-value"))
    assert annotation_run_config(public) == review_run_config(public) == public
    for invalid in (dict(public, api_key="must-not-be-recorded"), dict(public, invented_parameter=True)):
        for prepare_config in (annotation_run_config, review_run_config):
            with pytest.raises(ValueError):
                prepare_config(invalid)


def test_annotation_cli_preparation_and_factory_share_explicit_json_config(monkeypatch, tmp_path):
    from skillflow.propagation.annotation import __main__ as cli
    from skillflow.propagation.annotation import runner
    from skillflow.common import recording
    base = LlmConfig(api_key="test-only-value", model="fixture")
    monkeypatch.setattr(LlmConfig, "from_env", lambda **kwargs: base)
    seen = []
    def prepare(*args, **kwargs):
        seen.append(("prepare", kwargs["config"]))
        return {"preparation_status": "ready"}
    def factory(config, **kwargs):
        seen.append(("factory", config))
        return object(), ()
    def run(*args, **kwargs):
        seen.append(("run", kwargs["config"]))
        return {"status": "complete", "reason": "fixture"}
    monkeypatch.setattr(runner, "prepare_run", prepare)
    monkeypatch.setattr(runner, "run_annotation", run)
    monkeypatch.setattr(recording, "streaming_factory", factory)
    assert cli.main(["prepare", "--input", str(tmp_path), "--analysis", str(tmp_path / "analysis.json"),
                     "--run-dir", str(tmp_path / "run")]) == 0
    assert cli.main(["run", "--run-dir", str(tmp_path / "run")]) == 0
    assert [stage for stage, _ in seen] == ["prepare", "factory", "run"]
    assert all(config == seen[0][1] and config["response_format"] == "json_object" for _, config in seen)
    assert base.response_format is None
