"""Versioned experiment definitions and one-time preflight resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from skillflow.common.inputs.skill_package import SkillPackage
from skillflow.common.inputs.skill_package import load_skill_package
from skillflow.common.llm.config import LlmConfig
from skillflow.common.llm.config import LlmConfigError
from skillflow.common.llm.config import load_environment

PositiveInt = Annotated[int, Field(strict=True, gt=0)]
NonnegativeInt = Annotated[int, Field(strict=True, ge=0)]


class Definition(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NamedDefinition(Definition):
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

    @field_validator("id")
    @classmethod
    def portable_id(cls, value: str) -> str:
        reserved = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }
        if value.upper() in reserved:
            raise ValueError("identifier is a reserved filesystem name")
        return value


class CaseDefinition(NamedDefinition):
    input: str = Field(min_length=1)


class DatasetDefinition(Definition):
    cases: list[CaseDefinition] = Field(min_length=1)

    @field_validator("cases")
    @classmethod
    def unique_cases(cls, cases):
        _unique_ids(cases)
        return cases


class VariantDefinition(NamedDefinition):
    model: str | None = Field(default=None, min_length=1)
    endpoint: str | None = Field(default=None, pattern=r"^https?://\S+$")
    reasoning_effort: str | None = None
    timeout_ms: PositiveInt | None = None
    max_retries: NonnegativeInt | None = None
    retry_base_ms: PositiveInt | None = None
    retry_max_backoff_ms: PositiveInt | None = None
    api_key_env: str = Field(default="LLM_API_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    max_repair_rounds: NonnegativeInt = 3

    @field_validator("model", "reasoning_effort")
    @classmethod
    def nonblank_override(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("explicit configuration must not be blank")
        return value


class ExperimentDefinition(Definition):
    name: str
    dataset: str = Field(min_length=1)
    repetitions: PositiveInt = 1
    variants: list[VariantDefinition] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def portable_name(cls, value):
        return NamedDefinition(id=value).id

    @field_validator("variants")
    @classmethod
    def unique_variants(cls, variants):
        _unique_ids(variants)
        return variants


def _unique_ids(items) -> None:
    ids = [item.id.casefold() for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError(
            "IDs must be unique, including on case-insensitive filesystems"
        )


@dataclass(frozen=True)
class ResolvedCase:
    id: str
    source: Path
    package: SkillPackage = field(repr=False)
    sha256: str


@dataclass(frozen=True)
class ResolvedVariant:
    id: str
    config: LlmConfig
    api_key_env: str
    max_repair_rounds: int

    def snapshot(self) -> dict:
        return {
            "id": self.id,
            "api_key_env": self.api_key_env,
            "max_repair_rounds": self.max_repair_rounds,
            **{
                name: getattr(self.config, name)
                for name in self.config.__dataclass_fields__
                if name != "api_key" and getattr(self.config, name) is not None
            },
        }


@dataclass(frozen=True)
class ResolvedExperiment:
    definition: ExperimentDefinition
    config_path: Path
    dataset_path: Path
    cases: tuple[ResolvedCase, ...]
    variants: tuple[ResolvedVariant, ...]
    secrets: tuple[str, ...] = field(repr=False)


def _relative_to_file(value: str, file: Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else file.parent / path).resolve()


def _read_definition(model: type[Definition], path: Path):
    try:
        return model.model_validate_json(path.read_text(encoding="utf-8-sig"))
    except ValidationError as error:
        # Pydantic's default display includes rejected input values, which may
        # include a mistakenly embedded API key. Diagnostics need locations only.
        issues = [
            f"{'.'.join(map(str, item['loc'])) or 'definition'}: {item['msg']}"
            for item in error.errors(include_input=False, include_context=False)
        ]
        raise ValueError(f"Invalid {path.name}: " + "; ".join(issues)) from None


def resolve_experiment(
    path: str | Path,
    *,
    env_file: str | Path | None = None,
    environ: dict[str, str] | None = None,
) -> ResolvedExperiment:
    """Validate every definition, input and credential before any model request."""
    path = Path(path).expanduser().resolve()
    definition = _read_definition(ExperimentDefinition, path)
    dataset_path = _relative_to_file(definition.dataset, path)
    dataset = _read_definition(DatasetDefinition, dataset_path)
    environment = load_environment(env_file=env_file, environ=environ)
    variants = []
    names = {
        "model": "LLM_MODEL",
        "endpoint": "LLM_ENDPOINT",
        "reasoning_effort": "LLM_REASONING_EFFORT",
        "timeout_ms": "LLM_TIMEOUT",
        "max_retries": "LLM_MAX_RETRIES",
        "retry_base_ms": "LLM_RETRY_BASE_MS",
        "retry_max_backoff_ms": "LLM_RETRY_MAX_BACKOFF_MS",
    }
    for variant in definition.variants:
        overrides = variant.model_dump(
            exclude_none=True, exclude={"id", "api_key_env", "max_repair_rounds"}
        )
        values = {
            **environment,
            **{names[key]: str(value) for key, value in overrides.items()},
            "LLM_API_KEY": environment.get(variant.api_key_env, "").strip(),
        }
        config = LlmConfig.from_env(values)
        if not config.api_key:
            raise LlmConfigError(
                f"variant {variant.id!r} requires {variant.api_key_env}"
            )
        # An endpoint must be a complete, credential-free HTTP URL.
        try:
            address = urlsplit(config.endpoint)
            invalid_endpoint = (
                address.scheme not in {"http", "https"}
                or not address.hostname
                or address.username
                or address.password
                or address.fragment
                or address.port == 0
            )
        except ValueError:
            invalid_endpoint = True
        if invalid_endpoint:
            raise LlmConfigError(f"variant {variant.id!r} has an invalid endpoint")
        variants.append(
            ResolvedVariant(
                variant.id, config, variant.api_key_env, variant.max_repair_rounds
            )
        )
    cases = []
    for case in dataset.cases:
        source = _relative_to_file(case.input, dataset_path)
        package = load_skill_package(source)
        # Hash what extraction actually sees, including file paths, sizes and text.
        canonical = json.dumps(
            package.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        cases.append(
            ResolvedCase(
                case.id, source, package, hashlib.sha256(canonical.encode()).hexdigest()
            )
        )
    secrets = tuple(
        sorted({variant.config.api_key for variant in variants}, key=len, reverse=True)
    )
    return ResolvedExperiment(
        definition, path, dataset_path, tuple(cases), tuple(variants), secrets
    )
