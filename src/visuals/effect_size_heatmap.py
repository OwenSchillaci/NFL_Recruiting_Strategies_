"""Generate position-level standardized effect size heatmaps.

This module builds a metric x position heatmap from tidy model effect output with
columns:
    - position_group
    - metric
    - estimate
    - ci_low
    - ci_high

Cells encode effect-size estimates while an overlaid marker indicates confidence
intervals that include zero.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.visuals.effect_size_dotplot import prepare_effects_for_plot

REQUIRED_COLUMNS = {"position_group", "metric", "estimate", "ci_low", "ci_high"}


def _validate_input_columns(effects_df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(effects_df.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(
            "Input effects table is missing required columns: "
            f"{missing_columns}."
        )


def build_effect_size_heatmap(
    effects_df: pd.DataFrame,
    heuristic_version: str,
    model_version: str,
    chart_title: str = "Standardized Combine Metric Effects on NFL Production Value by Position",
) -> go.Figure:
    """Construct a metric-by-position effect-size heatmap figure."""

    _validate_input_columns(effects_df)
    plot_df = prepare_effects_for_plot(effects_df)

    positions: list[str] = sorted(plot_df["position_group"].unique())
    metric_order = (
        plot_df[["metric", "metric_order"]]
        .drop_duplicates()
        .sort_values("metric_order")["metric"]
        .tolist()
    )

    if not positions or not metric_order:
        raise ValueError("Input effects table is empty after validation.")

    matrix_df = (
        plot_df.pivot_table(
            index="metric",
            columns="position_group",
            values="estimate",
            aggfunc="mean",
        )
        .reindex(index=metric_order, columns=positions)
    )

    uncertainty_df = (
        plot_df.assign(ci_includes_zero=lambda d: (d["ci_low"] <= 0) & (d["ci_high"] >= 0))
        .pivot_table(
            index="metric",
            columns="position_group",
            values="ci_includes_zero",
            aggfunc="max",
        )
        .reindex(index=metric_order, columns=positions)
        .fillna(False)
    )

    z_values = matrix_df.to_numpy(dtype=float)
    max_abs = float(np.nanmax(np.abs(z_values))) if np.isfinite(z_values).any() else 1.0
    z_limit = max(0.1, max_abs)

    fig = go.Figure()
    fig.add_trace(
        go.Heatmap(
            x=positions,
            y=metric_order,
            z=z_values,
            zmid=0,
            zmin=-z_limit,
            zmax=z_limit,
            colorscale="RdBu",
            reversescale=True,
            colorbar={"title": "Std. marginal effect"},
            hovertemplate=(
                "Position: %{x}<br>"
                "Metric: %{y}<br>"
                "Estimate: %{z:.3f}<extra></extra>"
            ),
        )
    )

    marker_y, marker_x = np.where(uncertainty_df.to_numpy(dtype=bool))
    if marker_x.size:
        fig.add_trace(
            go.Scatter(
                x=[positions[idx] for idx in marker_x],
                y=[metric_order[idx] for idx in marker_y],
                mode="markers",
                marker={"symbol": "x", "size": 10, "color": "#1f1f1f", "line": {"width": 1}},
                name="CI includes zero",
                hovertemplate=(
                    "Position: %{x}<br>"
                    "Metric: %{y}<br>"
                    "Uncertainty marker: CI includes zero<extra></extra>"
                ),
            )
        )

    subtitle = f"Heuristic version: {heuristic_version} · Model version: {model_version}"
    fig.update_layout(
        title={"text": f"{chart_title}<br><sup>{subtitle}</sup>", "x": 0.02, "xanchor": "left"},
        template="plotly_white",
        width=max(900, 100 * len(positions) + 320),
        height=max(500, 34 * len(metric_order) + 210),
        margin={"l": 150, "r": 70, "t": 150, "b": 80},
    )
    fig.update_xaxes(title_text="Position group")
    fig.update_yaxes(title_text="Metric", autorange="reversed")

    return fig


def export_figure(fig: go.Figure, output_stem: Path) -> tuple[Path, Path]:
    """Export the figure to both SVG and PDF vector formats."""

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    svg_path = output_stem.with_suffix(".svg")
    pdf_path = output_stem.with_suffix(".pdf")

    fig.write_image(str(svg_path))
    fig.write_image(str(pdf_path))

    return svg_path, pdf_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create position-level standardized combine effect-size heatmaps."
    )
    parser.add_argument("input_csv", type=Path, help="Path to tidy effects CSV.")
    parser.add_argument(
        "--output-stem",
        type=Path,
        default=Path("outputs/visualizations/effect_size_heatmap"),
        help="Output file stem (without extension).",
    )
    parser.add_argument(
        "--heuristic-version",
        required=True,
        help="Heuristic version label to embed in subtitle.",
    )
    parser.add_argument(
        "--model-version",
        required=True,
        help="Model version label to embed in subtitle.",
    )
    parser.add_argument(
        "--title",
        default="Standardized Combine Metric Effects on NFL Production Value by Position",
        help="Chart title.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)

    effects_df = pd.read_csv(args.input_csv)
    fig = build_effect_size_heatmap(
        effects_df=effects_df,
        heuristic_version=args.heuristic_version,
        model_version=args.model_version,
        chart_title=args.title,
    )
    svg_path, pdf_path = export_figure(fig, args.output_stem)
    print(f"Saved chart: {svg_path}")
    print(f"Saved chart: {pdf_path}")


if __name__ == "__main__":
    main()
