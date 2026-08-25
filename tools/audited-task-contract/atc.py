#!/usr/bin/env python3
"""Create and validate audited task contract JSON files (D4)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).with_name("schema.json")

ALLOWED_TOP_LEVEL = {
    "objective",
    "acceptance_checks",
    "write_scope",
    "accepted_commit",
    "decisions",
    "failed_approaches",
    "blockers",
    "phase",
    "state_version",
}

PHASES = {"plan", "execute", "audit", "complete", "blocked"}

FORBIDDEN_KEYS = {
    "transcript",
    "transcripts",
    "messages",
    "conversation",
    "chat",
    "kv_cache",
    "kv",
    "tool_dump",
    "tool_output",
    "tool_outputs",
    "raw_tool",
    "raw_tools",
    "secrets",
    "secret",
    "credentials",
    "credential",
    "password",
    "passwords",
    "api_key",
    "api_keys",
    "token",
    "tokens",
}

SUBJECTIVE_WORDS = {
    "awesome",
    "bad",
    "beautiful",
    "best",
    "better",
    "clean",
    "clever",
    "elegant",
    "excellent",
    "good",
    "great",
    "horrible",
    "nice",
    "perfect",
    "poor",
    "robust",
    "simple",
    "terrible",
    "ugly",
    "worse",
    "worst",
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:live|test|proj)-[A-Za-z0-9]{10,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|secret|password)\s*[:=]\s*\S+", re.IGNORECASE),
]

TRANSCRIPT_PATTERNS = [
    re.compile(r"^\s*(?:user|assistant|human|system|tool)\s*:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"<\|(?:im_start|im_end|assistant|user|system)\|>", re.IGNORECASE),
    re.compile(r"\b(?:tool_call|function_call)\s*[:{]", re.IGNORECASE),
]

COMMIT_SHA = re.compile(r"^[0-9a-f]{7,40}$")
WORD = re.compile(r"[A-Za-z]+")


def _load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _template() -> dict[str, Any]:
    return {
        "objective": "Describe the concrete task goal.",
        "acceptance_checks": [
            "python3 tools/audited-task-contract/atc.py validate contract.json exits 0",
        ],
        "write_scope": ["tools/audited-task-contract/"],
        "decisions": [],
        "failed_approaches": [],
        "blockers": [],
        "phase": "plan",
        "state_version": 1,
    }


def _path(path: str) -> str:
    return f"$.{path}" if path else "$"


def _check_type(value: Any, expected: str, path: str, errors: list[str]) -> None:
    type_map = {
        "string": str,
        "integer": int,
        "array": list,
        "object": dict,
    }
    if not isinstance(value, type_map[expected]):
        errors.append(f"{_path(path)}: expected {expected}, got {type(value).__name__}")


def _validate_schema(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    extra = set(data) - ALLOWED_TOP_LEVEL
    if extra:
        errors.append(f"$: unknown top-level fields: {', '.join(sorted(extra))}")

    missing = {"objective", "phase", "state_version"} - set(data)
    if missing:
        errors.append(f"$: missing required fields: {', '.join(sorted(missing))}")

    if "objective" in data:
        _check_type(data["objective"], "string", "objective", errors)
        if isinstance(data["objective"], str):
            if not data["objective"].strip():
                errors.append("$.objective: must not be empty")
            if len(data["objective"]) > 2000:
                errors.append("$.objective: exceeds 2000 characters")

    if "phase" in data:
        _check_type(data["phase"], "string", "phase", errors)
        if isinstance(data["phase"], str) and data["phase"] not in PHASES:
            errors.append(f"$.phase: must be one of {', '.join(sorted(PHASES))}")

    if "state_version" in data:
        _check_type(data["state_version"], "integer", "state_version", errors)
        if isinstance(data["state_version"], int) and data["state_version"] < 1:
            errors.append("$.state_version: must be >= 1")

    if "accepted_commit" in data:
        _check_type(data["accepted_commit"], "string", "accepted_commit", errors)
        if isinstance(data["accepted_commit"], str) and not COMMIT_SHA.match(data["accepted_commit"]):
            errors.append("$.accepted_commit: must be a lowercase git SHA (7-40 hex chars)")

    for field, max_len in (
        ("acceptance_checks", 500),
        ("write_scope", 500),
        ("blockers", 1000),
    ):
        if field not in data:
            continue
        _check_type(data[field], "array", field, errors)
        if not isinstance(data[field], list):
            continue
        for index, item in enumerate(data[field]):
            item_path = f"{field}[{index}]"
            _check_type(item, "string", item_path, errors)
            if isinstance(item, str):
                if not item.strip():
                    errors.append(f"$.{item_path}: must not be empty")
                if len(item) > max_len:
                    errors.append(f"$.{item_path}: exceeds {max_len} characters")

    if "decisions" in data:
        _check_type(data["decisions"], "array", "decisions", errors)
        if isinstance(data["decisions"], list):
            for index, item in enumerate(data["decisions"]):
                base = f"decisions[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"$.{base}: expected object")
                    continue
                extra = set(item) - {"decision", "evidence"}
                if extra:
                    errors.append(f"$.{base}: unknown fields: {', '.join(sorted(extra))}")
                missing = {"decision", "evidence"} - set(item)
                if missing:
                    errors.append(f"$.{base}: missing fields: {', '.join(sorted(missing))}")
                for key, max_len in (("decision", 1000), ("evidence", 2000)):
                    if key in item:
                        _check_type(item[key], "string", f"{base}.{key}", errors)
                        if isinstance(item[key], str):
                            if not item[key].strip():
                                errors.append(f"$.{base}.{key}: must not be empty")
                            if len(item[key]) > max_len:
                                errors.append(f"$.{base}.{key}: exceeds {max_len} characters")

    if "failed_approaches" in data:
        _check_type(data["failed_approaches"], "array", "failed_approaches", errors)
        if isinstance(data["failed_approaches"], list):
            for index, item in enumerate(data["failed_approaches"]):
                base = f"failed_approaches[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"$.{base}: expected object")
                    continue
                extra = set(item) - {"approach", "reason"}
                if extra:
                    errors.append(f"$.{base}: unknown fields: {', '.join(sorted(extra))}")
                missing = {"approach", "reason"} - set(item)
                if missing:
                    errors.append(f"$.{base}: missing fields: {', '.join(sorted(missing))}")
                for key, max_len in (("approach", 1000), ("reason", 2000)):
                    if key in item:
                        _check_type(item[key], "string", f"{base}.{key}", errors)
                        if isinstance(item[key], str):
                            if not item[key].strip():
                                errors.append(f"$.{base}.{key}: must not be empty")
                            if len(item[key]) > max_len:
                                errors.append(f"$.{base}.{key}: exceeds {max_len} characters")

    return errors


def _walk(node: Any, path: str, errors: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_path = f"{path}.{key}" if path else key
            if key.lower() in FORBIDDEN_KEYS:
                errors.append(f"{_path(key_path)}: forbidden field name (D4)")
            _walk(value, key_path, errors)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk(value, f"{path}[{index}]", errors)
    elif isinstance(node, str):
        if len(node) > 4000:
            errors.append(f"{_path(path)}: string exceeds 4000 characters (possible transcript dump)")
        for pattern in SECRET_PATTERNS:
            if pattern.search(node):
                errors.append(f"{_path(path)}: possible secret or credential (D4)")
                break
        for pattern in TRANSCRIPT_PATTERNS:
            if pattern.search(node):
                errors.append(f"{_path(path)}: possible transcript or raw tool dump (D4)")
                break
        words = {match.group(0).lower() for match in WORD.finditer(node)}
        subjective = sorted(words & SUBJECTIVE_WORDS)
        if subjective:
            errors.append(
                f"{_path(path)}: subjective wording not allowed (D4): {', '.join(subjective)}"
            )


def validate_contract(data: dict[str, Any]) -> list[str]:
    errors = _validate_schema(data)
    _walk(data, "", errors)
    return errors


def cmd_create(args: argparse.Namespace) -> int:
    output = Path(args.output)
    if output.exists() and not args.force:
        print(f"error: {output} already exists (use --force)", file=sys.stderr)
        return 1

    payload = _template()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    errors = validate_contract(payload)
    if errors:
        print("warning: template failed self-validation:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)

    print(f"created {output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    target = Path(args.file)
    try:
        with target.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"error: file not found: {target}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {target}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print(f"error: contract root must be a JSON object", file=sys.stderr)
        return 1

    errors = validate_contract(data)
    if errors:
        print(f"invalid: {target}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"valid: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and validate audited task contract JSON files (D4)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Write a starter contract file")
    create.add_argument(
        "output",
        nargs="?",
        default="contract.json",
        help="Output path (default: contract.json)",
    )
    create.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing file",
    )
    create.set_defaults(func=cmd_create)

    validate = subparsers.add_parser("validate", help="Validate a contract file")
    validate.add_argument("file", help="Contract JSON path")
    validate.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _load_schema()  # fail fast if schema.json is missing
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
