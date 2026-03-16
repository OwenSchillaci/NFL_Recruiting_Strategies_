"""Prepare tidy five-column effect tables for visualization.

Converts modeling outputs (e.g., `outputs/modeling/feature_effects.csv`) into the
five-column tidy schema required by `effect_size_dotplot.py`:

    position_group, metric, estimate, ci_low, ci_high
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.modeling.position_models import PositionModelingConfig, run_position_modeling_workflow

REQUIRED_MODEL_COLUMNS = {
    "position_group",
    "feature",
    "estimate",
    "ci_lower",
    "ci_upper",
}


def _validate_model_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_MODEL_COLUMNS - set(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(
            "Input model-effects file is missing required columns: "
            f"{missing_cols}."
        )


def prepare_tidy_effects(
    model_effects_df: pd.DataFrame,
    include_pooled: bool = False,
    include_missing_indicators: bool = False,
    include_intercept: bool = False,
) -> pd.DataFrame:
    """Transform model feature effects into tidy five-column chart input.

    By default, this keeps only standardized combine features (`*_z`) and drops
    pooled, intercept, and missingness-indicator rows.
    """

    _validate_model_columns(model_effects_df)

    tidy = model_effects_df.copy()

    if not include_pooled:
        tidy = tidy.loc[tidy["position_group"] != "POOLED"]

    feature_mask = tidy["feature"].str.endswith("_z", na=False)
    if include_missing_indicators:
        feature_mask = feature_mask | tidy["feature"].str.endswith("_missing", na=False)
    if include_intercept:
        feature_mask = feature_mask | tidy["feature"].eq("intercept")

    tidy = tidy.loc[feature_mask, ["position_group", "feature", "estimate", "ci_lower", "ci_upper"]].copy()
    tidy = tidy.rename(
        columns={
            "feature": "metric",
            "ci_lower": "ci_low",
            "ci_upper": "ci_high",
        }
    )

    tidy["metric"] = tidy["metric"].str.replace("_z$", "", regex=True)

    return tidy.sort_values(["position_group", "metric"]).reset_index(drop=True)


RAW_COMBINE_REQUIRED_COLUMNS = {
    "Pos",
    "Ht",
    "Wt",
    "40yd",
    "Vertical",
    "Bench",
    "Broad Jump",
    "3Cone",
    "Shuttle",
}
RAW_TARGET_REQUIRED_COLUMNS = {"career_year", "starts", "approximate_value", "snap_share", "seasons_active"}


def _raw_modeling_missing_columns(df: pd.DataFrame) -> list[str]:
    """List missing columns needed to run modeling from raw player data."""

    missing = set()
    cols = set(df.columns)
    missing |= RAW_COMBINE_REQUIRED_COLUMNS - cols

    # Target can come from precomputed production_value OR scoring inputs.
    if "production_value" not in cols:
        missing |= RAW_TARGET_REQUIRED_COLUMNS - cols

    return sorted(missing)


def load_or_generate_model_effects(
    input_csv: Path,
    model_output_dir: Path,
    model_version: str,
    bootstrap_iterations: int,
    min_group_size: int,
) -> pd.DataFrame:
    """Load feature effects directly, or generate them from raw player data.

    If `input_csv` already has feature-effect columns, it is returned directly.
    Otherwise, if it looks like raw player data with combine columns, the
    position modeling workflow is executed and the generated
    `feature_effects.csv` is loaded from `model_output_dir`.
    """

    source_df = pd.read_csv(input_csv, low_memory=False)
    if REQUIRED_MODEL_COLUMNS.issubset(set(source_df.columns)):
        return source_df

    missing = _raw_modeling_missing_columns(source_df)
    if missing:
        raise ValueError(
            "Input is neither a model-effects file nor valid raw player data. "
            f"Missing raw-data columns: {missing}"
        )

    config = PositionModelingConfig(
        model_version=model_version,
        bootstrap_iterations=bootstrap_iterations,
        min_group_size=min_group_size,
    )
    run_position_modeling_workflow(df=source_df, output_dir=model_output_dir, config=config)
    feature_effects_path = model_output_dir / "feature_effects.csv"
    if not feature_effects_path.exists():
        raise FileNotFoundError(f"Modeling completed but no feature effects were found at {feature_effects_path}")
    return pd.read_csv(feature_effects_path, low_memory=False)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert model feature effects CSV into tidy five-column chart input."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help=(
            "Path to either model effects CSV (outputs/modeling/feature_effects.csv) "
            "or raw player dataset (e.g., NFL_data/combine_with_college_stats.csv)."
        ),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("outputs/model_effects/standardized_effects.csv"),
        help="Output path for tidy five-column effects CSV.",
    )
    parser.add_argument(
        "--model-output-dir",
        type=Path,
        default=Path("outputs/modeling"),
        help=(
            "Directory for generated modeling outputs when input_csv is raw player data. "
            "Ignored when input_csv is already a model-effects file."
        ),
    )
    parser.add_argument(
        "--model-version",
        default="v1.0.0",
        help="Model version label to use if modeling is run from raw player data.",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=200,
        help="Bootstrap iterations to use if modeling is run from raw player data.",
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=30,
        help="Minimum position-group sample size to use if modeling is run from raw player data.",
    )
    parser.add_argument(
        "--include-pooled",
        action="store_true",
        help="Include POOLED rows in output.",
    )
    parser.add_argument(
        "--include-missing-indicators",
        action="store_true",
        help="Include *_missing features in output.",
    )
    parser.add_argument(
        "--include-intercept",
        action="store_true",
        help="Include intercept rows in output.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)

    model_effects_df = load_or_generate_model_effects(
        input_csv=args.input_csv,
        model_output_dir=args.model_output_dir,
        model_version=args.model_version,
        bootstrap_iterations=args.bootstrap_iterations,
        min_group_size=args.min_group_size,
    )
    tidy = prepare_tidy_effects(
        model_effects_df=model_effects_df,
        include_pooled=args.include_pooled,
        include_missing_indicators=args.include_missing_indicators,
        include_intercept=args.include_intercept,
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(args.output_csv, index=False)

    print(f"Saved tidy effects: {args.output_csv}")
    print("Columns:", ", ".join(tidy.columns.tolist()))
    print(f"Rows: {len(tidy)}")


if __name__ == "__main__":
    main()
