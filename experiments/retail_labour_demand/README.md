# Retail Labor Demand Forecasting Pipeline

A fully reproducible Python pipeline for forecasting retail store demand with Random Forest and converting forecasts to labor hours using SPLH/IPLH productivity metrics, calibrated against BLS industry benchmarks.

## Overview

This project implements a complete workflow for:

1. **Demand Forecasting:** Random Forest model predicting weekly store sales
2. **Labor Conversion:** Transform sales/items into required labor hours using SPLH (Sales Per Labor Hour) or IPLH (Items Per Labor Hour)
3. **Productivity Calibration:** Compare implied store productivity against BLS labor productivity benchmarks for the retail sector

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone or navigate to project directory
cd retail_labour_demand

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Run complete pipeline
python run_all.py
```

This will execute all stages in sequence:
1. Data loading and EDA
2. Feature engineering
3. Model training and forecasting
4. Labor conversion
5. Productivity calibration vs BLS
6. Report generation

### Configuration

Edit `config.py` to customize:

- **Data paths:** Point to your sales, stores, features, and BLS data files
- **SPLH/IPLH values:** Set productivity parameters by store type
- **Model hyperparameters:** Adjust Random Forest settings
- **Planning parameters:** Baseline hours, test period, etc.

## Project Structure

```
retail_labour_demand/
├── README.md                     # This file
├── config.py                     # Configuration and parameters
├── requirements.txt              # Python dependencies
├── run_all.py                   # Master script to run full pipeline
├── data/                         # Input data
│   ├── historical_sales_data/
│   │   ├── sales data-set.csv
│   │   ├── stores data-set.csv
│   │   └── Features data set.csv
│   └── labour_productivity.csv   # BLS benchmark data
├── src/                          # Pipeline scripts
│   ├── 01_setup_and_load.py
│   ├── 02_feature_engineering.py
│   ├── 03_model_training.py
│   ├── 04_labor_conversion.py
│   ├── 05_productivity_calibration.py
│   └── 06_generate_report.py
├── output/                       # Generated outputs
│   ├── features_train.csv
│   ├── forecasts.csv
│   ├── hours_actual.csv
│   ├── hours_forecast.csv
│   ├── hours_comparison.csv
│   └── README_report.md         # Detailed analysis report
└── models/                       # Saved model artifacts
    └── random_forest_model.joblib
```

## Outputs

### CSV Files

- **features_train.csv:** Feature matrix with engineered features
- **forecasts.csv:** Sales forecasts with actuals for test period
- **hours_actual.csv:** Actual sales converted to labor hours
- **hours_forecast.csv:** Forecast sales converted to labor hours
- **hours_comparison.csv:** Side-by-side comparison of actual vs forecast hours

### Report

- **README_report.md:** Comprehensive Markdown report with:
  - Methodology explanation
  - Metrics and formulas
  - Results and findings
  - Productivity calibration analysis
  - Sensitivity analysis
  - Limitations and next steps
  - Full references

### Model Artifacts

- **random_forest_model.joblib:** Trained Random Forest model
- **preprocessor.pkl, scaler.pkl:** Preprocessing pipelines
- **feature_columns.pkl:** Feature names and metadata

## Methodology

### Forecasting

- **Model:** Random Forest Regressor
- **Features:** Calendar (month, week, etc.), lags (7/14/28 weeks), rolling averages, store attributes, external variables (temp, fuel, CPI, unemployment), promotions, holidays
- **Evaluation:** Time-based train/test split (last 8 weeks held out)
- **Metrics:** MAE, RMSE, MAPE, R²

### Labor Conversion

**SPLH (Sales Per Labor Hour):**
```
Labor Hours = Sales ($) / SPLH
```

**IPLH (Items Per Labor Hour):**
```
Labor Hours = Items (units) / IPLH
```

Plus baseline hours for fixed tasks (opening, closing, admin).

### BLS Calibration

Compare implied store productivity (sales per hour, CPI-deflated) against BLS industry labor productivity index for supermarkets (NAICS 445110).

## Key Metrics

### Labor Productivity (BLS Definition)
```
LP = Real Output / Hours Worked
```
Measures output per hour, **not** output per worker.

### SPLH
```
SPLH = Sales ($) / Labor Hours
```

### IPLH
```
IPLH = Items (units) / Labor Hours
```

## Configuration Example

```python
# In config.py

CONVERSION_MODE = "SPLH"  # or "IPLH"

PRODUCTIVITY_BY_STORE_TYPE = {
    "A": {"SPLH": 200.0, "IPLH": 50.0},  # Large stores
    "B": {"SPLH": 180.0, "IPLH": 45.0},  # Medium stores
    "C": {"SPLH": 150.0, "IPLH": 40.0},  # Small stores
}

BASELINE_HOURS_PER_DAY = 8.0  # Fixed tasks
TEST_WEEKS = 8  # Holdout period
```

## Use Cases

1. **Workforce Planning:** Convert sales forecasts to staffing needs
2. **Budget Planning:** Estimate labor costs from demand forecasts
3. **Scenario Analysis:** What-if analysis with different productivity assumptions
4. **Benchmarking:** Compare store productivity to industry norms
5. **Performance Monitoring:** Track actual vs planned hours

## Limitations

- **Sales ≠ Workload:** Not all tasks scale with sales (e.g., shelf resets)
- **SPLH/IPLH Variability:** Productivity varies by mix, layout, processes
- **BLS is Aggregate:** Industry average, not store-specific ground truth
- **Forecast Error Propagates:** Hour plans inherit forecast uncertainty
- **Weekly Granularity:** Dataset is weekly; daily/hourly patterns not captured

## Next Steps

- **Department-Level Models:** Separate models per department for task-specific productivity
- **Probabilistic Forecasts:** Quantile regression for robust planning under uncertainty
- **Erlang C Extension:** Queueing theory for checkout staffing with service level targets
- **Intraday Patterns:** Hourly demand curves for shift scheduling

## References

### Data
- [Kaggle: Favorita Grocery Sales Forecasting](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)
- [Kaggle: Walmart Recruiting - Store Sales Forecasting](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)

### BLS Labor Productivity
- [BLS: Labor Productivity Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)
- [BLS: Productivity Program](https://www.bls.gov/bls/productivity.htm)
- [FRED: Labor Productivity - Food & Beverage Stores](https://fred.stlouisfed.org/series/IPUHN445L001000000)

### SPLH/IPLH
- [Sales Per Labor Hour - Restaurant Glossary](https://blackboxintelligence.com/resources/restaurant-glossary/sales-per-labor-hour/)
- [Items Per Labor Hour - Logile Blog](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)

## License

This project is for educational and research purposes.

## Contact

For questions or issues, please refer to the detailed report in `output/README_report.md`.

---

**Generated with reproducible data science best practices.**
