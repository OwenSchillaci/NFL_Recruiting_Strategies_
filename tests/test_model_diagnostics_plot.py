import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.visuals.model_diagnostics import (
    DiagnosticsThresholds,
    build_model_diagnostics_figure,
    export_diagnostics_assets,
)


class ModelDiagnosticsPlotTests(unittest.TestCase):
    def test_build_and_export_assets(self):
        rng = np.random.default_rng(42)
        n = 180
        positions = np.array(["WR", "DB", "RB"])
        pos = positions[np.arange(n) % len(positions)]
        pred = rng.normal(3.6, 0.35, size=n)
        noise = rng.normal(0, 0.45, size=n)
        bias = np.where(pos == "RB", -0.12, np.where(pos == "DB", 0.06, 0.0))
        actual = pred + noise + bias

        df = pd.DataFrame(
            {
                "position_group": pos,
                "predicted_production_value": pred,
                "target_production_value": actual,
                "residual": actual - pred,
            }
        )

        fig, metrics, warnings = build_model_diagnostics_figure(
            predictions=df,
            thresholds=DiagnosticsThresholds(max_abs_mean_residual=0.05),
            calibration_bins=6,
            title="Test diagnostics",
        )

        self.assertGreater(metrics.shape[0], 0)
        self.assertIsInstance(warnings, list)

        with tempfile.TemporaryDirectory() as td:
            out = export_diagnostics_assets(fig, metrics, warnings, Path(td) / "diag")
            for path in out.values():
                self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
