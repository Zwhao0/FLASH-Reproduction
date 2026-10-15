#!/usr/bin/env python3
"""Offline publication hygiene and document structure checks, not scientific tests."""
import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED = (
    "AGENTS.md", "README.md", "docs/STATE.md", "docs/SOURCES.md",
    "docs/PAPER_CONTRACT.md", "docs/TRACEABILITY.md", "docs/DECISIONS.md",
    "docs/GREYHOUND_COMPARISON.md", "docs/GITHUB_POLICY.md", "docs/ROADMAP.md",
    "docs/evidence/P0_VALIDATION.md",
)
DENIED_PARTS = {".local", "private", "secrets", "raw", "node_modules"}
DENIED_SUFFIXES = {".pdf", ".png", ".jpg", ".log", ".pem", ".key", ".so", ".o"}
# Match sensitive shapes without printing matching contents.
SENSITIVE = (
    re.compile(r"/(?:Users|home)/[^/\s]+/"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bssh\s+(?:[^\s]+\s+)*[^\s@]+@[^\s]+"),
)


def check(root, names, require=True):
    errors = []
    bodies = {}
    if require:
        errors.extend(f"missing required file: {name}" for name in REQUIRED if name not in names)
    for name in sorted(names):
        rel = Path(name)
        if (rel.is_absolute() or ".." in rel.parts or DENIED_PARTS.intersection(rel.parts)
                or any(p.startswith(".local-") for p in rel.parts)
                or rel.suffix.lower() in DENIED_SUFFIXES or rel.name.startswith(".env")
                or rel.name == "服务器.md"):
            errors.append(f"publication exclusion: {name}")
            continue
        path = root / rel
        if path.is_symlink() or not path.is_file():
            errors.append(f"not a regular file: {name}")
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"non UTF-8 file: {name}")
            continue
        bodies[name] = body
        if any(pattern.search(body) for pattern in SENSITIVE):
            errors.append(f"sensitive content shape: {name}")
        if not body.endswith("\n") or any(line.rstrip() != line for line in body.splitlines()):
            errors.append(f"newline or trailing whitespace: {name}")
        if rel.suffix == ".md":
            if not body.startswith("# "):
                errors.append(f"missing document title: {name}")
            # Deliberately small inline-link dialect; remote URLs are not fetched.
            for link in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", body):
                target = urlsplit(link)
                if target.scheme or target.netloc or not target.path:
                    continue
                candidate = (rel.parent / unquote(target.path)).as_posix()
                import posixpath
                candidate = posixpath.normpath(candidate)
                if candidate.startswith("../") or candidate not in names:
                    errors.append(f"unpublished local link: {name}")
    if require and {"docs/PAPER_CONTRACT.md", "docs/TRACEABILITY.md"}.issubset(bodies):
        contract = bodies["docs/PAPER_CONTRACT.md"]
        trace = bodies["docs/TRACEABILITY.md"]
        contract_ids = re.findall(r"^### (F-[A-Z]+-\d+):|^### (F-[A-Z]+-\d+)：", contract, re.M)
        contract_ids = [a or b for a, b in contract_ids]
        trace_ids = re.findall(r"^\| (F-[A-Z]+-\d+) \|", trace, re.M)
        if (len(contract_ids) != 16 or len(set(contract_ids)) != 16
                or len(trace_ids) != 16 or set(contract_ids) != set(trace_ids)):
            errors.append("requirement IDs missing, duplicated or inconsistent")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    names = set(subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"], text=True).split("\0")) - {""}
    errors = check(root, names)
    if errors:
        print("FAIL: P0 document/publication checks")
        for error in errors:
            print(error)
        return 1
    print(f"PASS: {len(names)} tracked files; required documents, local file links, UTF-8, whitespace, publication exclusions")
    print("Scope: no remote URL/anchor validation, complete secret detection, scientific, GPU or permission enforcement claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
