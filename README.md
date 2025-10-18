# LinkedIn Demographic Data Collection Pipeline

## Overview
This tool collects digital behavioral data via LinkedIn's ad audience API (proxy for user demographics/interests) and integrates with World Bank demographics for analysis. Designed for CSS research on data quality and digital societies.

## Key Features
- **Data Collection**: Web API tracking for behavioral segments.
- **Pipeline**: Reproducible (cached, logged, validated).
- **Extensibility**: Config-driven; add mobile/browser extensions easily.
- **Research**: Outputs insights on penetration rates, e.g., expat communities.

## Setup
1. `pip install -r requirements.txt`
2. Create YAML files for cookies/headers (sensitive; use env vars in prod).
3. `python scripts/run_pipeline.py --locations "Germany,Italy" --cookies-file config/cookies.yaml --headers-file config/headers.yaml`

## Outputs
- CSVs: Raw/processed data.
- PNG: Visualizations.
- Logs: In console/file.

## Data Quality
- Caching prevents API overuse.
- Flags low counts (<100).
- Validation: Cross-checks with WB totals.

## Future Work
- Integrate Selenium for dynamic ads.
- Add data donation simulation.
- Dissertation Tie-in: Validate ad data as CSS method for societal transformation.