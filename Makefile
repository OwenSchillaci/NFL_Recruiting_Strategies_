.PHONY: build-onepager

build-onepager:
	python src/report/build_onepager.py \
		--effect-panel-pdf outputs/visualizations/effect_size_dotplot.pdf \
		--diagnostics-panel-pdf outputs/visualizations/model_diagnostics.pdf \
		--metadata-json outputs/modeling/metadata.json \
		--predictions-csv outputs/modeling/predictions.csv \
		--output-pdf output/NFL_recruiting_strategy_onepager.pdf
