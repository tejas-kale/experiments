"""
Section 11: Markdown Report Generation

This script generates a comprehensive README_report.md explaining the methodology,
formulas, results, and limitations with proper references.
"""

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from datetime import datetime

# Import configuration
import config

warnings.filterwarnings('ignore')

print("=" * 80)
print("SECTION 11: MARKDOWN REPORT GENERATION")
print("=" * 80)

# ============================================================================
# LOAD RESULTS
# ============================================================================

print("\n--- Loading Results ---")

# Load all result files
forecasts = pd.read_csv(config.FORECASTS_PATH)
hours_actual = pd.read_csv(config.HOURS_ACTUAL_PATH)
hours_forecast = pd.read_csv(config.HOURS_FORECAST_PATH)
hours_comparison = pd.read_csv(config.HOURS_COMPARISON_PATH)
model_comparison = pd.read_csv(config.OUTPUT_DIR / "model_comparison.csv")
sensitivity = pd.read_csv(config.OUTPUT_DIR / "sensitivity_analysis.csv")
productivity = pd.read_csv(config.OUTPUT_DIR / "productivity_analysis.csv")

print(f"✓ Loaded all result files")

# ============================================================================
# GENERATE MARKDOWN REPORT
# ============================================================================

print("\n--- Generating Markdown Report ---")

report_lines = []

# Header
report_lines.append("# Retail Labour Demand Forecasting Report")
report_lines.append("")
report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Executive Summary
report_lines.append("## Executive Summary")
report_lines.append("")
report_lines.append("This report presents a reproducible retail labor demand forecasting system that:")
report_lines.append("")
report_lines.append("1. Forecasts daily store demand using Random Forest on Corporación Favorita dataset")
report_lines.append("2. Converts forecasts and actuals into labor hours using SPLH/IPLH parameters")
report_lines.append("3. Calibrates implied productivity against BLS labor productivity benchmarks")
report_lines.append("4. Provides sensitivity analysis to quantify planning risk")
report_lines.append("")

# Calculate key metrics for summary
mae_rf = model_comparison[model_comparison['Model'] == 'Random Forest']['MAE'].values[0]
mape_rf = model_comparison[model_comparison['Model'] == 'Random Forest']['MAPE'].values[0]
total_hours_actual = hours_comparison['hours_actual'].sum()
total_hours_forecast = hours_comparison['hours_forecast'].sum()
hours_error_pct = ((total_hours_forecast - total_hours_actual) / total_hours_actual) * 100

