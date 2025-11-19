# Retail Labor Demand Forecasting

A fully reproducible Python pipeline for forecasting retail store demand and converting it to labor hour requirements using industry-standard SPLH/IPLH metrics, calibrated against BLS labor productivity benchmarks.

## Overview

This project implements a complete retail labor demand forecasting system that:

1. **Forecasts daily store demand** using Random Forest on the Corporación Favorita dataset
2. **Converts forecasts to labor hours** using SPLH (Sales per Labor Hour) or IPLH (Items per Labor Hour)
3. **Calibrates implied productivity** against BLS labor productivity benchmarks for retail
4. **Generates comprehensive reports** with methodology, results, and sensitivity analysis

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

Execute the entire pipeline with a single command:

```bash
python run_pipeline.py
```

This will run all scripts in sequence:
1. `01_environment_and_data_loading.py` - Load and validate data
2. `02_feature_engineering.py` - Create features for modeling
3. `03_forecasting.py` - Train Random Forest and generate forecasts
4. `04_labor_conversion.py` - Convert to labor hours
5. `05_productivity_calibration.py` - Compare with BLS benchmarks
6. `06_diagnostics.py` - Generate diagnostics and sensitivity analysis
7. `07_generate_report.py` - Create comprehensive Markdown report

### Running Individual Scripts

You can also run scripts individually:

```bash
python 01_environment_and_data_loading.py
python 02_feature_engineering.py
# ... and so on
```

## Configuration

All settings are centralized in `config.py`:

- **Data paths:** Locations of input files
- **Planning parameters:** SPLH/IPLH values, baseline hours
- **Model parameters:** Random Forest hyperparameters, CV splits
- **Output paths:** Where results are saved

### Key Parameters to Adjust

```python
# In config.py

# Choose conversion mode: "SPLH" or "IPLH"
CONVERSION_MODE = "IPLH"

# IPLH target (items per labor hour)
IPLH_PER_STORE = {
    "default": 50.0,  # Adjust based on your operations
}

# SPLH target (sales per labor hour)
SPLH_PER_STORE = {
    "default": 150.0,  # Adjust based on your operations
}

# Baseline fixed hours per day
BASELINE_HOURS_PER_STORE_DAY = 8.0
```

## Project Structure

```
retail_labour_demand/
├── config.py                              # Configuration file
├── requirements.txt                       # Python dependencies
├── run_pipeline.py                        # Main runner script
├── README.md                              # This file
├── 01_environment_and_data_loading.py     # Data loading & EDA
├── 02_feature_engineering.py              # Feature creation
├── 03_forecasting.py                      # Model training
├── 04_labor_conversion.py                 # Labor hour calculation
├── 05_productivity_calibration.py         # BLS comparison
├── 06_diagnostics.py                      # Diagnostics & sensitivity
├── 07_generate_report.py                  # Report generation
├── data/                                  # Input data
│   ├── historical_sales_data/
│   │   ├── sales data-set.csv
│   │   ├── stores data-set.csv
│   │   ├── Features data set.csv
│   │   └── README.md
│   └── labour_productivity.csv
├── output/                                # Generated outputs
│   ├── features_train.csv
│   ├── forecasts.csv
│   ├── hours_actual.csv
│   ├── hours_forecast.csv
│   ├── hours_comparison.csv
│   ├── productivity_analysis.csv
│   ├── sensitivity_analysis.csv
│   ├── feature_importances.csv
│   ├── model_comparison.csv
│   └── visualizations/                    # Plots and charts
└── models/                                # Saved models
    ├── random_forest_model.joblib
    └── feature_names.joblib
```

## Output Files

### Data Files

- **features_train.csv** - Training dataset with engineered features
- **forecasts.csv** - Test set forecasts with actual vs predicted
- **hours_actual.csv** - Actual labor hours (ex-post)
- **hours_forecast.csv** - Forecasted labor hours (ex-ante)
- **hours_comparison.csv** - Side-by-side comparison with deltas
- **productivity_analysis.csv** - Implied productivity metrics
- **sensitivity_analysis.csv** - Sensitivity to parameter changes

### Reports

- **README_report.md** - Comprehensive analysis report with:
  - Methodology and formulas
  - Model performance metrics
  - Productivity analysis
  - Sensitivity analysis
  - Limitations and next steps
  - Full references

### Visualizations

Located in `output/visualizations/`:
- Hours over time (actual vs forecast)
- Hours by store
- Parity plots
- Productivity trends
- BLS comparison
- Sensitivity analysis
- Diagnostic plots

## Key Concepts

### SPLH (Sales per Labor Hour)

$$\text{SPLH} = \frac{\text{Sales (\$)}}{\text{Labor Hours}}$$

Therefore: $\text{Hours} = \frac{\text{Sales}}{\text{SPLH}}$

### IPLH (Items per Labor Hour)

$$\text{IPLH} = \frac{\text{Items (units)}}{\text{Labor Hours}}$$

Therefore: $\text{Hours} = \frac{\text{Items}}{\text{IPLH}}$

### BLS Labor Productivity

$$LP_t = \frac{\text{Real Output}_t}{\text{Hours Worked}_t}$$

This is output per hour (not per worker), using inflation-adjusted output.

## Data Sources

1. **Corporación Favorita:** Historical grocery sales data from Kaggle competition
   - 45 stores across different regions
   - 81 departments
   - Weekly sales from 2010-2012

2. **BLS Labor Productivity:** Bureau of Labor Statistics retail productivity series
   - Industry: Supermarkets and grocery stores (NAICS 445110)
   - Measure: Labor productivity index (2017=100)

## Reproducibility

- All scripts use fixed random seeds (`RANDOM_STATE = 42`)
- Time-based train/test split ensures no data leakage
- All dependencies pinned in requirements.txt
- Configuration centralized in config.py

## Next Steps

Potential enhancements:

1. **Department-level forecasts** with specific IPLH/SPLH by category
2. **Probabilistic forecasts** for uncertainty quantification
3. **Queueing models** (Erlang C) for checkout staffing
4. **Real-time updates** to refine plans intra-day
5. **Task decomposition** modeling hours by specific tasks
6. **Schedule optimization** given forecast hours and constraints

## References

- [Corporación Favorita Dataset](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)
- [BLS Labor Productivity Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)
- [FRED Retail Productivity Data](https://fred.stlouisfed.org/series/IPUHN445L001000000)
- [SPLH/IPLH Definitions](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)

See `README_report.md` (generated after running pipeline) for complete references and detailed analysis.

## License

This project uses publicly available datasets and is for educational/research purposes.
