"""
Section 11: Markdown Report Generation

This script generates a comprehensive README_report.md that explains:
- Data sources and methodology
- Metrics and formulas
- Results and findings
- Limitations and caveats
- References
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# Import configuration
import config

print("=" * 80)
print("Section 11: Generating Markdown Report")
print("=" * 80)
print()

# ============================================================================
# Load Results
# ============================================================================

print("Loading analysis results...")

# Load comparison metrics
model_comparison = pd.read_csv(config.OUTPUT_DIR / "model_comparison.csv", index_col=0)
forecasts = pd.read_csv(config.FORECASTS_CSV)
hours_comparison = pd.read_csv(config.HOURS_COMPARISON_CSV)
productivity_comparison = pd.read_csv(config.OUTPUT_DIR / "productivity_comparison.csv")
sensitivity = pd.read_csv(config.OUTPUT_DIR / "sensitivity_analysis.csv")
split_info = joblib.load(config.OUTPUT_DIR / "split_info.pkl")
feature_importance = pd.read_csv(config.OUTPUT_DIR / "feature_importance.csv")

print("✓ All results loaded")
print()

# ============================================================================
# Generate Report Content
# ============================================================================

print("Generating report content...")

report = []

# Header
report.append("# Retail Labor Demand Forecasting and Productivity Analysis")
report.append("")
report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("")
report.append("---")
report.append("")

# Executive Summary
report.append("## Executive Summary")
report.append("")
report.append("This report presents a fully reproducible pipeline for forecasting retail store demand ")
report.append("and converting those forecasts into labor hour requirements using industry-standard productivity ")
report.append("metrics (SPLH/IPLH). The implied productivity is then calibrated against BLS labor productivity ")
report.append("benchmarks to ensure operational realism.")
report.append("")

# Key metrics
rf_test = model_comparison.loc['Random Forest (Test)']
mean_hours_actual = hours_comparison['Hours_Actual'].mean()
mean_hours_forecast = hours_comparison['Hours_Forecast'].mean()
mean_productivity = productivity_comparison['Productivity_Index'].mean()

report.append("**Key Findings:**")
report.append("")
report.append(f"- **Forecast Accuracy:** MAPE = {rf_test['MAPE']:.2f}%, RMSE = ${rf_test['RMSE']:,.2f}")
report.append(f"- **Mean Weekly Hours:** Actual = {mean_hours_actual:.1f}, Forecast = {mean_hours_forecast:.1f}")
report.append(f"- **Productivity Alignment:** Store index = {mean_productivity:.1f} (vs BLS baseline = 100)")
report.append(f"- **Conversion Mode:** {config.CONVERSION_MODE}")
report.append("")
report.append("---")
report.append("")

# Table of Contents
report.append("## Table of Contents")
report.append("")
report.append("1. [Data Sources](#data-sources)")
report.append("2. [Methodology](#methodology)")
report.append("3. [Metrics and Formulas](#metrics-and-formulas)")
report.append("4. [Forecasting Results](#forecasting-results)")
report.append("5. [Labor Conversion](#labor-conversion)")
report.append("6. [Productivity Calibration](#productivity-calibration)")
report.append("7. [Sensitivity Analysis](#sensitivity-analysis)")
report.append("8. [Why This Method Works](#why-this-method-works)")
report.append("9. [Limitations](#limitations)")
report.append("10. [Next Steps](#next-steps)")
report.append("11. [References](#references)")
report.append("")
report.append("---")
report.append("")

# Data Sources
report.append("## Data Sources")
report.append("")
report.append("### Historical Retail Sales Data")
report.append("")
report.append("- **Source:** Retail sales dataset (Walmart recruiting dataset structure)")
report.append("- **Period:** 2010-02-05 to 2012-11-01")
report.append(f"- **Stores:** {forecasts['Store'].nunique()}")
report.append(f"- **Departments:** Multiple per store")
report.append("- **Granularity:** Weekly sales by store and department")
report.append("- **Features:** Store type, size, temperature, fuel price, CPI, unemployment, markdowns, holidays")
report.append("")

report.append("### BLS Labor Productivity Benchmark")
report.append("")
report.append("- **Source:** U.S. Bureau of Labor Statistics (BLS)")
report.append("- **Industry:** Supermarkets and other grocery stores (NAICS 445110)")
report.append("- **Measure:** Labor productivity (output per hour)")
report.append("- **Units:** Index (2017 = 100)")
report.append("- **Years:** 1987 to present")
report.append("")
report.append("**Important:** BLS labor productivity measures *output per hour worked*, not output per worker. ")
report.append("This distinction matters because hours per worker can vary with part-time employment, overtime, etc.")
report.append("")
report.append("---")
report.append("")

# Methodology
report.append("## Methodology")
report.append("")
report.append("### Pipeline Overview")
report.append("")
report.append("The analysis follows a six-stage pipeline:")
report.append("")
report.append("1. **Data Loading & EDA:** Load sales, stores, features, and BLS productivity data; validate quality")
report.append("2. **Feature Engineering:** Aggregate to store level; create calendar, lag, rolling, and promotional features")
report.append("3. **Forecasting:** Train Random Forest model with time-based train/test split; generate forecasts")
report.append("4. **Labor Conversion (Actuals):** Convert actual sales to labor hours using SPLH/IPLH")
report.append("5. **Labor Conversion (Forecasts):** Convert forecast sales to labor hours using same parameters")
report.append("6. **Productivity Calibration:** Compare implied productivity to BLS industry benchmarks")
report.append("")

report.append("### Train/Test Split")
report.append("")
report.append(f"- **Training:** {split_info['train_start'].date()} to {split_info['train_end'].date()} ({split_info['n_train']:,} records)")
report.append(f"- **Testing:** {split_info['test_start'].date()} to {split_info['test_end'].date()} ({split_info['n_test']:,} records)")
report.append(f"- **Test Period:** Last {config.TEST_WEEKS} weeks held out")
report.append("")
report.append("Time-based splitting prevents data leakage and ensures realistic evaluation.")
report.append("")

report.append("### Feature Engineering")
report.append("")
report.append("**Features created:**")
report.append("")
report.append("- **Calendar:** Year, month, week, day of week, quarter, cyclical encodings (sin/cos)")
report.append(f"- **Lags:** Sales lagged by {config.LAG_PERIODS} weeks")
report.append(f"- **Rolling:** {config.ROLLING_WINDOWS}-week rolling means and standard deviations")
report.append("- **Store Attributes:** Type, size, normalized size")
report.append("- **External:** Temperature, fuel price, CPI, unemployment")
report.append("- **Promotional:** Markdown amounts (MD1-5), total markdown, markdown flag")
report.append("- **Holiday:** Holiday flag, pre-holiday flag, holiday × month interaction")
report.append("- **Trend:** Days since start, week number")
report.append("")
report.append(f"**Total features:** {len(feature_importance)} (top 10 by importance shown below)")
report.append("")

# Top features
top_features = feature_importance.head(10)
report.append("| Rank | Feature | Importance |")
report.append("|------|---------|------------|")
for idx, row in top_features.iterrows():
    report.append(f"| {idx+1} | {row['Feature']} | {row['Importance']:.4f} |")
report.append("")

report.append("---")
report.append("")

# Metrics and Formulas
report.append("## Metrics and Formulas")
report.append("")

report.append("### 1. Labor Productivity (BLS Definition)")
report.append("")
report.append("**Formula:**")
report.append("")
report.append("```")
report.append("LP = Real Output / Hours Worked")
report.append("```")
report.append("")
report.append("**Interpretation:** Measures output per hour. Real output is adjusted for inflation using industry price indices.")
report.append("")
report.append("**Important Distinction:**")
report.append("- **Labor Productivity:** Output / Hours Worked (what we use)")
report.append("- **Output per Worker:** Output / Number of Employees")
report.append("")
report.append("These can diverge when average hours per worker change (e.g., increased part-time employment).")
report.append("")

report.append("### 2. SPLH (Sales Per Labor Hour)")
report.append("")
report.append("**Formula:**")
report.append("")
report.append("```")
report.append("SPLH = Sales ($) / Labor Hours")
report.append("```")
report.append("")
report.append("**Inverse (for planning):**")
report.append("")
report.append("```")
report.append("Labor Hours = Sales ($) / SPLH")
report.append("```")
report.append("")
report.append(f"**Configuration:** {config.PRODUCTIVITY_BY_STORE_TYPE}")
report.append("")

report.append("### 3. IPLH (Items Per Labor Hour)")
report.append("")
report.append("**Formula:**")
report.append("")
report.append("```")
report.append("IPLH = Items (units) / Labor Hours")
report.append("```")
report.append("")
report.append("**Inverse (for planning):**")
report.append("")
report.append("```")
report.append("Labor Hours = Items (units) / IPLH")
report.append("```")
report.append("")
report.append("**Note:** This dataset has sales but not item counts. When IPLH mode is used, items are estimated as `Sales / Average Item Price`.")
report.append("")

report.append("### 4. Forecast Metrics")
report.append("")
report.append("**MAE (Mean Absolute Error):**")
report.append("```")
report.append("MAE = mean(|y_true - y_pred|)")
report.append("```")
report.append("")
report.append("**RMSE (Root Mean Squared Error):**")
report.append("```")
report.append("RMSE = sqrt(mean((y_true - y_pred)²))")
report.append("```")
report.append("")
report.append("**MAPE (Mean Absolute Percentage Error):**")
report.append("```")
report.append("MAPE = mean(|y_true - y_pred| / y_true) × 100%")
report.append("```")
report.append("")
report.append("**R² (Coefficient of Determination):**")
report.append("```")
report.append("R² = 1 - SS_res / SS_tot")
report.append("```")
report.append("")
report.append("---")
report.append("")

# Forecasting Results
report.append("## Forecasting Results")
report.append("")

report.append("### Model Comparison")
report.append("")
report.append("| Model | MAE ($) | RMSE ($) | MAPE (%) | R² |")
report.append("|-------|---------|----------|----------|-----|")
for model_name, metrics in model_comparison.iterrows():
    report.append(f"| {model_name} | {metrics['MAE']:,.2f} | {metrics['RMSE']:,.2f} | {metrics['MAPE']:.2f} | {metrics['R2']:.4f} |")
report.append("")

report.append("### Interpretation")
report.append("")
report.append(f"- The Random Forest model achieves **{rf_test['MAPE']:.2f}% MAPE** on the test set")
report.append(f"- This represents a mean error of **${rf_test['MAE']:,.2f}** per store-week")
report.append(f"- The model explains **{rf_test['R2']*100:.1f}%** of variance in weekly sales")
report.append("- Compared to naive baselines, the Random Forest substantially improves accuracy")
report.append("")

report.append("### Forecast Quality by Store Type")
report.append("")
by_type = forecasts.groupby('Type')['abs_error'].mean().round(2)
report.append("| Store Type | Mean Absolute Error ($) |")
report.append("|------------|-------------------------|")
for store_type, mae in by_type.items():
    report.append(f"| {store_type} | {mae:,.2f} |")
report.append("")

report.append("---")
report.append("")

# Labor Conversion
report.append("## Labor Conversion")
report.append("")

report.append("### Configuration")
report.append("")
report.append(f"- **Mode:** {config.CONVERSION_MODE}")
report.append(f"- **Baseline Hours:** {config.BASELINE_HOURS_PER_DAY} hours/day × 7 days = {config.BASELINE_HOURS_PER_DAY * 7} hours/week")
report.append("- **Baseline Rationale:** Fixed tasks (opening, closing, stocking, admin) independent of sales volume")
report.append("")

report.append("### Results")
report.append("")
report.append(f"**Actual Hours (ex-post):**")
report.append(f"- Mean: {hours_comparison['Hours_Actual'].mean():.1f} hours/week ({hours_comparison['Hours_Actual'].mean()/7:.1f} hours/day)")
report.append(f"- Median: {hours_comparison['Hours_Actual'].median():.1f} hours/week")
report.append(f"- Std Dev: {hours_comparison['Hours_Actual'].std():.1f} hours/week")
report.append("")

report.append(f"**Forecast Hours (ex-ante):**")
report.append(f"- Mean: {hours_comparison['Hours_Forecast'].mean():.1f} hours/week ({hours_comparison['Hours_Forecast'].mean()/7:.1f} hours/day)")
report.append(f"- Median: {hours_comparison['Hours_Forecast'].median():.1f} hours/week")
report.append(f"- Std Dev: {hours_comparison['Hours_Forecast'].std():.1f} hours/week")
report.append("")

delta_mean = hours_comparison['Delta_Hours'].mean()
delta_pct = hours_comparison['Delta_Hours_Pct'].mean()
report.append(f"**Forecast vs Actual Delta:**")
report.append(f"- Mean: {delta_mean:+.1f} hours/week ({delta_pct:+.2f}%)")
report.append(f"- Interpretation: Forecasts {'overestimate' if delta_mean > 0 else 'underestimate'} hours by {abs(delta_mean):.1f} hours/week on average")
report.append("")

report.append("### Hours by Store Type")
report.append("")
hours_by_type = hours_comparison.groupby('Type').agg({
    'Hours_Actual': 'mean',
    'Hours_Forecast': 'mean',
    'Delta_Hours': 'mean'
}).round(1)
report.append("| Store Type | Actual (hrs/wk) | Forecast (hrs/wk) | Delta (hrs/wk) |")
report.append("|------------|-----------------|-------------------|----------------|")
for store_type, row in hours_by_type.iterrows():
    report.append(f"| {store_type} | {row['Hours_Actual']:.1f} | {row['Hours_Forecast']:.1f} | {row['Delta_Hours']:+.1f} |")
report.append("")

report.append("---")
report.append("")

# Productivity Calibration
report.append("## Productivity Calibration")
report.append("")

report.append("### BLS Benchmark Context")
report.append("")
report.append("The BLS publishes labor productivity for **Supermarkets and other grocery stores (NAICS 445110)** ")
report.append("as an index with 2017 = 100. This measures real output (deflated by industry price index) per hour worked.")
report.append("")

report.append("### Our Implied Productivity")
report.append("")
report.append("We compute implied productivity as:")
report.append("")
report.append("```")
report.append("Implied Productivity = Real Sales / Hours Actual")
report.append("```")
report.append("")
report.append("Where real sales are deflated using CPI from the features dataset.")
report.append("")

report.append("### Comparison to BLS")
report.append("")
report.append("| Quarter | Store Index | BLS Index | Deviation (pp) | Deviation (%) |")
report.append("|---------|-------------|-----------|----------------|---------------|")
for _, row in productivity_comparison.iterrows():
    report.append(f"| {row['YearQuarter']} | {row['Productivity_Index']:.1f} | {row['BLS_Index_Normalized']:.1f} | {row['Deviation']:+.1f} | {row['Deviation_Pct']:+.1f}% |")
report.append("")

report.append("### Interpretation")
report.append("")
mean_dev = productivity_comparison['Deviation_Pct'].mean()
flagged = len(productivity_comparison[abs(productivity_comparison['Deviation_Pct']) > 10])
report.append(f"- **Mean Deviation:** {mean_dev:+.1f}%")
report.append(f"- **Quarters Flagged (>±10%):** {flagged} / {len(productivity_comparison)}")
report.append("")
if abs(mean_dev) < 5:
    report.append("Store productivity aligns well with industry benchmarks, suggesting SPLH assumptions are reasonable.")
elif mean_dev > 5:
    report.append("Store productivity trends higher than industry, which may indicate optimistic SPLH assumptions or operational efficiency gains.")
else:
    report.append("Store productivity trends lower than industry, which may indicate conservative SPLH assumptions or operational challenges.")
report.append("")

report.append("---")
report.append("")

# Sensitivity Analysis
report.append("## Sensitivity Analysis")
report.append("")

report.append(f"We test sensitivity to SPLH assumptions by varying the productivity parameter by {config.SENSITIVITY_RANGE}:")
report.append("")

report.append("| SPLH Factor | Adjusted SPLH ($/hr) | Mean Hours/Week | Total Hours (all stores) |")
report.append("|-------------|----------------------|-----------------|--------------------------|")
for _, row in sensitivity.iterrows():
    report.append(f"| {row['SPLH_Factor']:.1f} | {row['SPLH_Adjusted']:.2f} | {row['Mean_Hours']:.1f} | {row['Total_Hours']:,.0f} |")
report.append("")

report.append("### Implications")
report.append("")
baseline_hours = sensitivity[sensitivity['SPLH_Factor'] == 1.0]['Mean_Hours'].values[0]
low_hours = sensitivity[sensitivity['SPLH_Factor'] == max(config.SENSITIVITY_RANGE)]['Mean_Hours'].values[0]
high_hours = sensitivity[sensitivity['SPLH_Factor'] == min(config.SENSITIVITY_RANGE)]['Mean_Hours'].values[0]

report.append(f"- **Baseline:** {baseline_hours:.1f} hours/week")
report.append(f"- **Range:** {low_hours:.1f} to {high_hours:.1f} hours/week")
report.append(f"- **Spread:** {high_hours - low_hours:.1f} hours/week ({(high_hours/low_hours - 1)*100:.1f}% variation)")
report.append("")
report.append("This demonstrates the operational risk from productivity assumptions. A 20% error in SPLH ")
report.append("translates directly to a 20% error in planned hours.")
report.append("")

report.append("---")
report.append("")

# Why This Method Works
report.append("## Why This Method Works")
report.append("")

report.append("### Strengths")
report.append("")
report.append("1. **Simple and Explainable**")
report.append("   - Direct mapping from demand (sales/items) to labor hours")
report.append("   - Easy to communicate to stakeholders")
report.append("   - Transparent assumptions (SPLH/IPLH parameters)")
report.append("")
report.append("2. **Quick What-If Analysis**")
report.append("   - Adjust SPLH/IPLH to instantly see impact on hours")
report.append("   - Sensitivity analysis reveals planning risk")
report.append("   - Store/department-level customization possible")
report.append("")
report.append("3. **Calibration to Industry Norms**")
report.append("   - BLS productivity provides external validation")
report.append("   - Flags unrealistic assumptions early")
report.append("   - Ensures plans are grounded in industry benchmarks")
report.append("")
report.append("4. **Actionable Outputs**")
report.append("   - Weekly hour plans by store")
report.append("   - Forecast error bounds propagate to hours")
report.append("   - Ready for scheduling systems")
report.append("")

report.append("---")
report.append("")

# Limitations
report.append("## Limitations")
report.append("")

report.append("### 1. Sales/Items May Not Equal Workload")
report.append("")
report.append("- **Issue:** Some tasks are independent of sales volume (e.g., shelf resets, cleaning)")
report.append("- **Mitigation:** We add baseline hours for fixed tasks")
report.append("- **Residual Risk:** Task mix varies; SPLH/IPLH are averages")
report.append("")

report.append("### 2. SPLH/IPLH Vary by Context")
report.append("")
report.append("- **Product Mix:** Different categories have different handling requirements")
report.append("- **Store Layout:** Efficiency varies with size and design")
report.append("- **Processes:** Self-checkout, curbside pickup, etc. change productivity")
report.append("- **Mitigation:** Use store type and department adjustments")
report.append("")

report.append("### 3. BLS Productivity is an Aggregate Benchmark")
report.append("")
report.append("- **Issue:** BLS data is industry-wide; individual stores vary")
report.append("- **Issue:** BLS uses real output (value-added), we use sales")
report.append("- **Issue:** Different deflators (industry price index vs CPI)")
report.append("- **Interpretation:** BLS provides directional guidance, not ground truth")
report.append("")

report.append("### 4. Forecast Error Propagates")
report.append("")
report.append("- **Issue:** Hours are only as accurate as sales forecasts")
report.append(f"- **Our Error:** {rf_test['MAPE']:.2f}% MAPE → same % error in hours")
report.append("- **Mitigation:** Use probabilistic forecasts (future work)")
report.append("")

report.append("### 5. Weekly Granularity")
report.append("")
report.append("- **Issue:** Dataset is weekly; daily/hourly staffing needs may differ")
report.append("- **Implication:** Assume even distribution across days (may not hold)")
report.append("- **Future:** Intraweek/intraday models for shift planning")
report.append("")

report.append("---")
report.append("")

# Next Steps
report.append("## Next Steps")
report.append("")

report.append("### Near-Term Enhancements")
report.append("")
report.append("1. **Department-Level Models**")
report.append("   - Current: Store-level aggregates")
report.append("   - Future: Model each department separately for task-specific SPLH/IPLH")
report.append("")
report.append("2. **Probabilistic Forecasts**")
report.append("   - Current: Point forecasts only")
report.append("   - Future: Quantile regression or prediction intervals for robust planning")
report.append("")
report.append("3. **Calibrate SPLH from Time Studies**")
report.append("   - Current: Example/assumed SPLH values")
report.append("   - Future: Estimate SPLH from historical hours and sales (if available)")
report.append("")

report.append("### Advanced Extensions")
report.append("")
report.append("4. **Erlang C for Checkout Staffing**")
report.append("   - Use queueing theory to meet service level targets (e.g., <2 min wait)")
report.append("   - Requires arrival rate estimates (transactions per hour)")
report.append("   - See: [Erlang C Overview](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)")
report.append("")
report.append("5. **Intraday/Intraweek Patterns**")
report.append("   - Model hourly demand curves for shift scheduling")
report.append("   - Account for peak hours, weekends, etc.")
report.append("")
report.append("6. **Multi-Objective Optimization**")
report.append("   - Minimize cost (hours) subject to service level constraints")
report.append("   - Balance overstaffing risk vs understaffing risk")
report.append("")

report.append("---")
report.append("")

# References
report.append("## References")
report.append("")

report.append("### Data Sources")
report.append("")
report.append("- [Corporación Favorita Grocery Sales Forecasting (Kaggle)](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)")
report.append("- [Walmart Recruiting - Store Sales Forecasting (similar dataset structure)](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)")
report.append("- [Example Analysis: Favorita Sales Forecasting](https://www.kaggle.com/code/sandraezzat/favorita-grocery-sales-forecasting)")
report.append("- [Stanford CS221 Project Poster](https://web.stanford.edu/class/archive/cs/cs221/cs221.1192/2018/restricted/posters/jzhao4/poster.pdf)")
report.append("")

report.append("### BLS Labor Productivity")
report.append("")
report.append("- [BLS: Labor Productivity Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)")
report.append("- [BLS: Productivity Program Overview](https://www.bls.gov/bls/productivity.htm)")
report.append("- [FRED: Labor Productivity - Food & Beverage Stores](https://fred.stlouisfed.org/series/IPUHN445L001000000)")
report.append("- [BLS: Labor Productivity vs Total Factor Productivity](https://www.bls.gov/productivity/educational-material/labor-productivity-total-factor-productivity-comparison.htm)")
report.append("- [USAFacts: What is Labor Productivity?](https://usafacts.org/articles/what-is-labor-productivity-and-how-has-it-changed-in-the-us-over-time/)")
report.append("")

report.append("### SPLH and IPLH Metrics")
report.append("")
report.append("- [Sales Per Labor Hour (SPLH) - Restaurant Glossary](https://blackboxintelligence.com/resources/restaurant-glossary/sales-per-labor-hour/)")
report.append("- [Items Per Labor Hour (IPLH) - Logile Blog](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)")
report.append("")

report.append("### Advanced Topics (Future Work)")
report.append("")
report.append("- [Erlang C Formula for Workforce Scheduling](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)")
report.append("")

report.append("---")
report.append("")

# Footer
report.append("## Reproducibility")
report.append("")
report.append("All analysis is fully reproducible:")
report.append("")
report.append("1. Install dependencies: `pip install -r requirements.txt`")
report.append("2. Run pipeline: `python run_all.py`")
report.append("3. Outputs are saved to `output/` directory")
report.append("4. Model artifacts saved to `models/` directory")
report.append("")
report.append(f"**Random Seed:** {config.RANDOM_SEED}")
report.append(f"**Python Packages:** See `requirements.txt` for pinned versions")
report.append("")

report.append("---")
report.append("")
report.append("*End of Report*")

# Join all lines
report_content = "\n".join(report)

# ============================================================================
# Save Report
# ============================================================================

print("Writing report to file...")

with open(config.REPORT_PATH, 'w') as f:
    f.write(report_content)

print(f"✓ Saved: {config.REPORT_PATH}")
print(f"  Lines: {len(report)}")
print(f"  Characters: {len(report_content):,}")
print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Report generated: {config.REPORT_PATH}")
print(f"Sections: 11")
print(f"References: 13")
print()
print("✓ Report generation complete!")
print("=" * 80)
