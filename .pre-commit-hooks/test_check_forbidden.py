#!/usr/bin/env python3
"""Tests for check_forbidden.py.

Run with `python3 .pre-commit-hooks/test_check_forbidden.py` from the
repo root. Stdlib only, so a fresh machine can run them before pytest
or anything else is installed.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

HOOK_PATH = Path(__file__).with_name("check_forbidden.py")

_spec = importlib.util.spec_from_file_location("check_forbidden", HOOK_PATH)
assert _spec is not None and _spec.loader is not None
check_forbidden = importlib.util.module_from_spec(_spec)
sys.modules["check_forbidden"] = check_forbidden
_spec.loader.exec_module(check_forbidden)


def scan(line: str) -> list[str]:
    """Return the names of the generic rules that fire on one line."""
    findings = check_forbidden.scan_text(
        "sample", line, check_forbidden.GENERIC_RULES
    )
    return [finding.rule.name for finding in findings]


class GenericRuleTests(unittest.TestCase):
    def test_flags_private_key_header(self) -> None:
        header = "-----BEGIN OPENSSH PRIVATE KEY-----"
        self.assertIn("private key", scan(header))

    def test_flags_ssh_host_key(self) -> None:
        line = "example.com ssh-ed25519 AAAA" + "B" * 40
        self.assertIn("ssh host key", scan(line))

    def test_flags_ssh_forwarding_directive(self) -> None:
        self.assertIn(
            "ssh config for real infrastructure",
            scan("    ProxyJump gateway"),
        )

    def test_flags_identity_file(self) -> None:
        self.assertIn(
            "ssh config for real infrastructure",
            scan("IdentityFile ~/.ssh/id_ed25519"),
        )

    def test_ignores_prose_mentioning_a_directive(self) -> None:
        # The rule is anchored so documentation can name directives;
        # any host in such a line is caught by the hostname rules.
        self.assertEqual(scan("# see ProxyJump in ssh_config(5)"), [])

    def test_flags_bastion_host(self) -> None:
        self.assertIn("bastion host", scan("Host bastion-01"))
        self.assertIn("bastion host", scan("alias j='ssh jumpbox'"))

    def test_flags_internal_hostname(self) -> None:
        self.assertIn("internal hostname", scan("db01.internal"))
        self.assertIn("internal hostname", scan("host web.corp"))
        self.assertIn("internal hostname", scan("vault.service.consul"))

    def test_allows_dot_local_dotfile_names(self) -> None:
        # The layering convention leans on .local everywhere, so it
        # must never look like an internal TLD.
        self.assertEqual(scan("source ~/.zshrc.local"), [])
        self.assertEqual(scan('DOTFILES_DIRS="$HOME/.dotfiles-local"'), [])

    def test_allows_words_ending_in_a_tld_substring(self) -> None:
        self.assertEqual(scan("syntax/ruby.lang"), [])
        self.assertEqual(scan("corporate.example.com"), [])

    def test_flags_kubernetes_service_address(self) -> None:
        self.assertIn(
            "kubernetes service address",
            scan("api.default.svc.cluster.local"),
        )

    def test_flags_private_ip_addresses(self) -> None:
        for address in ("10.1.2.3", "192.168.0.10", "172.20.4.5"):
            with self.subTest(address=address):
                self.assertIn("private IP address", scan(address))

    def test_allows_loopback_and_public_addresses(self) -> None:
        for address in ("127.0.0.1", "0.0.0.0", "8.8.8.8", "172.15.0.1"):
            with self.subTest(address=address):
                self.assertEqual(scan(address), [])

    def test_allows_version_numbers(self) -> None:
        # A leading digit or dot means this is not an octet boundary.
        self.assertEqual(scan("pyenv 1.10.0.0"), [])
        self.assertEqual(scan("v2.192.168.1"), [])

    def test_flags_credential_assignment(self) -> None:
        line = 'export API_KEY="abcdef0123456789xyz"'
        self.assertIn("credential assignment", scan(line))

    def test_allows_empty_and_short_assignments(self) -> None:
        self.assertEqual(scan('password = ""'), [])
        self.assertEqual(scan("export EDITOR=vim"), [])

    def test_flags_vendor_api_keys(self) -> None:
        tokens = (
            "AKIAIOSFODNN7EXAMPLE",
            "ghp_" + "a" * 36,
            "xoxb-1234567890-abcdefghij",
            "glpat-" + "b" * 20,
            "AIza" + "c" * 35,
        )
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn("vendor API key", scan(f"token: {token}"))

    def test_clean_line_produces_nothing(self) -> None:
        self.assertEqual(scan("export -U PATH"), [])


class AllowPragmaTests(unittest.TestCase):
    def test_pragma_exempts_its_own_line(self) -> None:
        line = "ping 10.0.0.1  # allow-forbidden: router on my LAN"
        self.assertEqual(scan(line), [])

    def test_pragma_does_not_exempt_other_lines(self) -> None:
        text = "# allow-forbidden\nping 10.0.0.1\n"
        findings = check_forbidden.scan_text(
            "sample", text, check_forbidden.GENERIC_RULES
        )
        self.assertEqual([f.line_number for f in findings], [2])


class OverlapTests(unittest.TestCase):
    def test_overlapping_matches_report_once(self) -> None:
        specific = check_forbidden.Rule(
            name="specific",
            pattern=re.compile(r"secret@example\.com"),
            hint="",
        )
        broad = check_forbidden.Rule(
            name="broad", pattern=re.compile(r"example"), hint=""
        )
        hits = check_forbidden.scan_line(
            "mail secret@example.com now", (specific, broad)
        )
        self.assertEqual([rule.name for rule, _ in hits], ["specific"])

    def test_separate_matches_both_report(self) -> None:
        rules = (
            check_forbidden.Rule(
                name="first", pattern=re.compile(r"aaa"), hint=""
            ),
            check_forbidden.Rule(
                name="second", pattern=re.compile(r"bbb"), hint=""
            ),
        )
        hits = check_forbidden.scan_line("aaa and bbb", rules)
        self.assertEqual([rule.name for rule, _ in hits], ["first", "second"])


class DenylistTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.tmp = Path(self._temp.name)

    def write_denylist(self, body: str) -> Path:
        path = self.tmp / "denylist.txt"
        path.write_text(body, encoding="utf-8")
        return path

    def test_literal_entry_matches_on_word_boundary(self) -> None:
        rules = check_forbidden.load_denylist(
            self.write_denylist("acmecorp\n")
        )
        findings = check_forbidden.scan_text(
            "sample", "works at AcmeCorp today", rules
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].excerpt, "AcmeCorp")

    def test_literal_entry_ignores_substring_matches(self) -> None:
        rules = check_forbidden.load_denylist(self.write_denylist("acme\n"))
        findings = check_forbidden.scan_text("sample", "acmeish", rules)
        self.assertEqual(findings, [])

    def test_slash_wrapped_entry_is_a_regex(self) -> None:
        rules = check_forbidden.load_denylist(
            self.write_denylist("/[\\w.]+@acme\\.example/\n")
        )
        findings = check_forbidden.scan_text(
            "sample", "email a.person@acme.example", rules
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].excerpt, "a.person@acme.example")

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        rules = check_forbidden.load_denylist(
            self.write_denylist("# heading\n\nacme  # trailing\n")
        )
        self.assertEqual(len(rules), 1)

    def test_empty_denylist_is_an_error(self) -> None:
        path = self.write_denylist("# nothing but a comment\n")
        with self.assertRaises(check_forbidden.DenylistError):
            check_forbidden.load_denylist(path)

    def test_bad_regex_is_an_error(self) -> None:
        path = self.write_denylist("/[unclosed/\n")
        with self.assertRaises(check_forbidden.DenylistError):
            check_forbidden.load_denylist(path)

    def test_missing_denylist_is_an_error(self) -> None:
        with self.assertRaises(check_forbidden.DenylistError):
            check_forbidden.find_denylist(self.tmp / "absent.txt")

    def test_override_wins_over_search_path(self) -> None:
        path = self.write_denylist("acme\n")
        self.assertEqual(check_forbidden.find_denylist(path), path)


class MainTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.tmp = Path(self._temp.name)
        self.denylist = self.tmp / "denylist.txt"
        self.denylist.write_text("acmecorp\n", encoding="utf-8")

    def run_main(self, body: str) -> int:
        target = self.tmp / "candidate.txt"
        target.write_text(body, encoding="utf-8")
        return check_forbidden.main(
            ["--denylist", str(self.denylist), str(target)]
        )

    def test_clean_file_exits_clean(self) -> None:
        self.assertEqual(
            self.run_main("export -U PATH\n"), check_forbidden.EXIT_CLEAN
        )

    def test_denylisted_string_fails(self) -> None:
        self.assertEqual(
            self.run_main("# built at AcmeCorp\n"),
            check_forbidden.EXIT_FOUND,
        )

    def test_secret_fails(self) -> None:
        self.assertEqual(
            self.run_main("aws_key = AKIAIOSFODNN7EXAMPLE\n"),
            check_forbidden.EXIT_FOUND,
        )

    def test_missing_denylist_is_not_a_pass(self) -> None:
        exit_code = check_forbidden.main(
            ["--denylist", str(self.tmp / "absent.txt"), __file__]
        )
        self.assertEqual(exit_code, check_forbidden.EXIT_MISCONFIGURED)

    def test_check_denylist_accepts_a_valid_denylist(self) -> None:
        exit_code = check_forbidden.main(
            ["--check-denylist", "--denylist", str(self.denylist)]
        )
        self.assertEqual(exit_code, check_forbidden.EXIT_CLEAN)

    def test_check_denylist_rejects_a_missing_denylist(self) -> None:
        exit_code = check_forbidden.main(
            ["--check-denylist", "--denylist", str(self.tmp / "absent.txt")]
        )
        self.assertEqual(exit_code, check_forbidden.EXIT_MISCONFIGURED)

    def test_unreadable_file_is_not_a_pass(self) -> None:
        exit_code = check_forbidden.main(
            ["--denylist", str(self.denylist), str(self.tmp / "gone.txt")]
        )
        self.assertEqual(exit_code, check_forbidden.EXIT_MISCONFIGURED)


if __name__ == "__main__":
    unittest.main()
