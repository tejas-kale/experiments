"""
Section 6-8: Labor Conversion

This script implements SPLH/IPLH conversion functions, computes actual and
forecasted labor hours, and generates comparison outputs.
"""

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Import configuration
import config

warnings.filterwarnings('ignore')

print("=" * 80)
print("SECTION 6-8: LABOR CONVERSION")
print("=" * 80)

# ============================================================================
# SECTION 6: LABOR CONVERSION DEFINITIONS
# ============================================================================

print("\n--- Labor Conversion Definitions ---")

def hours_from_sales(sales, splh):
    """
    Calculate required labor hours from sales using SPLH.
    
    SPLH (Sales per Labor Hour) = Sales / Hours
    Therefore: Hours = Sales / SPLH
    
    Parameters:
    -----------
    sales : float or array-like
        Sales amount in dollars
    splh : float
        Target sales per labor hour ($/hour)
        
    Returns:
    --------
    hours : float or array-like
        Required labor hours
    """
    return sales / splh


def hours_from_items(items, iplh):
    """
    Calculate required labor hours from item count using IPLH.
    
    IPLH (Items per Labor Hour) = Items / Hours
    Therefore: Hours = Items / IPLH
    
    Parameters:
    -----------
    items : float or array-like
        Number of items/units
    iplh : float
        Target items per labor hour (items/hour)
        
    Returns:
    --------
    hours : float or array-like
        Required labor hours
    """
    return items / iplh


print(f"✓ Conversion mode: {config.CONVERSION_MODE}")

if config.CONVERSION_MODE == "SPLH":
    print(f"  Using SPLH (Sales per Labor Hour)")
    print(f"  Default SPLH: ${config.SPLH_PER_STORE['default']}/hour")
    print(f"  Formula: Hours = Sales / SPLH")
elif config.CONVERSION_MODE == "IPLH":
    print(f"  Using IPLH (Items per Labor Hour)")
    print(f"  Default IPLH: {config.IPLH_PER_STORE['default']} items/hour")
    print(f"  Formula: Hours = Items / IPLH")

print(f"  Baseline hours per store-day: {config.BASELINE_HOURS_PER_STORE_DAY} hours")
print("\nNote: BLS Labor Productivity is defined as:")
print("  LP_t = Real Output_t / Hours Worked_t (output per hour)")

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n--- Loading Data ---")

# Load feature-engineered data (for actuals)
intermediate_dir = config.OUTPUT_DIR / "intermediate"
df = pd.read_csv(intermediate_dir / "features_full.csv", parse_dates=['Date'])

# Load forecasts
forecasts = pd.read_csv(config.FORECASTS_PATH)

print(f"✓ Loaded feature data: {df.shape}")
print(f"✓ Loaded forecasts: {forecasts.shape}")

# ============================================================================
# SECTION 7: ACTUALS → LABOR (EX-POST)
# ============================================================================

print("\n--- Computing Actual Labor Hours ---")

# Prepare actuals dataframe
actuals = df[['Date', 'Store', 'total_sales', 'total_units']].copy()

# Apply conversion based on mode
if config.CONVERSION_MODE == "SPLH":
    # Get SPLH for each store (use default if not specified)
    actuals['splh'] = actuals['Store'].map(
        lambda x: config.SPLH_PER_STORE.get(x, config.SPLH_PER_STORE['default'])
    )
    actuals['hours_variable'] = hours_from_sales(actuals['total_sales'], actuals['splh'])
    
elif config.CONVERSION_MODE == "IPLH":
    # Get IPLH for each store (use default if not specified)
    actuals['iplh'] = actuals['Store'].map(
        lambda x: config.IPLH_PER_STORE.get(x, config.IPLH_PER_STORE['default'])
    )
    actuals['hours_variable'] = hours_from_items(actuals['total_units'], actuals['iplh'])

# Add baseline hours
actuals['hours_baseline'] = config.BASELINE_HOURS_PER_STORE_DAY
actuals['hours_total'] = actuals['hours_variable'] + actuals['hours_baseline']

# Select final columns
hours_actual = actuals[['Date', 'Store', 'total_sales', 'total_units', 
                         'hours_variable', 'hours_baseline', 'hours_total']].copy()

