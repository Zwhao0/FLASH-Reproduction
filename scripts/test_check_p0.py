"""Adversarial fixtures for the publication checker; no infrastructure mutation."""
import tempfile
import unittest
from pathlib import Path
from check_p0 import REQUIRED, check


class PublicationFixtures(unittest.TestCase):
    def test_adversarial_publication_inputs(self):
        cases = [
            ("readme.md", "# Example\n\n[local](missing.md)\n", "unpublished local link"),
            ("服务器.md", "# Private\n", "publication exclusion"),
            ("reference.pdf", "not a PDF\n", "publication exclusion"),
            ("docs/note.md", "# Example\n\n" + "/" + "Users/example/private/\n", "sensitive content shape"),
            ("docs/note.md", "# Example  \n", "newline or trailing whitespace"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, body, expected in cases:
                with self.subTest(case=expected, name=name):
                    p = root / name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(body)
                    self.assertTrue(any(expected in error for error in check(root, {name}, require=False)))

    def test_regular_local_link(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "README.md").write_text("# Example\n\n[local](docs/note.md)\n")
            (root / "docs/note.md").write_text("# Note\n")
            self.assertEqual([], check(root, {"README.md", "docs/note.md"}, require=False))

    def test_symlink_to_private_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "private-source").write_text("withheld\n")
            (root / "README.md").symlink_to(root / "private-source")
            self.assertTrue(any("not a regular file" in e for e in check(root, {"README.md"}, require=False)))

    def test_requirement_identity_regressions(self):
        ids = [f"F-ITEM-{i:02}" for i in range(1, 17)]
        cases = [
            ("valid", ids, ids, False),
            ("duplicate contract", ids[:-1] + [ids[0]], ids, True),
            ("duplicate trace", ids, ids + [ids[0]], True),
            ("missing", ids, ids[:-1], True),
            ("mismatch", ids, ids[:-1] + ["F-OTHER-99"], True),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in REQUIRED:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("# Fixture\n")
            for label, contract_ids, trace_ids, should_fail in cases:
                with self.subTest(case=label):
                    (root / "docs/PAPER_CONTRACT.md").write_text(
                        "# Contract\n" + "".join(f"\n### {key}：Example\n" for key in contract_ids))
                    (root / "docs/TRACEABILITY.md").write_text(
                        "# Trace\n" + "".join(f"\n| {key} | planned | NOT_RUN |\n" for key in trace_ids))
                    errors = check(root, set(REQUIRED))
                    self.assertEqual(should_fail, bool(errors))
                    if should_fail:
                        self.assertTrue(any("requirement IDs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
