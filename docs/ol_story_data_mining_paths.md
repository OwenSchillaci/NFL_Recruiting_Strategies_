# Offensive Line Recruiting Story: Data-Mining Paths Using Current Data

This guide is tailored for a **time-constrained** workflow where you cannot collect substantial new college-game data.
It uses assets that already exist in this repository: combine measurements, modeled production value, feature effects, diagnostics, and prediction residuals.

## Story framing (one sentence)

> A good offensive lineman is not just "big"—the best signal in this dataset is a blend of movement quality (especially vertical and shuttle within OL cohorts), plus uncertainty-aware scouting to capture overperformers the model misses.

## What you already have (and can use immediately)

- `NFL_data/combine_with_college_stats.csv`: combined athlete-level table including combine metrics and downstream NFL-linked fields.
- `outputs/modeling/feature_effects.csv`: position-group model effects with confidence intervals.
- `outputs/modeling/diagnostics.csv`: model-vs-baseline error by position group.
- `outputs/modeling/predictions.csv`: player-level predictions and residuals for archetype mining.
- `src/modeling/position_models.py`: confirms OL grouping (`OT`, `OG`, `C`, `T`, `G`) and standardized feature construction.

## Recommended data-mining paths for your OL recruiting story

## Path 1 — "What actually matters for OL in this dataset?" (effect-size narrative)

Use OL rows in `feature_effects.csv` and rank standardized combine features by absolute estimate.

**Why this helps the story:**
- Gives your audience a concrete "signal hierarchy" (which metrics matter more/less).
- Avoids causal over-claims because you can present confidence intervals alongside estimates.

**How to mine it quickly:**
1. Filter to `position_group == "OL"`.
2. Keep standardized features ending in `_z`.
3. Rank by `abs(estimate)`.
4. Tag each metric as:
   - **Core signal**: CI mostly away from zero.
   - **Directional hint**: estimate non-zero but CI overlaps zero.

## Path 2 — "How reliable is this model for OL?" (trust-and-limits narrative)

Use `diagnostics.csv` to compare OL error versus baseline pooled model.

**Why this helps the story:**
- Makes your recommendation credible because you disclose model limitations.
- Lets you introduce a "confidence band" for decision-making.

**Quick interpretation template:**
- If OL `mae < baseline_mae` and `rmse < baseline_rmse`, position-specific modeling is adding value.
- Convert error scale into recruiting language (e.g., "expect moderate spread around predicted outcomes").

## Path 3 — "Who beats the model and why?" (archetype narrative)

Use `predictions.csv` residuals to identify OL overperformers and underperformers.

**Why this helps the story:**
- Residuals reveal traits your feature set does not capture (technique, processing, scheme fit, development context).
- Creates compelling examples for "don’t over-index on workouts alone."

**How to mine it quickly:**
1. Filter OL only.
2. Sort by `residual` descending (overperformers) and ascending (underperformers).
3. For each bucket, compare combine profile patterns (height/weight/speed/agility).
4. Convert findings into recruiting guardrails:
   - "High-testing OL still need floor checks."
   - "Mid-testing OL with strong context may outperform projections."

## Path 4 — "Missing-data realism" (operations narrative)

`src/modeling/position_models.py` creates missingness indicators for each combine feature (e.g., `Bench_missing`) and imputes within position group before standardizing.

**Why this helps the story:**
- You can still rank prospects even when some drills are missing.
- You can explicitly de-risk incomplete profiles rather than dropping them.

**How to use in recruiting language:**
- Flag prospects with multiple missing OL-relevant drills as **higher uncertainty** rather than automatic rejects.
- Prioritize additional scouting resources for those uncertainty-heavy profiles.

## Path 5 — "Build a practical OL board" (decision narrative)

Create a simple board combining prediction + uncertainty + residual archetype awareness:

1. Start with `predicted_production_value` (ceiling estimate).
2. Penalize wide intervals (`pred_interval_upper - pred_interval_lower`) as uncertainty cost.
3. Add a "context uplift" score from your overperformer archetype cues.
4. Bucket into:
   - **Priority target**
   - **Value target**
   - **Developmental target**
   - **Avoid / high risk**

This gives you a recruiting process that is data-driven but still scout-compatible.

## If you cannot collect more data, do this now

1. **Freeze this as Version 1**: use only current combine + model outputs.
2. **Add a context checklist column manually** for OL film/traits (technique, anchor, hand usage, mental processing, scheme fit).
3. **Re-rank with a blended score**: model score (quant) + context checklist (qual).
4. **Track outcomes prospectively** so your next cycle improves without needing a full new data pipeline.

## Suggested chapter structure for your story

1. **Myth:** "Good OL are just big and strong."
2. **Evidence:** OL effect sizes show movement traits carry signal too.
3. **Reality check:** model error is non-trivial; uncertainty must be priced in.
4. **Case studies:** overperformers and underperformers.
5. **Playbook:** operational OL recruiting board with uncertainty and context layering.
6. **Roadmap:** what to collect next cycle (only highest ROI fields).

## Highest-ROI "next data" (small additions only)

If you eventually have time for just a little more data, prioritize:

- College starts/snap counts by season (durability + experience proxy).
- Sack/pressure responsibility proxies (even rough public estimates).
- Conference/competition-strength tier.
- Basic injury availability history.

These fields typically improve OL screening more than collecting many extra combine-like features.
