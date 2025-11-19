# Retail Labour Demand Forecasting Report

**Generated:** 2025-11-19 13:49:33

---

## Executive Summary

This report presents a reproducible retail labor demand forecasting system that:

1. Forecasts daily store demand using Random Forest on Corporación Favorita dataset
2. Converts forecasts and actuals into labor hours using SPLH/IPLH parameters
3. Calibrates implied productivity against BLS labor productivity benchmarks
4. Provides sensitivity analysis to quantify planning risk

**Key Results:**

- Forecast MAE: 0.95 units
- Forecast MAPE: 1.53%
- Total hours forecast error: -0.01%
- Conversion mode: IPLH

---

## 1. Data Sources

### 1.1 Corporación Favorita Dataset

Historical sales data from the Corporación Favorita grocery sales forecasting competition:

- **Sales Data:** Weekly sales by store and department
  - 421,570 records
  - 45 stores, 81 departments
  - Date range: 2010-02-05 to 2012-10-26
- **Store Metadata:** Store type and size information
- **Features:** Temperature, fuel prices, CPI, unemployment, promotional markdowns, and holiday flags

### 1.2 BLS Labor Productivity

Bureau of Labor Statistics labor productivity series for retail:

- **Industry:** Supermarkets and other grocery stores (NAICS 445110)
- **Measure:** Labor productivity (output per hour worked)
- **Units:** Index (2017=100)
- **Purpose:** Industry benchmark for productivity calibration

---

## 2. Methodology

### 2.1 Feature Engineering

Data aggregated to daily store-level with the following features:

- **Calendar features:** Year, month, day, day of week, quarter, week of year
- **Cyclic encoding:** Sine/cosine transformations for month and day of week
- **Holiday indicators:** Current, pre-, and post-holiday flags
- **Promotion intensity:** Sum of markdown values and promotion flags
- **Economic features:** Temperature, fuel price, CPI, unemployment
- **Lagged features:** 7, 14, and 28-day lags for sales and units
- **Rolling features:** 7, 14, and 28-day rolling means (shifted to prevent leakage)

### 2.2 Forecasting Model

**Target Variable:** Total units/items per store per day

**Train/Test Split:**
- Last 4 weeks held out for testing
- Time-based split to respect temporal ordering

**Baseline Models:**
- Naive: Last observed value per store
- Seasonal Naive: Last value for same day of week per store
- Moving Average: Mean of last 4 weeks per store

**Random Forest:**
- Hyperparameter tuning via GridSearchCV with TimeSeriesSplit
- Cross-validation with 3 splits
- Optimized for mean absolute error

**Model Performance Comparison:**

| Model | MAE | RMSE | MAPE (%) |
|-------|-----|------|----------|
| Naive | 0.95 | 1.28 | 1.49 |
| Seasonal Naive | 0.95 | 1.28 | 1.49 |
| Moving Average | 0.91 | 1.17 | 1.45 |
| Random Forest | 0.95 | 1.23 | 1.53 |

### 2.3 Labor Conversion

Labor hours calculated using industry-standard metrics:

#### Sales per Labor Hour (SPLH)

SPLH measures sales revenue generated per labor hour:

$$
\text{SPLH} = \frac{\text{Sales (\\$)}}{\text{Labor Hours}}
$$

To calculate required hours from sales:

$$
\text{Hours} = \frac{\text{Sales (\\$)}}{\text{SPLH}}
$$

#### Items per Labor Hour (IPLH)

IPLH measures units/items processed per labor hour:

$$
\text{IPLH} = \frac{\text{Items (units)}}{\text{Labor Hours}}
$$

To calculate required hours from items:

$$
\text{Hours} = \frac{\text{Items (units)}}{\text{IPLH}}
$$

#### Configuration Used

- **Conversion Mode:** IPLH
- **Target IPLH:** 50.0 items/hour
- **Baseline Hours:** 8.0 hours/day per store
- **Total Hours:** Variable hours (demand-driven) + Baseline hours (fixed tasks)

#### BLS Labor Productivity

The Bureau of Labor Statistics defines labor productivity as:

$$
LP_t = \frac{\text{Real Output}_t}{\text{Hours Worked}_t}
$$

Where:
- **Real Output** = Inflation-adjusted output (constant dollars)
- **Hours Worked** = Total hours worked (not headcount)

**Important:** Labor productivity (output per hour) differs from output per worker,
which divides by employment rather than hours and can diverge when hours per worker change.

---

## 3. Results

### 3.1 Forecast Performance

- Average actual units: 65.97
- Average predicted units: 65.94
- Forecast bias: -0.03 units (-0.05%)

### 3.2 Labor Hours

**Actual Hours (Ex-Post):**
- Average variable hours per store-day: 1.31
- Average total hours per store-day: 9.31
- Total hours across all stores/days: 59911

**Forecasted Hours (Ex-Ante):**
- Average total hours per store-day: 9.32
- Total hours across test period: 1677

**Comparison:**
- Average hours error: -0.00 hours/day
- Average absolute hours error: 0.02 hours/day
- Total hours error: -0.01%

### 3.3 Productivity Analysis

**Implied Store Productivity:**
- Average units per hour: 7.02 items/hour
- Average sales per hour: $111741.18/hour (nominal)

**Note:** These are operational metrics. Direct comparison with BLS productivity
requires deflating sales to real terms. Units per hour is an operational efficiency
proxy, not economic productivity per se.

### 3.4 Sensitivity Analysis

**IPLH Sensitivity:**