print(f"✓ Computed actual labor hours")
print(f"  Average variable hours per store-day: {hours_actual['hours_variable'].mean():.2f}")
print(f"  Average total hours per store-day: {hours_actual['hours_total'].mean():.2f}")
print(f"  Min total hours: {hours_actual['hours_total'].min():.2f}")
print(f"  Max total hours: {hours_actual['hours_total'].max():.2f}")

# Save hours_actual.csv
hours_actual.to_csv(config.HOURS_ACTUAL_PATH, index=False)
print(f"\n✓ Saved actual hours to: {config.HOURS_ACTUAL_PATH}")

# Summarize by store
print("\nActual hours summary by store (sample of 5 stores):")
store_summary = hours_actual.groupby('Store').agg({
    'hours_variable': ['mean', 'std'],
    'hours_total': ['mean', 'std']
}).round(2)
print(store_summary.head())

# Summarize over time
print("\nActual hours summary over time (last 10 periods):")
time_summary = hours_actual.groupby('Date').agg({
    'hours_variable': 'sum',
    'hours_total': 'sum'
}).round(2)
print(time_summary.tail(10))

# ============================================================================
# SECTION 8: FORECASTS → LABOR (EX-ANTE)
# ============================================================================

print("\n--- Computing Forecasted Labor Hours ---")

# Parse Date if needed
if 'Date' in forecasts.columns:
    forecasts['Date'] = pd.to_datetime(forecasts['Date'])

# For forecasts, we need sales values to compute SPLH-based hours
# Since we forecasted units (y_pred), we'll use IPLH mode primarily
# For SPLH mode, we'd need to convert units to sales (we'll use a simple proxy)

# Merge forecasts with actuals to get sales data
forecast_with_actuals = forecasts.merge(
    df[['Date', 'Store', 'total_sales', 'total_units']],
    on=['Date', 'Store'],
    how='left'
)

# Apply conversion based on mode
if config.CONVERSION_MODE == "SPLH":
    # For forecast, we need sales. 
    # Since we predicted units, estimate sales using actual sales/units ratio
    # Calculate average sales per unit
    avg_sales_per_unit = df['total_sales'].sum() / df['total_units'].sum()
    forecast_sales = forecast_with_actuals['y_pred'] * avg_sales_per_unit
    
    forecast_with_actuals['splh'] = forecast_with_actuals['Store'].map(
        lambda x: config.SPLH_PER_STORE.get(x, config.SPLH_PER_STORE['default'])
    )
    forecast_with_actuals['hours_variable'] = hours_from_sales(forecast_sales, forecast_with_actuals['splh'])
    
elif config.CONVERSION_MODE == "IPLH":
    # Use predicted units directly
    forecast_with_actuals['iplh'] = forecast_with_actuals['Store'].map(
        lambda x: config.IPLH_PER_STORE.get(x, config.IPLH_PER_STORE['default'])
    )
    forecast_with_actuals['hours_variable'] = hours_from_items(
        forecast_with_actuals['y_pred'], 
        forecast_with_actuals['iplh']
    )

# Add baseline hours
forecast_with_actuals['hours_baseline'] = config.BASELINE_HOURS_PER_STORE_DAY
forecast_with_actuals['hours_total'] = forecast_with_actuals['hours_variable'] + forecast_with_actuals['hours_baseline']

# Select final columns for hours_forecast
hours_forecast = forecast_with_actuals[['Date', 'Store', 'y_pred', 
                                         'hours_variable', 'hours_baseline', 'hours_total']].copy()
hours_forecast = hours_forecast.rename(columns={'y_pred': 'forecast_units'})

print(f"✓ Computed forecasted labor hours")
print(f"  Average variable hours per store-day: {hours_forecast['hours_variable'].mean():.2f}")
print(f"  Average total hours per store-day: {hours_forecast['hours_total'].mean():.2f}")

# Save hours_forecast.csv
hours_forecast.to_csv(config.HOURS_FORECAST_PATH, index=False)
print(f"\n✓ Saved forecasted hours to: {config.HOURS_FORECAST_PATH}")

# ============================================================================
# BUILD HOURS COMPARISON
# ============================================================================

