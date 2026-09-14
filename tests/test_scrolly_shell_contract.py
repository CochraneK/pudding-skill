from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "src/components/ScrollyShell.svelte"
PATTERN = ROOT / "references/single-file-scrolly-pattern.md"


class ScrollyShellContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SHELL.read_text(encoding="utf-8")
        cls.pattern = PATTERN.read_text(encoding="utf-8")

    def test_uses_natural_scroll_observation(self):
        self.assertIn("IntersectionObserver", self.shell)
        self.assertNotIn("scrollTo(", self.shell)
        self.assertNotIn("preventDefault()", self.shell)

    def test_preserves_sticky_step_structure(self):
        self.assertIn("position: sticky", self.shell)
        self.assertIn("data-scrolly-index", self.shell)
        self.assertIn("data-step-id", self.shell)
        self.assertIn("aria-current", self.shell)

    def test_has_mobile_and_reduced_motion_contracts(self):
        self.assertIn("@media (max-width: 56rem)", self.shell)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.shell)
        self.assertIn("50svh", self.shell)

    def test_pattern_keeps_evidence_status_and_no_scrolly_default(self):
        for label in ("OBSERVED", "LITERATURE ESTIMATE", "DERIVED", "SCENARIO", "ASSUMPTION"):
            self.assertIn(label, self.pattern)
        self.assertIn("should **not** be forced into production", self.pattern)
        self.assertIn("Do not learn", self.pattern)


if __name__ == "__main__":
    unittest.main()
