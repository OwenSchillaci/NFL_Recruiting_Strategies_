# One-Pager Build Runbook

## Purpose
`src/report/build_onepager.py` assembles the final one-page submission PDF:

- Enforces a one-page US Letter template with one-inch margins.
- Uses Arial-equivalent sans serif text at 10pt or larger.
- Places two visual sections:
  - Effect-size panel.
  - Diagnostics mini-panel.
- Adds model/heuristic explanatory text and an auto-generated metadata footer.
- Runs preflight assertions after PDF creation.

## Expected Inputs

1. **Effect-size panel (PDF)**
   - Default: `outputs/visualizations/effect_size_dotplot.pdf`
2. **Diagnostics panel (PDF)**
   - Default: `outputs/visualizations/model_diagnostics.pdf`
3. **Model metadata (JSON)**
   - Default: `outputs/modeling/metadata.json`
   - Used for `heuristic_version` and `model_version` footer fields.
4. **Predictions CSV (optional, but recommended)**
   - Default: `outputs/modeling/predictions.csv`
   - Used to derive `data_cutoff_date` from max `combine_year` (formatted as `YYYY-12-31`).

If `--data-cutoff-date` is provided, it overrides derived cutoff logic.

## Output

- Final PDF: `output/NFL_recruiting_strategy_onepager.pdf`

## Build Commands

### Preferred (Make target)

```bash
make build-onepager
```

### Direct script invocation

```bash
python src/report/build_onepager.py \
  --effect-panel-pdf outputs/visualizations/effect_size_dotplot.pdf \
  --diagnostics-panel-pdf outputs/visualizations/model_diagnostics.pdf \
  --metadata-json outputs/modeling/metadata.json \
  --predictions-csv outputs/modeling/predictions.csv \
  --output-pdf output/NFL_recruiting_strategy_onepager.pdf
```

## Preflight Checks Performed

The script fails fast if any required input is missing and then asserts:

1. **Template constraints**
   - One-inch margins (template constant).
   - Body/footer text >= 10pt.
2. **Output PDF checks**
   - Exactly one page.
   - US Letter page size (8.5 x 11).

## Troubleshooting

- `FileNotFoundError`: generate upstream visuals/model outputs first.
- `AssertionError` from preflight: verify the report template constants were not modified.
- PDF parsing issues: validate source panel PDFs are not truncated/corrupted.
