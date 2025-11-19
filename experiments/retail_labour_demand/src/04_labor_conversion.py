"""
Sections 6-8: Labor Conversion from Sales/Items to Hours

This script:
1. Defines SPLH (Sales Per Labor Hour) and IPLH (Items Per Labor Hour) conversion functions
2. Converts actual sales to labor hours (ex-post)
3. Converts forecast sales to labor hours (ex-ante)
4. Compares actual vs forecast labor hours
5. Performs sensitivity analysis on productivity assumptions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Import configuration
import config

print("=" * 80)
print("Sections 6-8: Labor Conversion")
print("=" * 80)
print()

# ============================================================================
# Section 6: Labor Conversion Definitions
# ============================================================================

print("=" * 80)
print("Section 6: Labor Conversion Definitions")
print("=" * 80)
print()

print("Conversion Formulas:")
print("-" * 80)
print()
print("1. SPLH (Sales Per Labor Hour)")
print("   Definition: SPLH = Sales ($) / Labor Hours")
print("   Inverse:    Labor Hours = Sales ($) / SPLH")
print()
print("2. IPLH (Items Per Labor Hour)")
print("   Definition: IPLH = Items (units) / Labor Hours")
print("   Inverse:    Labor Hours = Items (units) / IPLH")
print()
print("3. BLS Labor Productivity")
print("   Definition: LP = Real Output / Hours Worked")
print("   (Output per hour, NOT output per worker)")
print()

def hours_from_sales(sales, splh):
    """
    Convert sales to labor hours using SPLH.

    Parameters:
    -----------
    sales : float or array-like
        Sales amount in dollars
    splh : float or array-like
        Sales per labor hour (dollars per hour)

    Returns:
    --------
    hours : float or array-like
        Required labor hours
    """
    return sales / splh


def hours_from_items(items, iplh):
    """
    Convert item count to labor hours using IPLH.

    Parameters:
    -----------
    items : float or array-like
        Number of items
    iplh : float or array-like
        Items per labor hour (items per hour)

    Returns:
    --------
    hours : float or array-like
        Required labor hours
    """
    return items / iplh


print("Conversion Configuration:")
print(f"  Mode: {config.CONVERSION_MODE}")
print(f"  Baseline hours per day: {config.BASELINE_HOURS_PER_DAY}")
print()

print("Productivity by Store Type:")
for store_type, params in config.PRODUCTIVITY_BY_STORE_TYPE.items():
    print(f"  Type {store_type}:")
    print(f"    SPLH: ${params['SPLH']:.2f}/hour")
    print(f"    IPLH: {params['IPLH']:.2f} items/hour")
print()

# ============================================================================
# Load Data
# ============================================================================

print("Loading data...")
forecasts_df = pd.read_csv(config.FORECASTS_CSV)
stores_df = joblib.load(config.OUTPUT_DIR / "stores_clean.pkl")

# Ensure Type is present
if 'Type' not in forecasts_df.columns:
    forecasts_df = forecasts_df.merge(stores_df[['Store', 'Type']], on='Store', how='left')

# Parse dates
forecasts_df['Date'] = pd.to_datetime(forecasts_df['Date'])

print(f"✓ Loaded {len(forecasts_df):,} forecast records")
print()

# ============================================================================
# Section 7: Actuals → Labor Hours (Ex-Post)
# ============================================================================

print("=" * 80)
print("Section 7: Actuals → Labor Hours (Ex-Post)")
print("=" * 80)
print()

print("Converting actual sales to labor hours...")

# Map SPLH/IPLH to each record based on store type
forecasts_df['SPLH'] = forecasts_df['Type'].map(
    lambda t: config.PRODUCTIVITY_BY_STORE_TYPE.get(t, {}).get('SPLH', 200.0)
)
forecasts_df['IPLH'] = forecasts_df['Type'].map(
    lambda t: config.PRODUCTIVITY_BY_STORE_TYPE.get(t, {}).get('IPLH', 50.0)
)

# Note: This dataset has weekly sales, not daily
# We'll treat each week as the planning unit and convert to weekly hours
# Then note that these would be distributed across 7 days

if config.CONVERSION_MODE == "SPLH":
    print(f"Using SPLH conversion...")
    # Weekly hours from weekly sales
    forecasts_df['Hours_Actual_Variable'] = hours_from_sales(
        forecasts_df['y_true'],
        forecasts_df['SPLH']
    )
elif config.CONVERSION_MODE == "IPLH":
    print(f"Using IPLH conversion...")
    # This dataset doesn't have item counts, so we'll use a proxy
    # Estimate items as sales / average_item_price
    avg_item_price = 10.0  # Assume $10 per item (example)
    estimated_items = forecasts_df['y_true'] / avg_item_price
    forecasts_df['Hours_Actual_Variable'] = hours_from_items(
        estimated_items,
        forecasts_df['IPLH']
    )
    print(f"  Note: Using estimated item count (sales / ${avg_item_price})")
else:
    raise ValueError(f"Unknown conversion mode: {config.CONVERSION_MODE}")

# Add baseline hours (fixed tasks)
# Baseline is daily, so multiply by 7 for weekly
forecasts_df['Hours_Actual_Baseline'] = config.BASELINE_HOURS_PER_DAY * 7

# Total hours = variable + baseline
forecasts_df['Hours_Actual'] = (
    forecasts_df['Hours_Actual_Variable'] +
    forecasts_df['Hours_Actual_Baseline']
)

print(f"✓ Actual hours calculated")
print()

# Summary statistics
print("Actual Hours Summary (per week):")
print(f"  Mean variable hours:  {forecasts_df['Hours_Actual_Variable'].mean():.2f}")
print(f"  Mean baseline hours:  {forecasts_df['Hours_Actual_Baseline'].mean():.2f}")
print(f"  Mean total hours:     {forecasts_df['Hours_Actual'].mean():.2f}")
print(f"  Median total hours:   {forecasts_df['Hours_Actual'].median():.2f}")
print(f"  Std total hours:      {forecasts_df['Hours_Actual'].std():.2f}")
print()

# By store type
print("Actual Hours by Store Type:")
by_type = forecasts_df.groupby('Type')['Hours_Actual'].agg(['mean', 'median', 'std'])
print(by_type.round(2).to_string())
print()

# ============================================================================
# Section 8: Forecasts → Labor Hours (Ex-Ante)
# ============================================================================

print("=" * 80)
print("Section 8: Forecasts → Labor Hours (Ex-Ante)")
print("=" * 80)
print()

print("Converting forecast sales to labor hours...")

if config.CONVERSION_MODE == "SPLH":
    forecasts_df['Hours_Forecast_Variable'] = hours_from_sales(
        forecasts_df['y_pred'],
        forecasts_df['SPLH']
    )
elif config.CONVERSION_MODE == "IPLH":
    estimated_items_pred = forecasts_df['y_pred'] / avg_item_price
    forecasts_df['Hours_Forecast_Variable'] = hours_from_items(
        estimated_items_pred,
        forecasts_df['IPLH']
    )

# Add baseline hours (same as actuals)
forecasts_df['Hours_Forecast_Baseline'] = config.BASELINE_HOURS_PER_DAY * 7

# Total hours
forecasts_df['Hours_Forecast'] = (
    forecasts_df['Hours_Forecast_Variable'] +
    forecasts_df['Hours_Forecast_Baseline']
)

print(f"✓ Forecast hours calculated")
print()

# Summary statistics
print("Forecast Hours Summary (per week):")
print(f"  Mean variable hours:  {forecasts_df['Hours_Forecast_Variable'].mean():.2f}")
print(f"  Mean baseline hours:  {forecasts_df['Hours_Forecast_Baseline'].mean():.2f}")
print(f"  Mean total hours:     {forecasts_df['Hours_Forecast'].mean():.2f}")
print(f"  Median total hours:   {forecasts_df['Hours_Forecast'].median():.2f}")
print(f"  Std total hours:      {forecasts_df['Hours_Forecast'].std():.2f}")
print()

# ============================================================================
# Hours Comparison
# ============================================================================

print("=" * 80)
print("Actual vs Forecast Hours Comparison")
print("=" * 80)
print()

# Calculate delta
forecasts_df['Delta_Hours'] = forecasts_df['Hours_Forecast'] - forecasts_df['Hours_Actual']
forecasts_df['Delta_Hours_Pct'] = (
    forecasts_df['Delta_Hours'] / forecasts_df['Hours_Actual'] * 100
)

print("Hours Delta Summary:")
print(f"  Mean delta:    {forecasts_df['Delta_Hours'].mean():+.2f} hours/week")
print(f"  Median delta:  {forecasts_df['Delta_Hours'].median():+.2f} hours/week")
print(f"  Std delta:     {forecasts_df['Delta_Hours'].std():.2f} hours/week")
print(f"  Mean % delta:  {forecasts_df['Delta_Hours_Pct'].mean():+.2f}%")
print()

# By store type
print("Hours Delta by Store Type:")
by_type_delta = forecasts_df.groupby('Type')['Delta_Hours'].agg(['mean', 'median', 'std'])
print(by_type_delta.round(2).to_string())
print()

# ============================================================================
# Save Hours DataFrames
# ============================================================================

print("=" * 80)
print("Saving Hours DataFrames")
print("=" * 80)
print()

# Hours actual
hours_actual = forecasts_df[[
    'Store', 'Date', 'Type', 'y_true',
    'SPLH', 'IPLH',
    'Hours_Actual_Variable', 'Hours_Actual_Baseline', 'Hours_Actual'
]].copy()
hours_actual.to_csv(config.HOURS_ACTUAL_CSV, index=False)
print(f"✓ Saved: {config.HOURS_ACTUAL_CSV}")

# Hours forecast
hours_forecast = forecasts_df[[
    'Store', 'Date', 'Type', 'y_pred',
    'SPLH', 'IPLH',
    'Hours_Forecast_Variable', 'Hours_Forecast_Baseline', 'Hours_Forecast'
]].copy()
hours_forecast.to_csv(config.HOURS_FORECAST_CSV, index=False)
print(f"✓ Saved: {config.HOURS_FORECAST_CSV}")

# Hours comparison
hours_comparison = forecasts_df[[
    'Store', 'Date', 'Type',
    'y_true', 'y_pred',
    'Hours_Actual', 'Hours_Forecast', 'Delta_Hours', 'Delta_Hours_Pct'
]].copy()
hours_comparison.to_csv(config.HOURS_COMPARISON_CSV, index=False)
print(f"✓ Saved: {config.HOURS_COMPARISON_CSV}")
print()

# ============================================================================
# Section 10: Sensitivity Analysis
# ============================================================================

print("=" * 80)
print("Section 10: Sensitivity Analysis")
print("=" * 80)
print()

print(f"Testing SPLH sensitivity with range: {config.SENSITIVITY_RANGE}")
print()

sensitivity_results = []

for factor in config.SENSITIVITY_RANGE:
    # Adjust SPLH
    adjusted_splh = forecasts_df['SPLH'] * factor

    # Recalculate hours
    if config.CONVERSION_MODE == "SPLH":
        hours_adjusted = hours_from_sales(forecasts_df['y_true'], adjusted_splh)
    else:
        hours_adjusted = hours_from_items(
            forecasts_df['y_true'] / avg_item_price,
            forecasts_df['IPLH'] * factor
        )

    hours_adjusted += config.BASELINE_HOURS_PER_DAY * 7

    sensitivity_results.append({
        'SPLH_Factor': factor,
        'SPLH_Adjusted': (forecasts_df['SPLH'] * factor).mean(),
        'Mean_Hours': hours_adjusted.mean(),
        'Median_Hours': hours_adjusted.median(),
        'Total_Hours': hours_adjusted.sum(),
    })

sensitivity_df = pd.DataFrame(sensitivity_results)
print("Sensitivity Analysis Results:")
print(sensitivity_df.to_string(index=False))
print()

# Save sensitivity
sensitivity_df.to_csv(config.OUTPUT_DIR / "sensitivity_analysis.csv", index=False)
print(f"✓ Saved: sensitivity_analysis.csv")
print()

# ============================================================================
# Visualizations
# ============================================================================

if config.SAVE_PLOTS:
    print("=" * 80)
    print("Generating Visualizations")
    print("=" * 80)
    print()

    # 1. Actual vs Forecast Hours
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(forecasts_df['Hours_Actual'], forecasts_df['Hours_Forecast'], alpha=0.4)
    min_h = min(forecasts_df['Hours_Actual'].min(), forecasts_df['Hours_Forecast'].min())
    max_h = max(forecasts_df['Hours_Actual'].max(), forecasts_df['Hours_Forecast'].max())
    ax.plot([min_h, max_h], [min_h, max_h], 'r--', lw=2, label='Perfect Forecast')
    ax.set_xlabel('Actual Hours (per week)')
    ax.set_ylabel('Forecast Hours (per week)')
    ax.set_title('Labor Hours: Actual vs Forecast')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'hours_parity.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: hours_parity.png")

    # 2. Hours over time for sample stores
    sample_stores = forecasts_df['Store'].unique()[:5]
    fig, axes = plt.subplots(5, 1, figsize=(14, 12))
    for idx, store in enumerate(sample_stores):
        store_data = forecasts_df[forecasts_df['Store'] == store].sort_values('Date')
        ax = axes[idx]
        ax.plot(store_data['Date'], store_data['Hours_Actual'], 'o-',
                label='Actual Hours', alpha=0.7)
        ax.plot(store_data['Date'], store_data['Hours_Forecast'], 's-',
                label='Forecast Hours', alpha=0.7)
        ax.set_title(f'Store {store} - Type {store_data["Type"].iloc[0]}')
        ax.set_ylabel('Hours/Week')
        ax.legend()
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel('Date')
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'hours_time_series.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: hours_time_series.png")

    # 3. Hours by store type
    fig, ax = plt.subplots(figsize=(10, 6))
    forecasts_df.boxplot(column='Hours_Actual', by='Type', ax=ax)
    ax.set_xlabel('Store Type')
    ax.set_ylabel('Actual Hours (per week)')
    ax.set_title('Labor Hours Distribution by Store Type')
    plt.suptitle('')  # Remove default title
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'hours_by_type.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: hours_by_type.png")

    # 4. Sensitivity chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sensitivity_df['SPLH_Factor'], sensitivity_df['Mean_Hours'], 'o-', lw=2)
    ax.axvline(x=1.0, color='r', linestyle='--', label='Baseline')
    ax.set_xlabel('SPLH Adjustment Factor')
    ax.set_ylabel('Mean Weekly Hours')
    ax.set_title('Sensitivity of Labor Hours to SPLH Assumptions')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'sensitivity_splh.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: sensitivity_splh.png")

    print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Conversion mode: {config.CONVERSION_MODE}")
print(f"Total forecast records: {len(forecasts_df):,}")
print(f"Mean actual hours/week: {forecasts_df['Hours_Actual'].mean():.2f}")
print(f"Mean forecast hours/week: {forecasts_df['Hours_Forecast'].mean():.2f}")
print(f"Mean hours delta: {forecasts_df['Delta_Hours'].mean():+.2f}")
print(f"Mean % delta: {forecasts_df['Delta_Hours_Pct'].mean():+.2f}%")
print()
print("Daily equivalent (divide by 7):")
print(f"  Actual: {forecasts_df['Hours_Actual'].mean()/7:.2f} hours/day")
print(f"  Forecast: {forecasts_df['Hours_Forecast'].mean()/7:.2f} hours/day")
print()
print("✓ Labor conversion complete!")
print("=" * 80)
