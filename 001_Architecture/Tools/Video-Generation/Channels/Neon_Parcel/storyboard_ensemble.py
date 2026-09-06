#!/usr/bin/env python3
"""Combine independent storyboard inspections under an explicit review policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_POLICY = {
    "manual_review_required": True,
    "require_provider_agreement": True,
    "agent_review_required": True,
    "never_auto_clear": True,
    "never_auto_reject": True,
    "user_decision_required": True,
}


def load_policy(path: Path | None = None) -> dict[str, bool]:
    """Load storyboard review policy; missing policy defaults to safest mode."""
    if path is None or not Path(path).is_file():
        return dict(DEFAULT_POLICY)
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("storyboard review policy must be an object")
    policy = dict(DEFAULT_POLICY)
    for field in DEFAULT_POLICY:
        if field in value and not isinstance(value[field], bool):
            raise ValueError(f"storyboard review policy field must be boolean: {field}")
        if field in value:
            policy[field] = value[field]
    return policy


def combine_reports(gemini: dict[str, Any], qwen: dict[str, Any], *, manual_review_required: bool) -> dict[str, Any]:
    """Require manual review when enabled or when provider decisions disagree."""
    if not isinstance(gemini, dict) or not isinstance(qwen, dict):
        raise ValueError("provider reports must be objects")
    gemini_status = gemini.get("status")
    qwen_status = qwen.get("status")
    if gemini_status not in {"pass", "fail", "manual_review"} or qwen_status not in {"pass", "fail", "manual_review"}:
        raise ValueError("provider reports must already be normalized by storyboard_qa")
    disagreement = gemini_status != qwen_status
    if manual_review_required or disagreement:
        status = "manual_review"
    else:
        status = gemini_status
    return {
        "status": status,
        "manual_review_required": manual_review_required,
        "provider_disagreement": disagreement,
        "agent_review_required": True,
        "never_auto_clear": True,
        "never_auto_reject": True,
        "user_decision_required": True,
        "providers": {"gemini": gemini, "qwen": qwen},
        "findings": [
            {"provider": provider, **finding}
            for provider, report in (("gemini", gemini), ("qwen", qwen))
            for finding in report.get("findings", [])
        ],
    }


def combine_with_policy(
    gemini: dict[str, Any], qwen: dict[str, Any], policy: dict[str, bool] | None = None
) -> dict[str, Any]:
    """Apply the production policy while keeping disagreement fail-closed."""
    resolved = dict(DEFAULT_POLICY) if policy is None else policy
    if not isinstance(resolved.get("manual_review_required"), bool):
        raise ValueError("manual_review_required must be boolean")
    result = combine_reports(
        gemini,
        qwen,
        manual_review_required=resolved["manual_review_required"],
    )
    if resolved.get("require_provider_agreement", True) and result["provider_disagreement"]:
        result["status"] = "manual_review"
    result["policy"] = resolved
    return result
