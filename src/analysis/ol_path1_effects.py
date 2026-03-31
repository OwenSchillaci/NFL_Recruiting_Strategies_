"""Build ranked OL Path 1 feature effects from model outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

INPUT_PATH = Path("outputs/modeling/feature_effects.csv")
OUTPUT_PATH = Path("outputs/analysis/ol_path1_ranked_effects.csv")


def _resolve_ci_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Return confidence interval column names present in the dataframe."""

    if {"conf.low", "conf.high"}.issubset(df.columns):
        return "conf.low", "conf.high"
    if {"ci_lower", "ci_upper"}.issubset(df.columns):
        return "ci_lower", "ci_upper"

    raise ValueError(
        "Expected either conf.low/conf.high or ci_lower/ci_upper columns in "
        "outputs/modeling/feature_effects.csv"
    )


def build_ranked_ol_effects(input_path: Path = INPUT_PATH) -> pd.DataFrame:
    """Filter OL standardized effects and rank by absolute estimate magnitude."""

    effects = pd.read_csv(input_path, low_memory=False)
    ci_low_col, ci_high_col = _resolve_ci_columns(effects)

    ol_ranked = (
        effects.loc[
            (effects["position_group"] == "OL") & (effects["feature"].str.endswith("_z", na=False))
        ]
        .copy()
        .assign(abs_estimate=lambda d: d["estimate"].abs())
        .sort_values("abs_estimate", ascending=False)
    )

    return (
        ol_ranked.loc[:, ["feature", "estimate", ci_low_col, ci_high_col, "abs_estimate"]]
        .rename(columns={ci_low_col: "conf.low", ci_high_col: "conf.high"})
        .reset_index(drop=True)
    )


def main() -> None:
    ranked = build_ranked_ol_effects()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(ranked)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
