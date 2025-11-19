# Retail Labor Demand Forecasting and Productivity Analysis

**Generated:** 2025-11-19 13:45:38

---

## Executive Summary

This report presents a fully reproducible pipeline for forecasting retail store demand 
and converting those forecasts into labor hour requirements using industry-standard productivity 
metrics (SPLH/IPLH). The implied productivity is then calibrated against BLS labor productivity 
benchmarks to ensure operational realism.

**Key Findings:**

- **Forecast Accuracy:** MAPE = 4.60%, RMSE = $60,731.06
- **Mean Weekly Hours:** Actual = 5398.6, Forecast = 5502.8
- **Productivity Alignment:** Store index = 99.9 (vs BLS baseline = 100)
- **Conversion Mode:** SPLH

---

## Table of Contents

1. [Data Sources](#data-sources)
2. [Methodology](#methodology)
3. [Metrics and Formulas](#metrics-and-formulas)
4. [Forecasting Results](#forecasting-results)
5. [Labor Conversion](#labor-conversion)
6. [Productivity Calibration](#productivity-calibration)
7. [Sensitivity Analysis](#sensitivity-analysis)
8. [Why This Method Works](#why-this-method-works)
9. [Limitations](#limitations)
10. [Next Steps](#next-steps)
11. [References](#references)

---

## Data Sources

### Historical Retail Sales Data

- **Source:** Retail sales dataset (Walmart recruiting dataset structure)
- **Period:** 2010-02-05 to 2012-11-01
- **Stores:** 45
- **Departments:** Multiple per store
- **Granularity:** Weekly sales by store and department
- **Features:** Store type, size, temperature, fuel price, CPI, unemployment, markdowns, holidays

### BLS Labor Productivity Benchmark

- **Source:** U.S. Bureau of Labor Statistics (BLS)
- **Industry:** Supermarkets and other grocery stores (NAICS 445110)
- **Measure:** Labor productivity (output per hour)
- **Units:** Index (2017 = 100)
- **Years:** 1987 to present

**Important:** BLS labor productivity measures *output per hour worked*, not output per worker. 
This distinction matters because hours per worker can vary with part-time employment, overtime, etc.

---

## Methodology

### Pipeline Overview

The analysis follows a six-stage pipeline:

1. **Data Loading & EDA:** Load sales, stores, features, and BLS productivity data; validate quality
2. **Feature Engineering:** Aggregate to store level; create calendar, lag, rolling, and promotional features
3. **Forecasting:** Train Random Forest model with time-based train/test split; generate forecasts
4. **Labor Conversion (Actuals):** Convert actual sales to labor hours using SPLH/IPLH
5. **Labor Conversion (Forecasts):** Convert forecast sales to labor hours using same parameters
6. **Productivity Calibration:** Compare implied productivity to BLS industry benchmarks

### Train/Test Split

- **Training:** 2010-02-05 to 2012-08-31 (6,075 records)
- **Testing:** 2012-09-07 to 2012-10-26 (360 records)
- **Test Period:** Last 8 weeks held out

Time-based splitting prevents data leakage and ensures realistic evaluation.

### Feature Engineering

**Features created:**

- **Calendar:** Year, month, week, day of week, quarter, cyclical encodings (sin/cos)
- **Lags:** Sales lagged by [7, 14, 28] weeks
- **Rolling:** [7, 28]-week rolling means and standard deviations
- **Store Attributes:** Type, size, normalized size
- **External:** Temperature, fuel price, CPI, unemployment
- **Promotional:** Markdown amounts (MD1-5), total markdown, markdown flag
- **Holiday:** Holiday flag, pre-holiday flag, holiday × month interaction
- **Trend:** Days since start, week number

**Total features:** 36 (top 10 by importance shown below)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | Sales_RollingMean_28 | 0.1832 |
| 2 | Sales_RollingMean_7 | 0.1820 |
| 3 | Sales_Lag_7 | 0.1415 |
| 4 | Sales_Lag_14 | 0.1093 |
| 5 | Size | 0.0872 |
| 6 | Size_Normalized | 0.0826 |
| 7 | Sales_Lag_28 | 0.0506 |
| 8 | Sales_RollingStd_7 | 0.0375 |
| 9 | Sales_RollingStd_28 | 0.0197 |
| 10 | Type | 0.0193 |

---

## Metrics and Formulas

### 1. Labor Productivity (BLS Definition)

**Formula:**

```
LP = Real Output / Hours Worked
```

**Interpretation:** Measures output per hour. Real output is adjusted for inflation using industry price indices.

**Important Distinction:**
- **Labor Productivity:** Output / Hours Worked (what we use)
- **Output per Worker:** Output / Number of Employees

These can diverge when average hours per worker change (e.g., increased part-time employment).

### 2. SPLH (Sales Per Labor Hour)

**Formula:**

```
SPLH = Sales ($) / Labor Hours
```

**Inverse (for planning):**

```
Labor Hours = Sales ($) / SPLH
```

**Configuration:** {'A': {'SPLH': 200.0, 'IPLH': 50.0}, 'B': {'SPLH': 180.0, 'IPLH': 45.0}, 'C': {'SPLH': 150.0, 'IPLH': 40.0}}

### 3. IPLH (Items Per Labor Hour)

**Formula:**

```
IPLH = Items (units) / Labor Hours
```

**Inverse (for planning):**

```
Labor Hours = Items (units) / IPLH
```

**Note:** This dataset has sales but not item counts. When IPLH mode is used, items are estimated as `Sales / Average Item Price`.

### 4. Forecast Metrics

**MAE (Mean Absolute Error):**
```
MAE = mean(|y_true - y_pred|)
```

**RMSE (Root Mean Squared Error):**
```
RMSE = sqrt(mean((y_true - y_pred)²))
```

**MAPE (Mean Absolute Percentage Error):**
```
MAPE = mean(|y_true - y_pred| / y_true) × 100%
```

**R² (Coefficient of Determination):**
```
R² = 1 - SS_res / SS_tot
```

---

## Forecasting Results

### Model Comparison

| Model | MAE ($) | RMSE ($) | MAPE (%) | R² |
|-------|---------|----------|----------|-----|
| Naive | 68,165.85 | 91,989.20 | 6.94 | 0.9686 |
| Seasonal Naive | 49,947.39 | 77,447.34 | 5.13 | 0.9777 |
| Moving Average | 64,496.13 | 87,442.08 | 6.42 | 0.9716 |
| Random Forest (Train) | 41,791.59 | 72,169.52 | 4.16 | 0.9838 |
| Random Forest (Test) | 44,026.84 | 60,731.06 | 4.60 | 0.9863 |

### Interpretation

- The Random Forest model achieves **4.60% MAPE** on the test set
- This represents a mean error of **$44,026.84** per store-week
- The model explains **98.6%** of variance in weekly sales
- Compared to naive baselines, the Random Forest substantially improves accuracy

### Forecast Quality by Store Type

| Store Type | Mean Absolute Error ($) |
|------------|-------------------------|
| A | 54,701.13 |
| B | 40,212.49 |
| C | 15,695.07 |

---

## Labor Conversion

### Configuration

- **Mode:** SPLH
- **Baseline Hours:** 8.0 hours/day × 7 days = 56.0 hours/week
- **Baseline Rationale:** Fixed tasks (opening, closing, stocking, admin) independent of sales volume

### Results

**Actual Hours (ex-post):**
- Mean: 5398.6 hours/week (771.2 hours/day)
- Median: 5071.5 hours/week
- Std Dev: 2487.8 hours/week

**Forecast Hours (ex-ante):**
- Mean: 5502.8 hours/week (786.1 hours/day)
- Median: 5117.2 hours/week
- Std Dev: 2511.8 hours/week

**Forecast vs Actual Delta:**
- Mean: +104.1 hours/week (+2.28%)
- Interpretation: Forecasts overestimate hours by 104.1 hours/week on average

### Hours by Store Type

| Store Type | Actual (hrs/wk) | Forecast (hrs/wk) | Delta (hrs/wk) |
|------------|-----------------|-------------------|----------------|
| A | 6727.2 | 6858.5 | +131.3 |
| B | 4418.2 | 4536.9 | +118.8 |
| C | 3305.3 | 3268.3 | -36.9 |

---

## Productivity Calibration

### BLS Benchmark Context

The BLS publishes labor productivity for **Supermarkets and other grocery stores (NAICS 445110)** 
as an index with 2017 = 100. This measures real output (deflated by industry price index) per hour worked.

### Our Implied Productivity

We compute implied productivity as:

```
Implied Productivity = Real Sales / Hours Actual
```

Where real sales are deflated using CPI from the features dataset.

### Comparison to BLS

| Quarter | Store Index | BLS Index | Deviation (pp) | Deviation (%) |
|---------|-------------|-----------|----------------|---------------|
| 2012-Q3 | 100.0 | 100.0 | +0.0 | +0.0% |
| 2012-Q4 | 99.8 | 100.0 | -0.2 | -0.2% |

### Interpretation

- **Mean Deviation:** -0.1%
- **Quarters Flagged (>±10%):** 0 / 2

Store productivity aligns well with industry benchmarks, suggesting SPLH assumptions are reasonable.

---

## Sensitivity Analysis

We test sensitivity to SPLH assumptions by varying the productivity parameter by [0.8, 0.9, 1.0, 1.1, 1.2]:

| SPLH Factor | Adjusted SPLH ($/hr) | Mean Hours/Week | Total Hours (all stores) |
|-------------|----------------------|-----------------|--------------------------|
| 0.8 | 148.62 | 6734.3 | 2,424,351 |
| 0.9 | 167.20 | 5992.3 | 2,157,219 |
| 1.0 | 185.78 | 5398.6 | 1,943,513 |
| 1.1 | 204.36 | 4913.0 | 1,768,663 |
| 1.2 | 222.93 | 4508.2 | 1,622,954 |

### Implications

- **Baseline:** 5398.6 hours/week
- **Range:** 4508.2 to 6734.3 hours/week
- **Spread:** 2226.1 hours/week (49.4% variation)

This demonstrates the operational risk from productivity assumptions. A 20% error in SPLH 
translates directly to a 20% error in planned hours.

---

## Why This Method Works

### Strengths

1. **Simple and Explainable**
   - Direct mapping from demand (sales/items) to labor hours
   - Easy to communicate to stakeholders
   - Transparent assumptions (SPLH/IPLH parameters)

2. **Quick What-If Analysis**
   - Adjust SPLH/IPLH to instantly see impact on hours
   - Sensitivity analysis reveals planning risk
   - Store/department-level customization possible

3. **Calibration to Industry Norms**
   - BLS productivity provides external validation
   - Flags unrealistic assumptions early
   - Ensures plans are grounded in industry benchmarks

4. **Actionable Outputs**
   - Weekly hour plans by store
   - Forecast error bounds propagate to hours
   - Ready for scheduling systems

---

## Limitations

### 1. Sales/Items May Not Equal Workload

- **Issue:** Some tasks are independent of sales volume (e.g., shelf resets, cleaning)
- **Mitigation:** We add baseline hours for fixed tasks
- **Residual Risk:** Task mix varies; SPLH/IPLH are averages

### 2. SPLH/IPLH Vary by Context

- **Product Mix:** Different categories have different handling requirements
- **Store Layout:** Efficiency varies with size and design
- **Processes:** Self-checkout, curbside pickup, etc. change productivity
- **Mitigation:** Use store type and department adjustments

### 3. BLS Productivity is an Aggregate Benchmark

- **Issue:** BLS data is industry-wide; individual stores vary
- **Issue:** BLS uses real output (value-added), we use sales
- **Issue:** Different deflators (industry price index vs CPI)
- **Interpretation:** BLS provides directional guidance, not ground truth

### 4. Forecast Error Propagates

- **Issue:** Hours are only as accurate as sales forecasts
- **Our Error:** 4.60% MAPE → same % error in hours
- **Mitigation:** Use probabilistic forecasts (future work)

### 5. Weekly Granularity

- **Issue:** Dataset is weekly; daily/hourly staffing needs may differ
- **Implication:** Assume even distribution across days (may not hold)
- **Future:** Intraweek/intraday models for shift planning

---

## Next Steps

### Near-Term Enhancements

1. **Department-Level Models**
   - Current: Store-level aggregates
   - Future: Model each department separately for task-specific SPLH/IPLH

2. **Probabilistic Forecasts**
   - Current: Point forecasts only
   - Future: Quantile regression or prediction intervals for robust planning

3. **Calibrate SPLH from Time Studies**
   - Current: Example/assumed SPLH values
   - Future: Estimate SPLH from historical hours and sales (if available)

### Advanced Extensions

4. **Erlang C for Checkout Staffing**
   - Use queueing theory to meet service level targets (e.g., <2 min wait)
   - Requires arrival rate estimates (transactions per hour)
   - See: [Erlang C Overview](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)

5. **Intraday/Intraweek Patterns**
   - Model hourly demand curves for shift scheduling
   - Account for peak hours, weekends, etc.

6. **Multi-Objective Optimization**
   - Minimize cost (hours) subject to service level constraints
   - Balance overstaffing risk vs understaffing risk

---

## References

### Data Sources

- [Corporación Favorita Grocery Sales Forecasting (Kaggle)](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)
- [Walmart Recruiting - Store Sales Forecasting (similar dataset structure)](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)
- [Example Analysis: Favorita Sales Forecasting](https://www.kaggle.com/code/sandraezzat/favorita-grocery-sales-forecasting)
- [Stanford CS221 Project Poster](https://web.stanford.edu/class/archive/cs/cs221/cs221.1192/2018/restricted/posters/jzhao4/poster.pdf)

### BLS Labor Productivity

- [BLS: Labor Productivity Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)
- [BLS: Productivity Program Overview](https://www.bls.gov/bls/productivity.htm)
- [FRED: Labor Productivity - Food & Beverage Stores](https://fred.stlouisfed.org/series/IPUHN445L001000000)
- [BLS: Labor Productivity vs Total Factor Productivity](https://www.bls.gov/productivity/educational-material/labor-productivity-total-factor-productivity-comparison.htm)
- [USAFacts: What is Labor Productivity?](https://usafacts.org/articles/what-is-labor-productivity-and-how-has-it-changed-in-the-us-over-time/)

### SPLH and IPLH Metrics

- [Sales Per Labor Hour (SPLH) - Restaurant Glossary](https://blackboxintelligence.com/resources/restaurant-glossary/sales-per-labor-hour/)
- [Items Per Labor Hour (IPLH) - Logile Blog](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)

### Advanced Topics (Future Work)

- [Erlang C Formula for Workforce Scheduling](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)

---

## Reproducibility

All analysis is fully reproducible:

1. Install dependencies: `pip install -r requirements.txt`
2. Run pipeline: `python run_all.py`
3. Outputs are saved to `output/` directory
4. Model artifacts saved to `models/` directory

**Random Seed:** 42
**Python Packages:** See `requirements.txt` for pinned versions

---

*End of Report*