Varying IPLH by ±30% shows operational risk from productivity assumptions:

| Scenario | Parameter Value | Total Hours | Change from Baseline |
|----------|----------------|-------------|----------------------|
| -30% | 35.00 | 1779 | +6.1% |
| -15% | 42.50 | 1719 | +2.5% |
| +0% | 50.00 | 1678 | +0.0% |
| +15% | 57.50 | 1647 | -1.8% |
| +30% | 65.00 | 1623 | -3.3% |

A ±30% variation in IPLH creates a **-157 hour** range
(-9.3% of baseline), exposing significant staffing risk.

---

## 4. Why This Method is Useful

1. **Simple and Explainable:** SPLH/IPLH are widely understood in retail operations
2. **Quick What-If Analysis:** Easy to adjust productivity assumptions and see impact
3. **Industry Calibration:** BLS benchmarks provide reality check on assumptions
4. **Actionable:** Directly translates demand forecasts into staffing plans
5. **Reproducible:** Fully scripted pipeline ensures consistency

---

## 5. Limitations

### 5.1 Conversion Limitations

- **Sales/units ≠ workload:** Not all tasks scale with sales (e.g., opening, closing, cleaning)
- **SPLH/IPLH vary by mix:** Different product categories require different labor
- **Process dependencies:** Checkout, stocking, and customer service have different drivers
- **Layout effects:** Store layout impacts labor efficiency but isn't captured

### 5.2 BLS Calibration Limitations

- **Aggregate benchmark:** BLS is industry-wide, not store-specific truth
- **Real vs nominal:** Our sales are nominal; BLS uses inflation-adjusted output
- **Units proxy:** Items per hour is operational efficiency, not economic productivity
- **Timing:** BLS annual data; our operations are daily/weekly

### 5.3 Forecast Limitations

- **Error propagation:** Forecast errors directly affect hour plans
- **Point forecasts:** No uncertainty quantification (see next steps)
- **Weekly granularity:** Original data is weekly, limiting daily insights
- **Limited features:** Could benefit from more granular promotional data

---

## 6. Next Steps

1. **Department-Level Models:** Separate forecasts by department with specific IPLH/SPLH
2. **Probabilistic Forecasts:** Quantile regression or prediction intervals for uncertainty
3. **Queueing Models:** Erlang C for checkout staffing based on service level objectives
4. **Real-Time Updates:** Integrate actual sales to refine hour plans intra-day
5. **Task-Based Models:** Decompose hours by task type (checkout, stocking, etc.)
6. **Optimization:** Schedule optimization given forecast hours and constraints

---

## 7. Output Files

This analysis generated the following files:

**Data Files:**
- `features_train.csv` - Training features and target
- `forecasts.csv` - Test set forecasts (date, store, actual, predicted)
- `hours_actual.csv` - Actual labor hours (ex-post)
- `hours_forecast.csv` - Forecasted labor hours (ex-ante)
- `hours_comparison.csv` - Side-by-side comparison with deltas
- `productivity_analysis.csv` - Implied productivity metrics
- `sensitivity_analysis.csv` - Sensitivity to IPLH/SPLH assumptions

**Model Artifacts:**
- `random_forest_model.joblib` - Trained Random Forest model
- `feature_names.joblib` - Feature column names
- `feature_importances.csv` - Feature importance scores

**Visualizations:**
- `hours_over_time.png` - Actual vs forecast hours timeline
- `hours_by_store.png` - Hours by store comparison
- `hours_parity_plot.png` - Actual vs forecast scatter
- `productivity_trends.png` - Productivity over time
- `bls_comparison.png` - BLS benchmark comparison
- `sensitivity_analysis.png` - Parameter sensitivity plots
- And more diagnostic plots...

---

## 8. References

1. **Corporación Favorita competition data:** [Kaggle Competition](https://www.kaggle.com/c/favorita-grocery-sales-forecasting/data)

2. **Favorita examples and write-ups:**
   - [Kaggle Notebook Example](https://www.kaggle.com/code/sandraezzat/favorita-grocery-sales-forecasting)
   - [Stanford CS221 Project Poster](https://web.stanford.edu/class/archive/cs/cs221/cs221.1192/2018/restricted/posters/jzhao4/poster.pdf)

3. **BLS labor productivity concepts:**
   - [Labor Productivity and Costs Concepts](https://www.bls.gov/opub/hom/msp/concepts.htm)
   - [BLS Productivity Overview](https://www.bls.gov/bls/productivity.htm)

4. **FRED labor productivity series:**
   - [Labor Productivity: Food & Beverage Stores](https://fred.stlouisfed.org/series/IPUHN445L001000000)

5. **SPLH and IPLH definitions:**
   - [Sales per Labor Hour Guide](https://blackboxintelligence.com/resources/restaurant-glossary/sales-per-labor-hour/)
   - [Measuring Retail Productivity](https://www.logile.com/resources/blog/measuring-retail-productivity-sales-per-labor-hour-or-items-per-labor-hour)

6. **Background on productivity:**
   - [Labor vs Total Factor Productivity](https://www.bls.gov/productivity/educational-material/labor-productivity-total-factor-productivity-comparison.htm)
   - [USAFacts Productivity Primer](https://usafacts.org/articles/what-is-labor-productivity-and-how-has-it-changed-in-the-us-over-time/)

7. **Erlang C for future extensions:**
   - [Erlang Formula Overview](https://help.calabrio.com/doc/Content/user-guides/schedules/about-erlang-formula.htm)

---

*Report generated by automated retail labor demand forecasting pipeline*
