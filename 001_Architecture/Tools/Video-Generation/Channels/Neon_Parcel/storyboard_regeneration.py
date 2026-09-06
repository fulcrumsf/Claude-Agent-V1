#!/usr/bin/env python3
"""Cap and audit storyboard candidate regeneration before video handoff."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from storyboard_contract import validate_spec


MAX_ATTEMPTS = 3
TERMINAL_QA_STATUSES = {"pass", "fail", "manual_review"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


class StoryboardAttemptController:
    """Append-only attempt controller for one shot's storyboard candidates."""

    def __init__(
        self,
        state_path: Path,
        shot_id: str,
        *,
        max_attempts: int = MAX_ATTEMPTS,
        archive_dir: Path | None = None,
        active_dir: Path | None = None,
    ) -> None:
        if max_attempts != MAX_ATTEMPTS:
            raise ValueError(f"storyboard regeneration cap is fixed at {MAX_ATTEMPTS}")
        self.state_path = Path(state_path)
        self.shot_id = shot_id
        self.max_attempts = max_attempts
        self.archive_dir = Path(archive_dir) if archive_dir else None
        self.active_dir = Path(active_dir) if active_dir else None
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.state_path.write_text(
                json.dumps({"shot_id": shot_id, "max_attempts": max_attempts, "events": []}, indent=2) + "\n",
                encoding="utf-8",
            )
        self._assert_identity()

    def _load(self) -> dict[str, Any]:
        value = json.loads(self.state_path.read_text(encoding="utf-8"))
        if value.get("shot_id") != self.shot_id:
            raise ValueError("attempt state belongs to a different shot")
        if value.get("max_attempts") != self.max_attempts:
            raise ValueError("attempt state has an incompatible attempt cap")
        if not isinstance(value.get("events"), list):
            raise ValueError("attempt state events must be a list")
        return value

    def _assert_identity(self) -> None:
        self._load()

    def _append(self, event: dict[str, Any]) -> dict[str, Any]:
        state = self._load()
        event = {"timestamp": _now(), "shot_id": self.shot_id, **event}
        state["events"].append(event)
        self.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return event

    def events(self) -> list[dict[str, Any]]:
        return self._load()["events"]

    def attempts(self) -> dict[int, dict[str, Any]]:
        result: dict[int, dict[str, Any]] = {}
        for event in self.events():
            number = event.get("attempt")
            if not isinstance(number, int):
                continue
            attempt = result.setdefault(number, {"attempt": number, "status": "unknown"})
            attempt.update(event)
            if event["event"] == "reserved":
                attempt["status"] = "reserved"
            elif event["event"] == "candidate_generated":
                attempt["status"] = "generated"
            elif event["event"] == "qa_recorded":
                attempt["status"] = event["qa_status"]
            elif event["event"] == "provider_failed":
                attempt["status"] = "provider_failed"
        return result

    def selected_attempt(self) -> int | None:
        selected = [event for event in self.events() if event["event"] == "selected"]
        return selected[-1]["attempt"] if selected else None

    def blocked(self) -> bool:
        return any(event["event"] == "blocked" for event in self.events())

    def reserve_attempt(
        self,
        prompt_path: Path,
        spec_path: Path,
        *,
        retry_reason: str | None = None,
    ) -> int:
        attempts = self.attempts()
        if self.blocked() or self.selected_attempt() is not None:
            raise ValueError("storyboard loop is already terminal")
        if len(attempts) >= self.max_attempts:
            raise ValueError(f"storyboard attempt cap reached: {self.max_attempts}")
        if not Path(prompt_path).is_file() or not Path(spec_path).is_file():
            raise ValueError("prompt and structured spec must exist before reserving an attempt")
        if attempts:
            latest = attempts[max(attempts)]
            if latest.get("status") not in {"fail", "manual_review", "provider_failed"}:
                raise ValueError("previous storyboard candidate has not completed QA")
            if not retry_reason:
                raise ValueError("retry_reason is required after a prior storyboard attempt")
        number = len(attempts) + 1
        self._append(
            {
                "event": "reserved",
                "attempt": number,
                "prompt_path": str(prompt_path),
                "prompt_sha256": _sha256(Path(prompt_path)),
                "spec_path": str(spec_path),
                "spec_sha256": _sha256(Path(spec_path)),
                "retry_reason": retry_reason,
            }
        )
        return number

    def record_generated(self, attempt: int, image_path: Path) -> None:
        current = self.attempts().get(attempt)
        if not current or current.get("status") != "reserved":
            raise ValueError("candidate must be reserved before it is recorded as generated")
        if not Path(image_path).is_file():
            raise ValueError(f"generated storyboard image does not exist: {image_path}")
        self._append(
            {
                "event": "candidate_generated",
                "attempt": attempt,
                "image_path": str(image_path),
                "image_sha256": _sha256(Path(image_path)),
            }
        )

    def record_provider_failure(self, attempt: int, error: str) -> None:
        current = self.attempts().get(attempt)
        if not current or current.get("status") != "reserved":
            raise ValueError("provider failure must follow a reserved attempt")
        self._append(
            {
                "event": "provider_failed",
                "attempt": attempt,
                "error": error,
            }
        )

    def record_qa(self, attempt: int, qa_report: dict[str, Any], qa_path: Path | None = None) -> None:
        current = self.attempts().get(attempt)
        if not current or current.get("status") != "generated":
            raise ValueError("QA must follow a generated candidate")
        status = qa_report.get("status")
        if status not in TERMINAL_QA_STATUSES:
            raise ValueError("QA status must be pass, fail, or manual_review")
        self._append(
            {
                "event": "qa_recorded",
                "attempt": attempt,
                "qa_status": status,
                "qa_path": str(qa_path) if qa_path else None,
                "qa_sha256": _sha256(Path(qa_path)) if qa_path else None,
                "finding_count": len(qa_report.get("findings", [])),
                "findings": qa_report.get("findings", []),
            }
        )

    def archive_candidate(self, attempt: int) -> Path:
        current = self.attempts().get(attempt)
        if not current or current.get("status") not in {"fail", "manual_review", "provider_failed"}:
            raise ValueError("only failed storyboard candidates can be archived")
        source = Path(current.get("image_path", ""))
        if not source.is_file():
            raise ValueError("failed candidate image is missing")
        if self.archive_dir is None:
            raise ValueError("archive_dir is required to archive a candidate")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        destination = self.archive_dir / f"attempt-{attempt:02d}-{source.name}"
        if destination.exists():
            raise FileExistsError(f"archive destination already exists: {destination}")
        shutil.move(str(source), str(destination))
        self._append({"event": "archived", "attempt": attempt, "archive_path": str(destination)})
        return destination

    def select_passing(self, attempt: int) -> Path:
        current = self.attempts().get(attempt)
        if not current or current.get("status") != "pass":
            raise ValueError("only a passing storyboard candidate can be selected")
        source = Path(current.get("image_path", ""))
        if not source.is_file():
            raise ValueError("passing candidate image is missing")
        destination = source
        if self.active_dir is not None:
            self.active_dir.mkdir(parents=True, exist_ok=True)
            destination = self.active_dir / source.name
            if destination.exists():
                raise FileExistsError(f"active storyboard already exists: {destination}")
            shutil.move(str(source), str(destination))
        self._append({"event": "selected", "attempt": attempt, "active_path": str(destination)})
        return destination

    def block(self, reason: str) -> None:
        if len(self.attempts()) < self.max_attempts:
            raise ValueError("cannot block storyboard loop before all candidates are exhausted")
        if self.selected_attempt() is not None:
            raise ValueError("cannot block a storyboard loop with a selected candidate")
        self._append({"event": "blocked", "reason": reason})


