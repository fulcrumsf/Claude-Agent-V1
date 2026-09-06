# Conventions

## Python
- Use type hints, `pathlib.Path`, explicit JSON serialization, and small pure functions where practical.
- CLI entry points use `argparse` and `if __name__ == "__main__":`.
- Invalid state or missing required artifacts raises `ValueError` with an actionable message.
- JSON output is indented and newline-terminated for auditability.

## Production Safety
- Do not overwrite prior attempts.
- Archive superseded prompts/media before promoting replacements.
- Require explicit retry reasons for additional paid attempts.
- Keep human review and provider failure distinct from automatic validation failure.

## Prompt/Artifact Conventions
- Preserve the exact submitted prompt in a file before a paid call.
- Record hashes, shot IDs, versions, provider task IDs, and statuses.
- Keep storyboard/reference-image roles distinct from clean temporal first-frame roles.
- Prefer explicit subject counts, object states, camera continuity, and frame-by-frame action.