print("\n--- Building Hours Comparison ---")

# Merge actual and forecast hours
comparison = forecast_with_actuals[['Date', 'Store', 'y_true', 'y_pred']].copy()

# Get actual hours for these dates/stores
comparison = comparison.merge(
    hours_actual[['Date', 'Store', 'hours_total']].rename(columns={'hours_total': 'hours_actual'}),
    on=['Date', 'Store'],
    how='left'
)

# Get forecast hours
comparison = comparison.merge(
    hours_forecast[['Date', 'Store', 'hours_total']].rename(columns={'hours_total': 'hours_forecast'}),
    on=['Date', 'Store'],
    how='left'
)

# Calculate delta
comparison['delta_hours'] = comparison['hours_forecast'] - comparison['hours_actual']

print(f"✓ Built comparison dataframe")
print(f"  Shape: {comparison.shape}")
print(f"  Average delta hours: {comparison['delta_hours'].mean():.2f}")
print(f"  Std delta hours: {comparison['delta_hours'].std():.2f}")

# Save hours_comparison.csv
comparison.to_csv(config.HOURS_COMPARISON_PATH, index=False)
print(f"\n✓ Saved hours comparison to: {config.HOURS_COMPARISON_PATH}")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

print("\n--- Creating Visualizations ---")

# Create visualization directory
viz_dir = config.OUTPUT_DIR / "visualizations"
viz_dir.mkdir(exist_ok=True)

# 1. Hours over time (aggregated across all stores)
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Aggregate by date
time_comparison = comparison.groupby('Date').agg({
    'hours_actual': 'sum',
    'hours_forecast': 'sum',
    'delta_hours': 'sum'
}).reset_index()

axes[0].plot(time_comparison['Date'], time_comparison['hours_actual'], 
             label='Actual Hours', marker='o', linewidth=2)
axes[0].plot(time_comparison['Date'], time_comparison['hours_forecast'], 
             label='Forecasted Hours', marker='s', linewidth=2)
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Total Hours (All Stores)')
axes[0].set_title('Actual vs Forecasted Labor Hours Over Time')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Delta over time
axes[1].bar(time_comparison['Date'], time_comparison['delta_hours'], 
            alpha=0.7, color='coral')
axes[1].axhline(y=0, color='black', linestyle='--', linewidth=1)
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Delta Hours (Forecast - Actual)')
axes[1].set_title('Labor Hours Forecast Error Over Time')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / 'hours_over_time.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved hours over time plot")

# 2. Hours by store (average)
fig, ax = plt.subplots(figsize=(14, 6))

store_comparison = comparison.groupby('Store').agg({
    'hours_actual': 'mean',
    'hours_forecast': 'mean'
}).reset_index()

x = np.arange(len(store_comparison))
width = 0.35

ax.bar(x - width/2, store_comparison['hours_actual'], width, 
       label='Actual Hours', alpha=0.8)
ax.bar(x + width/2, store_comparison['hours_forecast'], width, 
       label='Forecasted Hours', alpha=0.8)

ax.set_xlabel('Store')
ax.set_ylabel('Average Total Hours per Day')
ax.set_title('Average Daily Labor Hours by Store (Actual vs Forecast)')
ax.set_xticks(x)
ax.set_xticklabels(store_comparison['Store'])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(viz_dir / 'hours_by_store.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved hours by store plot")

# 3. Parity plot (actual vs forecast hours)
fig, ax = plt.subplots(figsize=(8, 8))

ax.scatter(comparison['hours_actual'], comparison['hours_forecast'], 
           alpha=0.5, s=30)

# Add diagonal line
min_val = min(comparison['hours_actual'].min(), comparison['hours_forecast'].min())
max_val = max(comparison['hours_actual'].max(), comparison['hours_forecast'].max())
ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Forecast')

ax.set_xlabel('Actual Hours')
ax.set_ylabel('Forecasted Hours')
ax.set_title('Labor Hours: Actual vs Forecast (Parity Plot)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / 'hours_parity_plot.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved parity plot")

print("\n" + "=" * 80)
print("LABOR CONVERSION COMPLETE")
print("=" * 80)
