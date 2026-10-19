"""Linting rules for .env files."""

import re
from dataclasses import dataclass

VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SECRET_VALUE = re.compile(
    r"(?i)(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


@dataclass
class Issue:
    line: int
    level: str  # error | warning | info
    code: str
    message: str


def lint_text(text: str) -> list[Issue]:
    issues: list[Issue] = []

    if text.startswith("\ufeff"):
        issues.append(Issue(1, "warning", "W003", "file starts with a BOM"))
        text = text[1:]

    lines = text.splitlines()

    seen: dict[str, int] = {}
    for i, raw in enumerate(lines, 1):
        line = raw
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            issues.append(Issue(i, "error", "E001", "line has no '=' separator"))
            continue

        keypart, _, value = line.partition("=")
        key = keypart.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()

        if not VALID_NAME.match(key):
            issues.append(Issue(i, "error", "E002", f"invalid variable name: {key!r}"))

        if key in seen:
            issues.append(
                Issue(i, "error", "E003", f"duplicate key {key!r} (first on line {seen[key]})")
            )
        else:
            seen[key] = i

        if key and any(c.islower() for c in key):
            issues.append(Issue(i, "info", "I001", f"key {key!r} is not uppercase"))

        v = value.strip()
        if v == "":
            issues.append(Issue(i, "warning", "W001", f"{key} has an empty value"))

        if value != value.rstrip() and not (v.startswith('"') or v.startswith("'")):
            issues.append(Issue(i, "warning", "W004", "trailing whitespace in value"))

        if value.startswith(" ") and not (v.startswith('"') or v.startswith("'")):
            issues.append(Issue(i, "info", "I002", "value has leading space"))

        if SECRET_VALUE.search(value):
            issues.append(Issue(i, "warning", "W002", "value looks like a secret/token"))

        if v.startswith('"') and not (len(v) > 1 and v.endswith('"')):
            issues.append(Issue(i, "error", "E004", "unterminated double-quoted value"))
        if v.startswith("'") and not (len(v) > 1 and v.endswith("'")):
            issues.append(Issue(i, "error", "E005", "unterminated single-quoted value"))

    return issues


def lint_file(path: str) -> list[Issue]:
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    return lint_text(text)