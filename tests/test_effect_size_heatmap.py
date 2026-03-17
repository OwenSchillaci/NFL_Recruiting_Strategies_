import unittest

import pandas as pd

from src.visuals.effect_size_heatmap import build_effect_size_heatmap
from src.visuals.effect_size_dotplot import prepare_effects_for_plot


class EffectSizeHeatmapTests(unittest.TestCase):
    def setUp(self):
        self.effects = pd.DataFrame(
            {
                "position_group": ["WR", "RB", "WR", "RB"],
                "metric": ["speed", "speed", "size", "size"],
                "estimate": [0.50, 0.10, -0.20, -0.40],
                "ci_low": [0.20, -0.10, -0.30, -0.60],
                "ci_high": [0.80, 0.30, -0.05, -0.10],
            }
        )

    def test_prepare_effects_sorts_by_global_mean_absolute_effect(self):
        prepared = prepare_effects_for_plot(self.effects)
        metric_order = (
            prepared[["metric", "metric_order"]]
            .drop_duplicates()
            .sort_values("metric_order")["metric"]
            .tolist()
        )
        self.assertEqual(metric_order, ["size", "speed"])

    def test_heatmap_contains_matrix_and_uncertainty_overlay(self):
        fig = build_effect_size_heatmap(
            effects_df=self.effects,
            heuristic_version="h1",
            model_version="m1",
        )

        self.assertEqual(len(fig.data), 2)
        heatmap = fig.data[0]
        markers = fig.data[1]

        self.assertEqual(list(heatmap.x), ["RB", "WR"])
        self.assertEqual(list(heatmap.y), ["size", "speed"])
        self.assertEqual(heatmap.z[0][0], -0.40)
        self.assertEqual(heatmap.z[1][1], 0.50)
        self.assertEqual(markers.name, "CI includes zero")
        self.assertEqual(len(markers.x), 1)
        self.assertEqual(markers.x[0], "RB")
        self.assertEqual(markers.y[0], "speed")


if __name__ == "__main__":
    unittest.main()
