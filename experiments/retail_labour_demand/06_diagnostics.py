"""
Section 10: Diagnostics and Sensitivity Analysis

This script generates diagnostic plots for forecast performance and performs
sensitivity analysis on SPLH/IPLH assumptions.
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
print("SECTION 10: DIAGNOSTICS AND SENSITIVITY ANALYSIS")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n--- Loading Data ---")

forecasts = pd.read_csv(config.FORECASTS_PATH, parse_dates=['Date'])
hours_comparison = pd.read_csv(config.HOURS_COMPARISON_PATH, parse_dates=['Date'])

print(f"✓ Loaded forecasts: {forecasts.shape}")
print(f"✓ Loaded hours comparison: {hours_comparison.shape}")

# ============================================================================
# FORECAST DIAGNOSTICS
# ============================================================================

print("\n--- Forecast Diagnostics ---")

# Calculate errors
forecasts['error'] = forecasts['y_pred'] - forecasts['y_true']
forecasts['abs_error'] = np.abs(forecasts['error'])
forecasts['pct_error'] = (forecasts['error'] / forecasts['y_true']) * 100

# Overall metrics
print(f"\nOverall forecast performance:")
print(f"  Mean Error (ME): {forecasts['error'].mean():.2f}")
print(f"  Mean Absolute Error (MAE): {forecasts['abs_error'].mean():.2f}")
print(f"  Root Mean Squared Error (RMSE): {np.sqrt((forecasts['error']**2).mean()):.2f}")
print(f"  Mean Absolute Percentage Error (MAPE): {forecasts['abs_error'].sum() / forecasts['y_true'].sum() * 100:.2f}%")

# By store
print("\nForecast performance by store (top 10 by MAE):")
store_metrics = forecasts.groupby('Store').agg({
    'error': 'mean',
    'abs_error': 'mean',
    'y_true': 'mean'
}).round(2)
store_metrics = store_metrics.rename(columns={
    'error': 'Mean_Error',
    'abs_error': 'MAE',
    'y_true': 'Avg_Actual'
})
print(store_metrics.nlargest(10, 'MAE'))

# By date
print("\nForecast performance by date:")
date_metrics = forecasts.groupby('Date').agg({
    'error': 'mean',
    'abs_error': 'mean',
    'y_true': 'sum',
    'y_pred': 'sum'
}).round(2)
print(date_metrics)

# ============================================================================
# HOURS DIAGNOSTICS
# ============================================================================

print("\n--- Hours Forecast Diagnostics ---")

# Hours errors
hours_comparison['hours_error'] = hours_comparison['delta_hours']
hours_comparison['hours_abs_error'] = np.abs(hours_comparison['hours_error'])

print(f"\nOverall hours forecast performance:")
print(f"  Mean Hours Error: {hours_comparison['hours_error'].mean():.2f}")
print(f"  Mean Absolute Hours Error: {hours_comparison['hours_abs_error'].mean():.2f}")
print(f"  Total Hours Actual: {hours_comparison['hours_actual'].sum():.2f}")
print(f"  Total Hours Forecast: {hours_comparison['hours_forecast'].sum():.2f}")
print(f"  Total Hours Difference: {hours_comparison['hours_error'].sum():.2f}")

# By store
print("\nHours forecast by store (top 10 by absolute error):")
store_hours_metrics = hours_comparison.groupby('Store').agg({
    'hours_error': 'mean',
    'hours_abs_error': 'mean',
    'hours_actual': 'mean'
}).round(2)
print(store_hours_metrics.nlargest(10, 'hours_abs_error'))

# ============================================================================
# DIAGNOSTIC VISUALIZATIONS
# ============================================================================

print("\n--- Creating Diagnostic Visualizations ---")

viz_dir = config.OUTPUT_DIR / "visualizations"
viz_dir.mkdir(exist_ok=True)

# 1. Forecast errors by store
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# MAE by store
store_mae = forecasts.groupby('Store')['abs_error'].mean().sort_values(ascending=False)
axes[0].bar(range(len(store_mae)), store_mae.values, alpha=0.7)
axes[0].set_xlabel('Store (sorted by MAE)')
axes[0].set_ylabel('Mean Absolute Error')
axes[0].set_title('Forecast MAE by Store')
axes[0].grid(True, alpha=0.3, axis='y')

# Error distribution
axes[1].hist(forecasts['error'], bins=50, alpha=0.7, edgecolor='black')
axes[1].axvline(x=0, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Forecast Error (Predicted - Actual)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Forecast Errors')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(viz_dir / 'forecast_diagnostics_by_store.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved forecast diagnostics by store")

# 2. Forecast errors over time
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

date_errors = forecasts.groupby('Date').agg({
    'error': 'mean',
    'abs_error': 'mean'
}).reset_index()

axes[0].plot(date_errors['Date'], date_errors['error'], marker='o', linewidth=2)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=1)
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Mean Error')
axes[0].set_title('Forecast Error Over Time')
axes[0].grid(True, alpha=0.3)

axes[1].plot(date_errors['Date'], date_errors['abs_error'], 
             marker='s', linewidth=2, color='orange')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Mean Absolute Error')
axes[1].set_title('Forecast MAE Over Time')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / 'forecast_diagnostics_by_date.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved forecast diagnostics by date")

# 3. Hours parity plots (already created in labor_conversion, but add more detail)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Parity plot with color by store
scatter = axes[0].scatter(hours_comparison['hours_actual'], 
                          hours_comparison['hours_forecast'],
                          c=hours_comparison['Store'], 
                          alpha=0.6, s=30, cmap='tab20')
min_val = min(hours_comparison['hours_actual'].min(), hours_comparison['hours_forecast'].min())
max_val = max(hours_comparison['hours_actual'].max(), hours_comparison['hours_forecast'].max())
axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Forecast')
axes[0].set_xlabel('Actual Hours')
axes[0].set_ylabel('Forecasted Hours')
axes[0].set_title('Hours Parity Plot (colored by Store)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Residuals plot
axes[1].scatter(hours_comparison['hours_actual'], hours_comparison['hours_error'],
                alpha=0.6, s=30)
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Actual Hours')
axes[1].set_ylabel('Hours Error (Forecast - Actual)')
axes[1].set_title('Hours Forecast Residuals')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / 'hours_parity_detailed.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved detailed hours parity plot")

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

print("\n--- Sensitivity Analysis on IPLH/SPLH ---")

# Load the feature data to get actuals
intermediate_dir = config.OUTPUT_DIR / "intermediate"
df = pd.read_csv(intermediate_dir / "features_full.csv", parse_dates=['Date'])

# Focus on test period
test_dates = sorted(forecasts['Date'].unique())
test_data = df[df['Date'].isin(test_dates)].copy()

print(f"\nAnalyzing sensitivity for {len(test_data)} test period observations")

# Define sensitivity ranges
if config.CONVERSION_MODE == "IPLH":
    baseline_value = config.IPLH_PER_STORE['default']
    param_name = "IPLH"
    output_col = 'total_units'
    
    # Vary IPLH by ±30%
    sensitivity_values = [
        baseline_value * 0.7,  # -30%
        baseline_value * 0.85, # -15%
        baseline_value,        # baseline
        baseline_value * 1.15, # +15%
        baseline_value * 1.3   # +30%
    ]
    
elif config.CONVERSION_MODE == "SPLH":
    baseline_value = config.SPLH_PER_STORE['default']
    param_name = "SPLH"
    output_col = 'total_sales'
    
    # Vary SPLH by ±30%
    sensitivity_values = [
        baseline_value * 0.7,
        baseline_value * 0.85,
        baseline_value,
        baseline_value * 1.15,
        baseline_value * 1.3
    ]

print(f"\n{param_name} sensitivity scenarios:")
print(f"  Baseline: {baseline_value:.2f}")
print(f"  Testing range: {sensitivity_values[0]:.2f} to {sensitivity_values[-1]:.2f}")

# Calculate hours for each scenario
sensitivity_results = []

for param_value in sensitivity_values:
    if config.CONVERSION_MODE == "IPLH":
        from importlib import reload
        # Import the hours_from_items function
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "labor_conversion",
            Path(__file__).parent / "04_labor_conversion.py"
        )
        labor_module = importlib.util.module_from_spec(spec)
        
        hours = test_data[output_col] / param_value
    else:  # SPLH
        hours = test_data[output_col] / param_value
    
    hours_with_baseline = hours + config.BASELINE_HOURS_PER_STORE_DAY
    
    sensitivity_results.append({
        f'{param_name}': param_value,
        'pct_change': ((param_value - baseline_value) / baseline_value) * 100,
        'avg_hours': hours_with_baseline.mean(),
        'total_hours': hours_with_baseline.sum(),
        'min_hours': hours_with_baseline.min(),
        'max_hours': hours_with_baseline.max()
    })

sensitivity_df = pd.DataFrame(sensitivity_results)

print(f"\n{param_name} Sensitivity Analysis Results:")
print(sensitivity_df.to_string(index=False))

# Calculate hour range sensitivity
baseline_total = sensitivity_df[sensitivity_df['pct_change'] == 0]['total_hours'].values[0]
min_total = sensitivity_df['total_hours'].min()
max_total = sensitivity_df['total_hours'].max()

print(f"\nTotal Hours Sensitivity:")
print(f"  Baseline scenario: {baseline_total:.0f} hours")
print(f"  Low {param_name} scenario (-30%): {max_total:.0f} hours (+{((max_total-baseline_total)/baseline_total)*100:.1f}%)")
print(f"  High {param_name} scenario (+30%): {min_total:.0f} hours ({((min_total-baseline_total)/baseline_total)*100:.1f}%)")
print(f"  Range: {max_total - min_total:.0f} hours")

# ============================================================================
# SENSITIVITY VISUALIZATION
# ============================================================================

print("\n--- Creating Sensitivity Visualizations ---")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Total hours vs parameter value
axes[0].plot(sensitivity_df[param_name], sensitivity_df['total_hours'], 
             marker='o', linewidth=2, markersize=8)
axes[0].axvline(x=baseline_value, color='red', linestyle='--', 
                linewidth=2, label=f'Baseline {param_name}')
axes[0].set_xlabel(f'{param_name} (items/hour)' if param_name == 'IPLH' else f'{param_name} ($/hour)')
axes[0].set_ylabel('Total Labor Hours (Test Period)')
axes[0].set_title(f'Sensitivity of Total Hours to {param_name}')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].invert_xaxis()  # Higher productivity = fewer hours

# Average hours vs parameter value with error bars
avg_hours_by_scenario = []
for param_value in sensitivity_values:
    if config.CONVERSION_MODE == "IPLH":
        hours = test_data[output_col] / param_value
    else:
        hours = test_data[output_col] / param_value
    hours_with_baseline = hours + config.BASELINE_HOURS_PER_STORE_DAY
    avg_hours_by_scenario.append(hours_with_baseline)

axes[1].boxplot(avg_hours_by_scenario, 
                labels=[f'{v:.1f}' for v in sensitivity_values],
                showmeans=True)
axes[1].axvline(x=3, color='red', linestyle='--', linewidth=2, 
                alpha=0.5, label='Baseline')  # Index 2 is baseline (0-indexed becomes 3 in plot)
axes[1].set_xlabel(f'{param_name} Value')
axes[1].set_ylabel('Labor Hours per Store-Day')
axes[1].set_title(f'Distribution of Hours Across {param_name} Scenarios')
axes[1].grid(True, alpha=0.3, axis='y')
axes[1].legend()

plt.tight_layout()
plt.savefig(viz_dir / 'sensitivity_analysis.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved sensitivity analysis plot")

# Save sensitivity results
sensitivity_path = config.OUTPUT_DIR / "sensitivity_analysis.csv"
sensitivity_df.to_csv(sensitivity_path, index=False)
print(f"✓ Saved sensitivity analysis to: {sensitivity_path}")

print("\n" + "=" * 80)
print("DIAGNOSTICS AND SENSITIVITY ANALYSIS COMPLETE")
print("=" * 80)
