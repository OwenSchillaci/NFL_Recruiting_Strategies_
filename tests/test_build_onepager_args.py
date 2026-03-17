import unittest
from pathlib import Path

from src.report.build_onepager import parse_args


class BuildOnepagerArgTests(unittest.TestCase):
    def test_default_effect_panel_source_is_dotplot(self):
        args = parse_args([])
        self.assertEqual(args.effect_panel_source, "dotplot")
        self.assertIsNone(args.effect_panel_pdf)

    def test_effect_panel_source_can_be_heatmap(self):
        args = parse_args(["--effect-panel-source", "heatmap"])
        self.assertEqual(args.effect_panel_source, "heatmap")

    def test_explicit_effect_panel_pdf_is_supported(self):
        args = parse_args(["--effect-panel-pdf", "custom/effects.pdf"])
        self.assertEqual(args.effect_panel_pdf, Path("custom/effects.pdf"))


if __name__ == "__main__":
    unittest.main()
