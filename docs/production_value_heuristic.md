# Production Value Heuristic

This project includes a standalone scoring layer in `src/scoring/production_value.py` that converts raw NFL outcomes into a single `production_value` target.

## Single config entrypoint

The scorer loads one canonical config file:

- `src/scoring/config/production_value_config.json`

Use `load_production_value_config()` to ensure all scoring behavior is controlled from that one file.

## Config schema

Top-level keys:

- `version` *(string)*: reproducibility tag written to `heuristic_version` output.
- `components` *(object)*: each metric includes:
  - `weight` *(float)*
  - `transform` *(identity|log1p|sqrt|square|sigmoid|inverse)*
  - `min` / `max` *(numeric bounds for guardrail validation)*
- `position_overrides` *(object)*: per-position replacement of component weights.
- `time_decay` *(object)*:
  - `career_year_column`
  - `early_career_multiplier`
  - `late_career_multiplier`
  - `early_career_cutoff_year`
  - `late_career_start_year`
- `missing_data` *(object)*:
  - `strategy` = `impute` | `drop` | `cap`
  - optional `impute.method` = `median` | `mean` | `zero`
- `winsorization` *(object)*:
  - `enabled` *(bool)*
  - `lower_quantile`, `upper_quantile`
- `output` *(object)*:
  - `scale`, `offset`
  - `deterministic_sort` (list of stable sort columns)

## Minimal example config (JSON)

```json
{
  "version": "v1-minimal",
  "components": {
    "starts": {"weight": 1.0, "transform": "log1p", "min": 0, "max": 300}
  },
  "position_overrides": {},
  "time_decay": {
    "career_year_column": "career_year",
    "early_career_multiplier": 1.0,
    "late_career_multiplier": 1.0,
    "early_career_cutoff_year": 3,
    "late_career_start_year": 10
  },
  "missing_data": {"strategy": "impute", "impute": {"method": "median"}},
  "winsorization": {"enabled": false},
  "output": {"scale": 1.0, "offset": 0.0, "deterministic_sort": ["Player"]}
}
```

## Advanced example config (YAML)

```yaml
version: v2-advanced
components:
  starts:
    weight: 0.30
    transform: log1p
    min: 0
    max: 300
  approximate_value:
    weight: 0.40
    transform: log1p
    min: 0
    max: 250
  snap_share:
    weight: 0.20
    transform: sigmoid
    min: 0
    max: 1
  seasons_active:
    weight: 0.10
    transform: sqrt
    min: 0
    max: 30
position_overrides:
  QB:
    components:
      approximate_value:
        weight: 0.55
      starts:
        weight: 0.20
  RB:
    components:
      snap_share:
        weight: 0.30
time_decay:
  career_year_column: career_year
  early_career_multiplier: 1.20
  late_career_multiplier: 0.85
  early_career_cutoff_year: 3
  late_career_start_year: 9
missing_data:
  strategy: cap
winsorization:
  enabled: true
  lower_quantile: 0.01
  upper_quantile: 0.99
output:
  scale: 1.0
  offset: 0.0
  deterministic_sort: [Player, Pos]
```

## API

- `compute_production_value(player_row, config)` for a single row.
- `compute_production_value_batch(df, config)` for vectorized deterministic scoring.

Both emit:

- `production_value`
- `heuristic_version`
