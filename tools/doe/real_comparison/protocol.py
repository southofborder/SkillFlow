"""Shared preregistration and immutable, English experiment policy."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "skillflow-real-comparison-v1"
SEED = 20261020
METHODS = ("skillflow", "audit", "chain")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def write_json(path, value, *, immutable=False):
    path = Path(path)
    content = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if immutable and path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise ValueError(f"Immutable artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def policy():
    return {
        "schema_version": SCHEMA,
        "objective": "Determine whether SkillFlow has an actual comparative benefit, without favoring any method.",
        "purpose_basis": "skill_declared_purpose_only",
        "user_request": None,
        "authorization_limit": "Author statements are not independently verified user authorization. Existing data use is not proof of necessity.",
        "corpus": {"registry": "https://clawhub.ai", "artifact_family": "skills",
                   "sort": "downloads", "roster_size": 1000,
                   "atomic_snapshot": False, "freeze_roster_before_downloads": True,
                   "filter_security_labels": False, "substitute_missing_rank": False,
                   "execute_or_install_downloaded_content": False},
        "selection": {"cases": 24, "reserves": 6, "seed": SEED,
                      "minimum_operational_nonempty_lines": 200,
                      "alternative_cross_referenced_operational_files": 4,
                      "minimum_source_evidenced_features": 2,
                      "max_numbered_bundle_bytes": 262144,
                      "max_reference_tokens": 64000, "reference_encoding": "o200k_base",
                      "reference_encoding_is_runtime_tokenizer": False,
                      "max_per_near_fork_group": 1, "max_per_source_cluster": 3,
                      "minimum_source_clusters": 8, "relax_rules_automatically": False,
                      "replace_after_formal_start": False},
        "source_features": ["cross_file_dataflow", "conditions_or_retries", "versions_or_transformations",
                            "element_or_recipient_pairing", "multiple_receiving_boundaries",
                            "persistence_or_cross_session"],
        "runtime": {"transport": "codex_collaboration_injected", "model": "gpt-6.1-sol",
                    "effort": "ultra", "provider": "openai", "fork_turns": "none",
                    "tools": False, "delegation": False, "follow_up_hints": False,
                    "api_configuration_binding": False, "hard_sandbox": False,
                    "receipt_plaintext_delivery_equality": "unavailable_when_encrypted"},
        "workflows": {"methods": list(METHODS), "repeats": 3, "primary": 216,
                      "independent_reviews": 48, "review_repeat": 1, "results": 264,
                      "calibration_cases": ["gh-fix-ci", "netlify-deploy", "transcribe"],
                      "formal_graph_reuse": False, "manual_semantic_repairs": False,
                      "quality_resampling": False, "final_uncounted_model_polish": False,
                      "no_original_review_policy": "not_reviewable_no_replacement"},
        "budget": {"child_requests": 64, "reported_total_tokens": 8000000,
                   "workflow_seconds": 21600, "outstanding_request_seconds": 2700,
                   "delivered_reference_tokens": 300000,
                   "token_stop": "after_receipt_before_next_dispatch",
                   "unknown_usage": "retain_unknown_and_stop_further_dispatch",
                   "truncate_source_or_requests": False},
        "human_reference": {"independent_verifiers": 2, "required_before_formal": True,
                            "assistant_drafts_are_human_approval": False,
                            "source_only": True, "registry_scores_or_scans_are_gold": False},
        "human_scoring": {"all_results_primary_human": True,
                          "all_errors_and_disputes_secondary_human": True,
                          "initial_pass_secondary_fraction": 0.2, "seed": SEED,
                          "irreconcilable_disagreement": "indeterminate",
                          "reference_corrigendum": "retain_old_and_regrade_all_methods_no_regeneration"},
        "timed_review": {"reviewers": 3, "independent_of_reference_authors": True,
                         "repeat": 1, "assignments": 72, "per_reviewer": 24,
                         "per_method_per_reviewer": 8, "seconds_cap": 1800,
                         "same_case_multiple_methods_per_reviewer": False,
                         "censor_timeouts": True, "quick_wrong_is_efficient": False},
        "primary_endpoint": "All adjudicated supported DOE findings located with material source/payload/version/condition/recipient distinctions, no substantive unsupported claims or functionality-breaking reductions, and concrete source-supported reductions for established reducible excess.",
        "format_reward": False,
        "chain_endpoint": "Secondary semantic completeness and cross-layer consistency; not requested for direct audit.",
        "unknowns": "Abstention on a known supported excess is a miss. Source-justified uncertainty is calibrated uncertainty, never proof of safety.",
        "denominator": "Every planned workflow, including technical failure, missing output, budget exhaustion and protocol violation; completed-only analysis is secondary.",
        "statistics": {"unit": "case", "average_repeats_first": True,
                       "cluster_by_source": True, "paired": True, "bootstrap_samples": 10000,
                       "seed": SEED, "primary_comparisons": [["skillflow", "audit"], ["skillflow", "chain"]],
                       "multiplicity": "Holm", "alpha": 0.05,
                       "practical_accuracy_difference": 0.10,
                       "efficiency_quality_noninferiority_margin": 0.05,
                       "practical_efficiency_reduction": 0.20,
                       "weighted_overall_score": False,
                       "extend_until_significant": False},
        "interpretation": [
            "Direct methods winning or matching are valid outcomes. Do not defend SkillFlow through format, number of fields, or architecture alone.",
            "If one independent direct review removes an apparent benefit, report that explicitly with original-plus-review cost.",
            "Distinguish declared-purpose auditing from independently authorized user-task auditing.",
            "Insufficient adjudicated positives, unresolved references or wide intervals limit the conclusion; do not manufacture positives or reselect cases.",
            "Tokens, currency and human time are separate units. Infer no currency amount without actual billing evidence.",
        ],
        "language": "New prompts, synthetic fixtures, diagnostics, interpretations and reports are English. Genuine source and quotations remain unchanged.",
    }


RUBRIC = """# Common audit rubric, frozen before formal generation

