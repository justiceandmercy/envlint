"""Command-line interface for envlint."""

import argparse
import os
import sys

from .rules import Issue, lint_file


def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in sorted(files):
                    if fn.startswith(".env"):
                        out.append(os.path.join(root, fn))
        else:
            out.append(p)
    return out


def format_issue(issue: Issue) -> str:
    return f"  line {issue.line}: [{issue.level}] {issue.code} {issue.message}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="envlint", description="Lint .env files for common mistakes."
    )
    parser.add_argument("paths", nargs="*", default=[".env"])
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    parser.add_argument("--version", action="version", version="envlint 0.1.0")
    args = parser.parse_args(argv)

    files = collect(args.paths)
    exit_code = 0
    total_issues = 0
    for path in files:
        try:
            issues = lint_file(path)
        except OSError as exc:
            print(f"{path}: error reading file: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        if not issues:
            print(f"{path}: ok")
            continue
        print(f"{path}:")
        for issue in issues:
            print(format_issue(issue))
        total_issues += len(issues)
        if any(i.level == "error" for i in issues):
            exit_code = 1
        elif args.strict and any(i.level == "warning" for i in issues):
            exit_code = 1

    if total_issues:
        print(f"\n{total_issues} issue(s) found.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())