# NFL Recruiting Strategies

## Overperformer quadrant visualization

The script `analysis/visualizations/quadrant_overperformers.py` creates an interactive Plotly HTML chart at `outputs/visualizations/overperformer_quadrant.html`.

### Scoring logic and assumptions

- **Player-level deduplication**: source data is season-grain, so rows are grouped to one record per player using `NFL_id` when available and a normalized `Player` name fallback.
- **Combine score**:
  - Uses `40yd`, `Vertical`, `Bench`, `Broad Jump`, `3Cone`, `Shuttle`, `Ht`, and `Wt`.
  - Height is converted from `feet-inches` to total inches.
  - Timing drills (`40yd`, `3Cone`, `Shuttle`) are sign-inverted so higher is always better.
  - Each combine metric is z-scored **within `Pos`** and averaged to a composite combine score.
- **Production score**:
  - Career production is aggregated as player totals (or included rate stats where available) across NFL seasons.
  - Position-relevant stat families are selected per position group:
    - QB: passing-centered metrics (+ rushing contribution)
    - Skill positions (RB/FB/WR/TE): rushing + receiving (+ return yards)
    - Defensive positions: tackles/sacks/INT/pass defenses/forced fumbles
    - Specialists (K/P/LS): kicking/punting/return outputs
  - Chosen production components are z-scored within `Pos` and averaged to a composite production score.
- **Normalization**: final combine and production composites are both re-z-scored within `Pos` to keep cross-position comparisons centered around 0.
- **Filters in HTML**: position, drafted vs undrafted, and combine year min/max sliders are applied client-side.

### Run

```bash
python analysis/visualizations/quadrant_overperformers.py
```


## Standardized effect-size dotplot workflow

`src/visuals/effect_size_dotplot.py` expects a **tidy five-column effect table** with:

- `position_group`: modeled position bucket used for paneling
- `metric`: combine metric label shown on the y-axis
- `estimate`: standardized marginal effect estimate
- `ci_low`: lower confidence interval bound
- `ci_high`: upper confidence interval bound

This format is intentionally narrow so chart code stays simple and reusable regardless of model internals.

### 1) Run modeling to produce feature effects

```bash
python - <<'PY'
import pandas as pd
from src.modeling.position_models import run_position_modeling_workflow

df = pd.read_csv("NFL_data/combine_with_college_stats.csv", low_memory=False)
run_position_modeling_workflow(df, output_dir="outputs/modeling")
PY
```

### 2) Convert model outputs to the tidy five-column CSV

Use the runner file `src/visuals/prepare_effects_tidy.py`:

```bash
python src/visuals/prepare_effects_tidy.py outputs/modeling/feature_effects.csv \
  --output-csv outputs/model_effects/standardized_effects.csv
```

You can also point it directly at raw player data and it will automatically run modeling first, then build the tidy five-column file:

```bash
python src/visuals/prepare_effects_tidy.py NFL_data/combine_with_college_stats.csv \
  --model-output-dir outputs/modeling \
  --output-csv outputs/model_effects/standardized_effects.csv
```

By default this keeps standardized combine features (`*_z`) and excludes pooled/intercept/missing-indicator rows.

> Note on missing college stats: the position modeling workflow does **not** require college-stat columns for target construction. It uses the production-value components in `src/scoring/config/production_value_config.json` (e.g., starts, approximate_value, snap_share, seasons_active) with configured imputation for missing values. High missingness in college-stat fields therefore does not directly break this analysis pipeline.

### 3) Build the chart

```bash
python src/visuals/effect_size_dotplot.py outputs/model_effects/standardized_effects.csv \
  --heuristic-version 1 --model-version 1
```

Outputs:

- `outputs/visualizations/effect_size_dotplot.svg`
- `outputs/visualizations/effect_size_dotplot.pdf`
