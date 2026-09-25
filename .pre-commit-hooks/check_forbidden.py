#!/usr/bin/env python3
"""Refuse to commit secrets, infra details, or employer references.

This repo is public. pre-commit runs this over every staged text file
and fails the commit when a line looks like a credential, an internal
hostname, an SSH config for real infrastructure, or a string the private
denylist says must never be published.

The employer-specific strings deliberately do not live in this file: a
denylist in a public repo announces exactly what it is hiding. They come
from the private dotfiles layer instead, and a missing denylist is an
error rather than a skip -- a guard that quietly turns itself off is
worse than no guard, because you stop checking by hand.

Put `allow-forbidden` in a comment on a line to exempt that line.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ALLOW_PRAGMA = "allow-forbidden"
DENYLIST_ENV_VAR = "DOTFILES_DENYLIST"
# Dot-prefixed so rcm leaves it alone: rcm symlinks every plain
# top-level entry of a DOTFILES_DIR into $HOME, and this file has
# no business being ~/.pre-commit-denylist.txt.
DENYLIST_FILENAME = ".pre-commit-denylist.txt"

# Same precedence as DOTFILES_DIRS in rcrc, minus this public repo --
# the denylist itself is not publishable.
DENYLIST_SEARCH_DIRS = (
    Path.home() / ".dotfiles-local",
    Path.home() / ".dotfiles-private",
)

COMMENT_MARKER = "#"
REGEX_DELIMITER = "/"
MAX_EXCERPT_CHARS = 120
MIN_SECRET_CHARS = 16

EXIT_CLEAN = 0
EXIT_FOUND = 1
EXIT_MISCONFIGURED = 2

_LONG_VALUE = r"[\"']?[A-Za-z0-9/+_.=-]{" + str(MIN_SECRET_CHARS) + r",}"


@dataclass(frozen=True)
class Rule:
    """One thing that must not reach a public commit."""

    name: str
    pattern: re.Pattern[str]
    hint: str


@dataclass(frozen=True)
class Finding:
    path: str
    line_number: int
    rule: Rule
    excerpt: str


GENERIC_RULES: tuple[Rule, ...] = (
    Rule(
        name="private key",
        pattern=re.compile(
            r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"
        ),
        hint="private keys live in ~/.ssh, never in a repo",
    ),
    Rule(
        name="ssh host key",
        pattern=re.compile(
            r"\b(?:ssh-rsa|ssh-ed25519|ssh-dss|ecdsa-sha2-nistp\d+)"
            r"\s+AAAA[\w+/=]{20,}"
        ),
        hint="known_hosts and authorized_keys name real machines",
    ),
    Rule(
        name="ssh config for real infrastructure",
        pattern=re.compile(
            r"^\s*(?:ProxyJump|ProxyCommand|IdentityFile|IdentityAgent"
            r"|CertificateFile|LocalForward|RemoteForward"
            r"|DynamicForward)\b",
            re.IGNORECASE,
        ),
        hint="keep ssh_config in ~/.dotfiles-private",
    ),
    Rule(
        name="bastion host",
        pattern=re.compile(
            r"\b(?:bastion|jump-?box|jump-?host)\b", re.IGNORECASE
        ),
        hint="keep ssh_config in ~/.dotfiles-private",
    ),
    Rule(
        name="internal hostname",
        pattern=re.compile(
            r"\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*"
            r"\.(?:internal|intranet|intra|corp|lan|consul|vpc)\b",
            re.IGNORECASE,
        ),
        hint="internal DNS names map out the private network",
    ),
    Rule(
        name="kubernetes service address",
        pattern=re.compile(
            r"\b[a-z0-9-]+\.[a-z0-9-]+\.svc(?:\.cluster\.local)?\b",
            re.IGNORECASE,
        ),
        hint="cluster-internal addresses map out the private network",
    ),
    Rule(
        name="private IP address",
        pattern=re.compile(
            r"(?<![\d.])"
            r"(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))"
            r"\.\d{1,3}\.\d{1,3}(?!\d)"
        ),
        hint="RFC 1918 addresses identify hosts on a real network",
    ),
    Rule(
        name="credential assignment",
        pattern=re.compile(
            r"(?:api[_-]?key|secret[_-]?key|access[_-]?token"
            r"|auth[_-]?token|client[_-]?secret|private[_-]?token"
            r"|password|passwd)\s*[:=]\s*" + _LONG_VALUE,
            re.IGNORECASE,
        ),
        hint="read secrets from the environment or a private file",
    ),
    # Vendor-shaped tokens: a hit here is a live credential, not a
    # near-miss, so the hint says revoke rather than move.
    Rule(
        name="vendor API key",
        pattern=re.compile(
            r"\b(?:AKIA[0-9A-Z]{16}"
            r"|ASIA[0-9A-Z]{16}"
            r"|gh[pousr]_[A-Za-z0-9]{16,}"
            r"|github_pat_[A-Za-z0-9_]{20,}"
            r"|xox[abposr]-[A-Za-z0-9-]{10,}"
            r"|sk-(?:proj-)?[A-Za-z0-9_-]{20,}"
            r"|sk_(?:live|test)_[A-Za-z0-9]{16,}"
            r"|glpat-[A-Za-z0-9_-]{20,}"
            r"|npm_[A-Za-z0-9]{36}"
            r"|dop_v1_[a-f0-9]{64}"
            r"|AIza[0-9A-Za-z_-]{35})\b"
        ),
        hint="revoke this credential; it has been on disk in the clear",
    ),
)


class DenylistError(Exception):
    """The private denylist is missing or unusable."""


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filenames",
        nargs="*",
        help="files to scan; pre-commit passes the staged ones",
    )
    parser.add_argument(
        "--check-denylist",
        action="store_true",
        help=(
            "only verify that the denylist exists and parses, then "
            "exit; pre-commit runs this once per commit so a missing "
            "denylist reports one error rather than one per file batch"
        ),
    )
    parser.add_argument(
        "--denylist",
        type=Path,
        default=None,
        help=(
            "denylist file to use instead of the one found in the "
            "private dotfiles layer"
        ),
    )
    return parser.parse_args(argv)


def find_denylist(override: Path | None) -> Path:
    """Locate the denylist, preferring an explicit override.

    Raises DenylistError rather than returning None: scanning without
    the private strings would pass a commit that should have failed, so
    an unreadable or absent denylist has to stop the commit.
    """
    explicit = override or os.environ.get(DENYLIST_ENV_VAR)
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise DenylistError(f"{path} does not exist")

        return path

    for directory in DENYLIST_SEARCH_DIRS:
        candidate = directory / DENYLIST_FILENAME
        if candidate.is_file():
            return candidate

    searched = ", ".join(
        str(directory / DENYLIST_FILENAME)
        for directory in DENYLIST_SEARCH_DIRS
    )
    raise DenylistError(
        f"no denylist found (looked in {searched}). Create one, or "
        f"point {DENYLIST_ENV_VAR} at it. One entry per line: a literal "
        f"string, or {REGEX_DELIMITER}regex{REGEX_DELIMITER}."
    )


def compile_denylist_entry(entry: str) -> re.Pattern[str]:
    """Turn one denylist line into a pattern.

    A bare word is matched on word boundaries, which is what a company
    or product name needs. Wrapping it in slashes opts into a raw
    regex for the cases a word boundary gets wrong -- an email address,
    say, whose dots and @ are not word characters.
    """
    is_regex = (
        len(entry) > 2
        and entry.startswith(REGEX_DELIMITER)
        and entry.endswith(REGEX_DELIMITER)
    )
    if is_regex:
        return re.compile(entry[1:-1], re.IGNORECASE)

    return re.compile(rf"\b{re.escape(entry)}\b", re.IGNORECASE)


def load_denylist(path: Path) -> tuple[Rule, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise DenylistError(f"cannot read {path}: {error}") from error

    rules: list[Rule] = []

    for number, raw in enumerate(lines, start=1):
        entry = raw.split(COMMENT_MARKER, 1)[0].strip()
        if not entry:
            continue

        try:
            pattern = compile_denylist_entry(entry)
        except re.error as error:
            raise DenylistError(
                f"{path}:{number}: bad pattern: {error}"
            ) from error

        rules.append(
            Rule(
                name="denylisted string",
                pattern=pattern,
                hint=f"listed in {path} as unpublishable",
            )
        )

    if not rules:
        raise DenylistError(f"{path} has no entries")

    return tuple(rules)


def overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def scan_line(
    line: str, rules: Sequence[Rule]
) -> list[tuple[Rule, re.Match[str]]]:
    """Return the matches on one line, at most one per span.

    Rules overlap by design -- a work email address is also an employer
    reference -- and reporting both for the same characters only doubles
    the output. First rule wins, so pass the specific ones first.
    """
    hits: list[tuple[Rule, re.Match[str]]] = []
    claimed: list[tuple[int, int]] = []

    for rule in rules:
        for match in rule.pattern.finditer(line):
            if any(overlaps(match.span(), taken) for taken in claimed):
                continue

            claimed.append(match.span())
            hits.append((rule, match))

    return sorted(hits, key=lambda hit: hit[1].start())


def scan_text(
    path: str, text: str, rules: Sequence[Rule]
) -> list[Finding]:
    findings: list[Finding] = []

    for number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_PRAGMA in line:
            continue

        for rule, match in scan_line(line, rules):
            findings.append(
                Finding(
                    path=path,
                    line_number=number,
                    rule=rule,
                    excerpt=match.group(0)[:MAX_EXCERPT_CHARS],
                )
            )

    return findings


def report(findings: Sequence[Finding]) -> None:
    for finding in findings:
        print(
            f"{finding.path}:{finding.line_number}: "
            f"{finding.rule.name}: {finding.excerpt}",
            file=sys.stderr,
        )
        print(f"    {finding.rule.hint}", file=sys.stderr)

    print(
        f"\n{len(findings)} problem(s) found. Move the content to "
        f"~/.dotfiles-private or ~/.dotfiles-local, or add an "
        f"`{ALLOW_PRAGMA}` comment on the line if it is a false "
        f"positive.",
        file=sys.stderr,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        denylist = find_denylist(args.denylist)
        rules = load_denylist(denylist) + GENERIC_RULES
    except DenylistError as error:
        print(f"check-forbidden: {error}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    if args.check_denylist:
        return EXIT_CLEAN

    findings: list[Finding] = []
    has_unreadable_file = False

    for name in args.filenames:
        try:
            text = Path(name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            print(
                f"check-forbidden: cannot scan {name}: {error}",
                file=sys.stderr,
            )
            has_unreadable_file = True
            continue

        findings.extend(scan_text(name, text, rules))

    if findings:
        report(findings)
        return EXIT_FOUND

    if has_unreadable_file:
        return EXIT_MISCONFIGURED

    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