def retry_context(qa_report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only recorded findings for the next prompt revision."""
    return [
        {
            "frame": finding.get("frame"),
            "category": finding.get("category"),
            "evidence": finding.get("evidence"),
        }
        for finding in qa_report.get("findings", [])
    ]


def run_storyboard_loop(
    spec: dict[str, Any],
    controller: StoryboardAttemptController,
    generate_candidate: Callable[[dict[str, Any], int, list[dict[str, Any]]], Path],
    evaluate_candidate: Callable[[dict[str, Any], Path], dict[str, Any]],
    *,
    prompt_path_factory: Callable[[int], Path],
    spec_path: Path,
) -> dict[str, Any]:
    """Generate, QA, and select one storyboard candidate, capped at three."""
    validate_spec(spec)
    retry_findings: list[dict[str, Any]] = []
    for attempt in range(1, controller.max_attempts + 1):
        prompt_path = prompt_path_factory(attempt)
        reserved = controller.reserve_attempt(
            prompt_path,
            spec_path,
            retry_reason=("prior QA findings" if attempt > 1 else None),
        )
        try:
            image_path = Path(generate_candidate(spec, reserved, retry_findings))
            controller.record_generated(reserved, image_path)
        except Exception as error:  # provider failures must remain distinct from QA failures
            controller.record_provider_failure(reserved, str(error))
            if attempt == controller.max_attempts:
                controller.block("three storyboard candidate attempts exhausted after provider failure")
                return {"status": "blocked", "reason": "provider_failure", "attempts": controller.attempts()}
            continue

        qa_report = evaluate_candidate(spec, image_path)
        controller.record_qa(reserved, qa_report)
        if qa_report["status"] == "pass":
            active_path = controller.select_passing(reserved)
            return {"status": "pass", "attempt": reserved, "active_path": str(active_path), "qa": qa_report}
        retry_findings = retry_context(qa_report)
        controller.archive_candidate(reserved)

    controller.block("three storyboard candidates failed or required manual review")
    return {"status": "blocked", "reason": "qa_failure", "attempts": controller.attempts()}