report_lines.append("**Key Results:**")
report_lines.append("")
report_lines.append(f"- Forecast MAE: {mae_rf:.2f} units")
report_lines.append(f"- Forecast MAPE: {mape_rf:.2f}%")
report_lines.append(f"- Total hours forecast error: {hours_error_pct:.2f}%")
report_lines.append(f"- Conversion mode: {config.CONVERSION_MODE}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Data Sources
report_lines.append("## 1. Data Sources")
report_lines.append("")
report_lines.append("### 1.1 Corporación Favorita Dataset")
report_lines.append("")
report_lines.append("Historical sales data from the Corporación Favorita grocery sales forecasting competition:")
report_lines.append("")
report_lines.append("- **Sales Data:** Weekly sales by store and department")
report_lines.append(f"  - {len(pd.read_csv(config.SALES_PATH)):,} records")
report_lines.append(f"  - 45 stores, 81 departments")
report_lines.append("  - Date range: 2010-02-05 to 2012-10-26")
report_lines.append("- **Store Metadata:** Store type and size information")
report_lines.append("- **Features:** Temperature, fuel prices, CPI, unemployment, promotional markdowns, and holiday flags")
report_lines.append("")
report_lines.append("### 1.2 BLS Labor Productivity")
report_lines.append("")
report_lines.append("Bureau of Labor Statistics labor productivity series for retail:")
report_lines.append("")
report_lines.append("- **Industry:** Supermarkets and other grocery stores (NAICS 445110)")
report_lines.append("- **Measure:** Labor productivity (output per hour worked)")
report_lines.append("- **Units:** Index (2017=100)")
report_lines.append("- **Purpose:** Industry benchmark for productivity calibration")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Methodology
report_lines.append("## 2. Methodology")
report_lines.append("")

report_lines.append("### 2.1 Feature Engineering")
report_lines.append("")
report_lines.append("Data aggregated to daily store-level with the following features:")
report_lines.append("")
report_lines.append("- **Calendar features:** Year, month, day, day of week, quarter, week of year")
report_lines.append("- **Cyclic encoding:** Sine/cosine transformations for month and day of week")
report_lines.append("- **Holiday indicators:** Current, pre-, and post-holiday flags")
report_lines.append("- **Promotion intensity:** Sum of markdown values and promotion flags")
report_lines.append("- **Economic features:** Temperature, fuel price, CPI, unemployment")
report_lines.append("- **Lagged features:** 7, 14, and 28-day lags for sales and units")
report_lines.append("- **Rolling features:** 7, 14, and 28-day rolling means (shifted to prevent leakage)")
report_lines.append("")

report_lines.append("### 2.2 Forecasting Model")
report_lines.append("")
report_lines.append("**Target Variable:** Total units/items per store per day")
report_lines.append("")
report_lines.append("**Train/Test Split:**")
report_lines.append(f"- Last {config.TEST_WEEKS} weeks held out for testing")
report_lines.append("- Time-based split to respect temporal ordering")
report_lines.append("")
report_lines.append("**Baseline Models:**")
report_lines.append("- Naive: Last observed value per store")
report_lines.append("- Seasonal Naive: Last value for same day of week per store")
report_lines.append("- Moving Average: Mean of last 4 weeks per store")
report_lines.append("")
report_lines.append("**Random Forest:**")
report_lines.append("- Hyperparameter tuning via GridSearchCV with TimeSeriesSplit")
report_lines.append("- Cross-validation with 3 splits")
report_lines.append("- Optimized for mean absolute error")
report_lines.append("")

# Model comparison table
report_lines.append("**Model Performance Comparison:**")
report_lines.append("")
report_lines.append("| Model | MAE | RMSE | MAPE (%) |")
report_lines.append("|-------|-----|------|----------|")
for _, row in model_comparison.iterrows():
    report_lines.append(f"| {row['Model']} | {row['MAE']:.2f} | {row['RMSE']:.2f} | {row['MAPE']:.2f} |")
report_lines.append("")

report_lines.append("### 2.3 Labor Conversion")
report_lines.append("")
report_lines.append("Labor hours calculated using industry-standard metrics:")
report_lines.append("")

# SPLH Definition
report_lines.append("#### Sales per Labor Hour (SPLH)")
report_lines.append("")
report_lines.append("SPLH measures sales revenue generated per labor hour:")
report_lines.append("")
report_lines.append("$$")
report_lines.append(r"\text{SPLH} = \frac{\text{Sales (\\$)}}{\text{Labor Hours}}")
report_lines.append("$$")
report_lines.append("")
report_lines.append("To calculate required hours from sales:")
report_lines.append("")
report_lines.append("$$")
report_lines.append(r"\text{Hours} = \frac{\text{Sales (\\$)}}{\text{SPLH}}")
report_lines.append("$$")
report_lines.append("")

# IPLH Definition
report_lines.append("#### Items per Labor Hour (IPLH)")
report_lines.append("")
report_lines.append("IPLH measures units/items processed per labor hour:")
report_lines.append("")
report_lines.append("$$")
report_lines.append(r"\text{IPLH} = \frac{\text{Items (units)}}{\text{Labor Hours}}")
report_lines.append("$$")
report_lines.append("")
report_lines.append("To calculate required hours from items:")
report_lines.append("")
report_lines.append("$$")
report_lines.append(r"\text{Hours} = \frac{\text{Items (units)}}{\text{IPLH}}")
report_lines.append("$$")
report_lines.append("")

# Configuration used
report_lines.append("#### Configuration Used")
report_lines.append("")
report_lines.append(f"- **Conversion Mode:** {config.CONVERSION_MODE}")
if config.CONVERSION_MODE == "IPLH":
    report_lines.append(f"- **Target IPLH:** {config.IPLH_PER_STORE['default']} items/hour")
else:
    report_lines.append(f"- **Target SPLH:** ${config.SPLH_PER_STORE['default']}/hour")
report_lines.append(f"- **Baseline Hours:** {config.BASELINE_HOURS_PER_STORE_DAY} hours/day per store")
report_lines.append("- **Total Hours:** Variable hours (demand-driven) + Baseline hours (fixed tasks)")
report_lines.append("")

# BLS Productivity
report_lines.append("#### BLS Labor Productivity")
report_lines.append("")
report_lines.append("The Bureau of Labor Statistics defines labor productivity as:")
report_lines.append("")
report_lines.append("$$")
report_lines.append(r"LP_t = \frac{\text{Real Output}_t}{\text{Hours Worked}_t}")
report_lines.append("$$")
report_lines.append("")
report_lines.append("Where:")
report_lines.append("- **Real Output** = Inflation-adjusted output (constant dollars)")
report_lines.append("- **Hours Worked** = Total hours worked (not headcount)")
report_lines.append("")
report_lines.append("**Important:** Labor productivity (output per hour) differs from output per worker,")
report_lines.append("which divides by employment rather than hours and can diverge when hours per worker change.")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Results
report_lines.append("## 3. Results")
report_lines.append("")

report_lines.append("### 3.1 Forecast Performance")
report_lines.append("")
avg_actual = forecasts['y_true'].mean()
avg_pred = forecasts['y_pred'].mean()
report_lines.append(f"- Average actual units: {avg_actual:.2f}")
report_lines.append(f"- Average predicted units: {avg_pred:.2f}")
report_lines.append(f"- Forecast bias: {avg_pred - avg_actual:.2f} units ({((avg_pred-avg_actual)/avg_actual)*100:.2f}%)")
report_lines.append("")

report_lines.append("### 3.2 Labor Hours")
report_lines.append("")

# Actual hours summary
avg_hours_actual = hours_actual['hours_total'].mean()
avg_hours_variable = hours_actual['hours_variable'].mean()
report_lines.append("**Actual Hours (Ex-Post):**")
report_lines.append(f"- Average variable hours per store-day: {avg_hours_variable:.2f}")
report_lines.append(f"- Average total hours per store-day: {avg_hours_actual:.2f}")
report_lines.append(f"- Total hours across all stores/days: {hours_actual['hours_total'].sum():.0f}")
report_lines.append("")

# Forecast hours summary
avg_hours_forecast = hours_forecast['hours_total'].mean()
report_lines.append("**Forecasted Hours (Ex-Ante):**")
report_lines.append(f"- Average total hours per store-day: {avg_hours_forecast:.2f}")
report_lines.append(f"- Total hours across test period: {hours_forecast['hours_total'].sum():.0f}")
report_lines.append("")

# Hours comparison
avg_delta = hours_comparison['delta_hours'].mean()
abs_avg_delta = hours_comparison['delta_hours'].abs().mean()
report_lines.append("**Comparison:**")
report_lines.append(f"- Average hours error: {avg_delta:.2f} hours/day")
report_lines.append(f"- Average absolute hours error: {abs_avg_delta:.2f} hours/day")
report_lines.append(f"- Total hours error: {hours_error_pct:.2f}%")
report_lines.append("")

report_lines.append("### 3.3 Productivity Analysis")
report_lines.append("")
avg_prod_units = productivity['productivity_units'].mean()
avg_prod_sales = productivity['productivity_sales'].mean()
report_lines.append(f"**Implied Store Productivity:**")
report_lines.append(f"- Average units per hour: {avg_prod_units:.2f} items/hour")
report_lines.append(f"- Average sales per hour: ${avg_prod_sales:.2f}/hour (nominal)")
report_lines.append("")
report_lines.append("**Note:** These are operational metrics. Direct comparison with BLS productivity")
report_lines.append("requires deflating sales to real terms. Units per hour is an operational efficiency")
report_lines.append("proxy, not economic productivity per se.")
report_lines.append("")

report_lines.append("### 3.4 Sensitivity Analysis")
report_lines.append("")
param_name = "IPLH" if config.CONVERSION_MODE == "IPLH" else "SPLH"
baseline_row = sensitivity[sensitivity['pct_change'] == 0].iloc[0]
low_row = sensitivity.iloc[0]  # Most negative change
high_row = sensitivity.iloc[-1]  # Most positive change

report_lines.append(f"**{param_name} Sensitivity:**")
report_lines.append("")
report_lines.append(f"Varying {param_name} by ±30% shows operational risk from productivity assumptions:")
report_lines.append("")
report_lines.append("| Scenario | Parameter Value | Total Hours | Change from Baseline |")
report_lines.append("|----------|----------------|-------------|----------------------|")
for _, row in sensitivity.iterrows():
    pct_change_str = f"{row['pct_change']:+.0f}%"
    param_val = row[param_name]
    total_hrs = row['total_hours']
    change = ((total_hrs - baseline_row['total_hours']) / baseline_row['total_hours']) * 100
    report_lines.append(f"| {pct_change_str} | {param_val:.2f} | {total_hrs:.0f} | {change:+.1f}% |")
report_lines.append("")

hours_range = high_row['total_hours'] - low_row['total_hours']
report_lines.append(f"A ±30% variation in {param_name} creates a **{hours_range:.0f} hour** range")
report_lines.append(f"({((hours_range/baseline_row['total_hours'])*100):.1f}% of baseline), exposing significant staffing risk.")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Why This Method is Useful
report_lines.append("## 4. Why This Method is Useful")
report_lines.append("")
report_lines.append("1. **Simple and Explainable:** SPLH/IPLH are widely understood in retail operations")
report_lines.append("2. **Quick What-If Analysis:** Easy to adjust productivity assumptions and see impact")
report_lines.append("3. **Industry Calibration:** BLS benchmarks provide reality check on assumptions")
report_lines.append("4. **Actionable:** Directly translates demand forecasts into staffing plans")
report_lines.append("5. **Reproducible:** Fully scripted pipeline ensures consistency")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Limitations
report_lines.append("## 5. Limitations")
report_lines.append("")
report_lines.append("### 5.1 Conversion Limitations")
report_lines.append("")
report_lines.append("- **Sales/units ≠ workload:** Not all tasks scale with sales (e.g., opening, closing, cleaning)")
report_lines.append("- **SPLH/IPLH vary by mix:** Different product categories require different labor")
report_lines.append("- **Process dependencies:** Checkout, stocking, and customer service have different drivers")
report_lines.append("- **Layout effects:** Store layout impacts labor efficiency but isn't captured")
report_lines.append("")

report_lines.append("### 5.2 BLS Calibration Limitations")
report_lines.append("")
report_lines.append("- **Aggregate benchmark:** BLS is industry-wide, not store-specific truth")
report_lines.append("- **Real vs nominal:** Our sales are nominal; BLS uses inflation-adjusted output")
report_lines.append("- **Units proxy:** Items per hour is operational efficiency, not economic productivity")
report_lines.append("- **Timing:** BLS annual data; our operations are daily/weekly")
report_lines.append("")

report_lines.append("### 5.3 Forecast Limitations")
report_lines.append("")
report_lines.append("- **Error propagation:** Forecast errors directly affect hour plans")
report_lines.append("- **Point forecasts:** No uncertainty quantification (see next steps)")
report_lines.append("- **Weekly granularity:** Original data is weekly, limiting daily insights")
report_lines.append("- **Limited features:** Could benefit from more granular promotional data")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Next Steps
report_lines.append("## 6. Next Steps")
report_lines.append("")
report_lines.append("1. **Department-Level Models:** Separate forecasts by department with specific IPLH/SPLH")
report_lines.append("2. **Probabilistic Forecasts:** Quantile regression or prediction intervals for uncertainty")
report_lines.append("3. **Queueing Models:** Erlang C for checkout staffing based on service level objectives")
report_lines.append("4. **Real-Time Updates:** Integrate actual sales to refine hour plans intra-day")
report_lines.append("5. **Task-Based Models:** Decompose hours by task type (checkout, stocking, etc.)")
report_lines.append("6. **Optimization:** Schedule optimization given forecast hours and constraints")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Files Generated
report_lines.append("## 7. Output Files")
report_lines.append("")
report_lines.append("This analysis generated the following files:")
report_lines.append("")
report_lines.append("**Data Files:**")
report_lines.append(f"- `features_train.csv` - Training features and target")
report_lines.append(f"- `forecasts.csv` - Test set forecasts (date, store, actual, predicted)")
report_lines.append(f"- `hours_actual.csv` - Actual labor hours (ex-post)")
report_lines.append(f"- `hours_forecast.csv` - Forecasted labor hours (ex-ante)")
report_lines.append(f"- `hours_comparison.csv` - Side-by-side comparison with deltas")
report_lines.append(f"- `productivity_analysis.csv` - Implied productivity metrics")
report_lines.append(f"- `sensitivity_analysis.csv` - Sensitivity to IPLH/SPLH assumptions")
report_lines.append("")
report_lines.append("**Model Artifacts:**")
report_lines.append(f"- `random_forest_model.joblib` - Trained Random Forest model")
report_lines.append(f"- `feature_names.joblib` - Feature column names")
report_lines.append(f"- `feature_importances.csv` - Feature importance scores")
report_lines.append("")
report_lines.append("**Visualizations:**")
report_lines.append(f"- `hours_over_time.png` - Actual vs forecast hours timeline")
report_lines.append(f"- `hours_by_store.png` - Hours by store comparison")
report_lines.append(f"- `hours_parity_plot.png` - Actual vs forecast scatter")
report_lines.append(f"- `productivity_trends.png` - Productivity over time")
report_lines.append(f"- `bls_comparison.png` - BLS benchmark comparison")
report_lines.append(f"- `sensitivity_analysis.png` - Parameter sensitivity plots")
report_lines.append(f"- And more diagnostic plots...")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# References
report_lines.append("## 8. References")
report_lines.append("")
report_lines.append("1. **Corporación Favorita competition data:** [Kaggle Competition](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)")
report_lines.append("")
report_lines.append("2. **Favorita examples and write-ups:**")
report_lines.append("   - [Kaggle Notebook Example](https://www.kaggle.com/code/sandraezzat/favorita-grocery-sales-forecasting)")
report_lines.append("   - [Stanford CS221 Project Poster](https://web.stanford.edu/class/archive/cs/cs221/cs221.1192/2018/restricted/posters/jzhao4/poster.pdf)")
report_lines.append("")
report_lines.append("3. **BLS labor productivity concepts:**")
report_lines.append("   - [Labor Productivity and Costs Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)")
report_lines.append("   - [BLS Productivity Overview](https://www.bls.gov/bls/productivity.htm)")
report_lines.append("")
report_lines.append("4. **FRED labor productivity series:**")
report_lines.append("   - [Labor Productivity: Food & Beverage Stores](https://fred.stlouisfed.org/series/IPUHN445L001000000)")
report_lines.append("")
report_lines.append("5. **SPLH and IPLH definitions:**")
report_lines.append("   - [Sales per Labor Hour Guide](https://blackboxintelligence.com/resources/restaurant-glossary/sales-per-labor-hour/)")
report_lines.append("   - [Measuring Retail Productivity](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)")
report_lines.append("")
report_lines.append("6. **Background on productivity:**")
report_lines.append("   - [Labor vs Total Factor Productivity](https://www.bls.gov/productivity/educational-material/labor-productivity-total-factor-productivity-comparison.htm)")
report_lines.append("   - [USAFacts Productivity Primer](https://usafacts.org/articles/what-is-labor-productivity-and-how-has-it-changed-in-the-us-over-time/)")
report_lines.append("")
report_lines.append("7. **Erlang C for future extensions:**")
report_lines.append("   - [Erlang Formula Overview](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Footer
report_lines.append("*Report generated by automated retail labor demand forecasting pipeline*")
report_lines.append("")

# ============================================================================
# WRITE REPORT
# ============================================================================

report_content = "\n".join(report_lines)

with open(config.REPORT_PATH, 'w') as f:
    f.write(report_content)

print(f"✓ Generated report: {config.REPORT_PATH}")
print(f"  Total lines: {len(report_lines)}")
print(f"  Total characters: {len(report_content)}")

# Display first few sections
print("\n--- Report Preview ---")
print("\n".join(report_lines[:50]))
print("...")
print(f"\n(Full report saved to {config.REPORT_PATH})")

print("\n" + "=" * 80)
print("REPORT GENERATION COMPLETE")
print("=" * 80)