All three methods receive the same declared-purpose audit. An independent user
task is absent. Author instructions are source evidence, not verified user
authorization. Distinguish high-level purpose and required behavior from current
implementation and payload. Include excess payload on necessary actions and
exposures from unnecessary actions. Do not treat a boundary level as DOE.

The common primary endpoint is source-grounded audit adequacy, not a particular
schema, graph, ID, length, or number of fields. Check every adjudicated supported
excess and every material receiving point. A reduction must preserve required
values, conditions, cardinality, quality, recipients and side effects. Unsupported
recipient assertions, invented protection, plaintext claims from possible
influence, and harmful reductions are substantive errors when material.

Match canonical exposure units by source, sensitive scope, version, condition,
recipient and boundary event. Equivalent descriptions receive one credit;
overlapping fields do not create extra credit. A broad claim matches several
units only when it unambiguously covers each. Distinguish an established excess
on a conditional branch from uncertainty about whether it is excess. Do not
duplicate one network delivery as a second external-tool event.

Source-justified uncertainty is not a safety claim. Abstention on a supported
reference finding is a miss. Empty output or failed execution does not yield
perfect precision. Precision is undefined without positive claims. Native partial
status is scored by substantive content; mechanical completion is not semantic
success. Retain every planned workflow in the effectiveness denominator.

Full-chain completeness and consistency are secondary endpoints for SkillFlow
and the full-chain prompt. Direct audit is not required to reproduce that chain.
Preserved source code metadata is not proof that its semantics were modeled.

Two humans independently confirm source references before formal targets. All
264 results receive a primary human check of proposed mappings and reasons. Every
error/dispute and a seeded 20 percent sample of initial passes receive a second
independent human check. Keep unresolved source disputes indeterminate. A genuine
reference correction preserves its old version and requires regrading all arms
and repeats without regenerating answers.

Mask method names, repeats and ordering; disclose incomplete blinding where
artifact structure reveals the method. Preserve exact candidate text and source
evidence. A grader may propose additional source-supported findings, but cannot
silently amend the frozen reference or invent missing interfaces.
"""


def prepare_protocol(run_dir):
    run = Path(run_dir)
    document = policy()
    write_json(run / "protocol.json", document, immutable=True)
    rubric_path = run / "rubric.md"
    if rubric_path.exists() and rubric_path.read_text(encoding="utf-8") != RUBRIC:
        raise ValueError("Frozen rubric differs")
    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    rubric_path.write_text(RUBRIC, encoding="utf-8")
    freeze = {"schema_version": SCHEMA, "policy_sha256": canonical_hash(document),
              "files": {"protocol.json": sha256(run / "protocol.json"), "rubric.md": sha256(rubric_path)}}
    write_json(run / "protocol-freeze.json", freeze, immutable=True)
    return freeze
