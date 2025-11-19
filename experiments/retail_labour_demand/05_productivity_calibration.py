"""
Section 9: Productivity Calibration vs BLS

This script computes implied store productivity and compares it with BLS 
benchmark labor productivity for the retail sector.
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
print("SECTION 9: PRODUCTIVITY CALIBRATION VS BLS")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n--- Loading Data ---")

# Load BLS productivity data
intermediate_dir = config.OUTPUT_DIR / "intermediate"
bls_df = pd.read_csv(intermediate_dir / "bls_clean.csv")

# Load hours actual (contains output and hours)
hours_actual = pd.read_csv(config.HOURS_ACTUAL_PATH, parse_dates=['Date'])

print(f"✓ Loaded BLS productivity data: {bls_df.shape}")
print(f"✓ Loaded actual hours data: {hours_actual.shape}")

# ============================================================================
# COMPUTE IMPLIED STORE PRODUCTIVITY
# ============================================================================

print("\n--- Computing Implied Store Productivity ---")

# BLS defines labor productivity as: LP = Real Output / Hours Worked
# For stores, we can compute an operational proxy:
# - If we have revenue: Productivity ≈ Revenue / Hours (nominal, should be deflated)
# - If we have units: Productivity = Units / Hours (operational proxy)

# We'll compute both and note that units-based is an operational proxy

# 1. Units-based productivity (operational proxy)
hours_actual['productivity_units'] = hours_actual['total_units'] / hours_actual['hours_total']

# 2. Sales-based productivity (nominal, ideally should be deflated)
hours_actual['productivity_sales'] = hours_actual['total_sales'] / hours_actual['hours_total']

print(f"✓ Computed implied productivity metrics")
print(f"\nUnits-based productivity (items per hour):")
print(f"  Mean: {hours_actual['productivity_units'].mean():.2f} items/hour")
print(f"  Median: {hours_actual['productivity_units'].median():.2f} items/hour")
print(f"  Std: {hours_actual['productivity_units'].std():.2f}")

print(f"\nSales-based productivity ($/hour, nominal):")
print(f"  Mean: ${hours_actual['productivity_sales'].mean():.2f}/hour")
print(f"  Median: ${hours_actual['productivity_sales'].median():.2f}/hour")
print(f"  Std: ${hours_actual['productivity_sales'].std():.2f}")

# Add year for comparison with BLS
hours_actual['year'] = pd.to_datetime(hours_actual['Date']).dt.year

# Aggregate productivity by year
yearly_productivity = hours_actual.groupby('year').agg({
    'productivity_units': 'mean',
    'productivity_sales': 'mean',
    'total_units': 'sum',
    'total_sales': 'sum',
    'hours_total': 'sum'
}).reset_index()

# Recalculate aggregate productivity
yearly_productivity['productivity_units_agg'] = (
    yearly_productivity['total_units'] / yearly_productivity['hours_total']
)
yearly_productivity['productivity_sales_agg'] = (
    yearly_productivity['total_sales'] / yearly_productivity['hours_total']
)

print("\nYearly aggregate productivity:")
print(yearly_productivity[['year', 'productivity_units_agg', 'productivity_sales_agg']])

# ============================================================================
# COMPARE WITH BLS BENCHMARK
# ============================================================================

print("\n--- Comparing with BLS Benchmark ---")

# Display BLS data context
print("\nBLS Labor Productivity Series:")
if 'Industry' in bls_df.columns:
    print(f"  Industry: {bls_df['Industry'].iloc[0]}")
if 'Measure' in bls_df.columns:
    print(f"  Measure: {bls_df['Measure'].iloc[0]}")
if 'Units' in bls_df.columns:
    print(f"  Units: {bls_df['Units'].iloc[0]}")

# Note on comparability
print("\n" + "=" * 80)
print("IMPORTANT NOTES ON PRODUCTIVITY COMPARISON")
print("=" * 80)
print("""
1. BLS Labor Productivity Definition:
   - LP_t = Real Output_t / Hours Worked_t
   - Output is in constant (real) dollars, adjusted for inflation
   - This is an index (typically 2017=100) showing productivity trends
   
2. Our Store Metrics:
   - Units-based: Items/Hour (operational proxy, not directly comparable)
   - Sales-based: $/Hour (nominal, not inflation-adjusted)
   
3. Key Differences:
   - BLS uses real (inflation-adjusted) output; ours uses nominal sales
   - BLS is an index showing trends; ours are absolute values
   - BLS covers entire industry; ours are specific store operations
   - Units/hour is an operational efficiency metric, not economic productivity
   
4. Interpretation:
   - We can compare TRENDS over time, not absolute levels
   - A deflator (CPI) would be needed to make sales comparable to BLS
   - Units/hour is useful for operations but distinct from economic productivity
""")

# ============================================================================
# TREND COMPARISON
# ============================================================================

print("\n--- Trend Analysis ---")

# Get BLS data for the years in our dataset
years_in_data = sorted(hours_actual['year'].unique())
print(f"\nYears in our data: {years_in_data}")

bls_filtered = bls_df[bls_df['Year'].isin(years_in_data)].copy()

# Convert Value to numeric if needed
if 'Value' in bls_filtered.columns:
    bls_filtered['Value'] = pd.to_numeric(bls_filtered['Value'], errors='coerce')

print(f"BLS data for these years:")
print(bls_filtered[['Year', 'Value']])

# Calculate year-over-year change
if len(yearly_productivity) > 1:
    yearly_productivity['units_pct_change'] = yearly_productivity['productivity_units_agg'].pct_change() * 100
    yearly_productivity['sales_pct_change'] = yearly_productivity['productivity_sales_agg'].pct_change() * 100
    
    print("\nYear-over-year productivity changes (our data):")
    print(yearly_productivity[['year', 'units_pct_change', 'sales_pct_change']])

if len(bls_filtered) > 1:
    bls_filtered = bls_filtered.sort_values('Year')
    bls_filtered['bls_pct_change'] = bls_filtered['Value'].pct_change() * 100
    
    print("\nYear-over-year BLS productivity changes:")
    print(bls_filtered[['Year', 'Value', 'bls_pct_change']])

# ============================================================================
# DETECT UNREALISTIC PRODUCTIVITY ASSUMPTIONS
# ============================================================================

print("\n--- Productivity Reality Check ---")

# Check if any store-periods have unrealistically high or low productivity
# Based on typical retail benchmarks:
# - Grocery retail: typically 20-70 items per hour depending on tasks
# - Sales per hour: typically $100-$300 depending on store format

REASONABLE_UNITS_MIN = 10  # items/hour
REASONABLE_UNITS_MAX = 100  # items/hour
REASONABLE_SALES_MIN = 50  # $/hour
REASONABLE_SALES_MAX = 500  # $/hour

unrealistic_low_units = hours_actual[hours_actual['productivity_units'] < REASONABLE_UNITS_MIN]
unrealistic_high_units = hours_actual[hours_actual['productivity_units'] > REASONABLE_UNITS_MAX]
unrealistic_low_sales = hours_actual[hours_actual['productivity_sales'] < REASONABLE_SALES_MIN]
unrealistic_high_sales = hours_actual[hours_actual['productivity_sales'] > REASONABLE_SALES_MAX]

print(f"\nProductivity flags (based on typical retail benchmarks):")
print(f"  Periods with low units productivity (<{REASONABLE_UNITS_MIN} items/hr): {len(unrealistic_low_units)}")
print(f"  Periods with high units productivity (>{REASONABLE_UNITS_MAX} items/hr): {len(unrealistic_high_units)}")
print(f"  Periods with low sales productivity (<${REASONABLE_SALES_MIN}/hr): {len(unrealistic_low_sales)}")
print(f"  Periods with high sales productivity (>${REASONABLE_SALES_MAX}/hr): {len(unrealistic_high_sales)}")

if len(unrealistic_high_units) > 0:
    print(f"\n  Warning: {len(unrealistic_high_units)} periods show unusually high productivity")
    print(f"  This may indicate understaffing or aggressive IPLH assumptions")

if len(unrealistic_low_units) > 0:
    print(f"\n  Warning: {len(unrealistic_low_units)} periods show unusually low productivity")
    print(f"  This may indicate overstaffing or conservative IPLH assumptions")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

print("\n--- Creating Visualizations ---")

viz_dir = config.OUTPUT_DIR / "visualizations"
viz_dir.mkdir(exist_ok=True)

# 1. Productivity over time
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Units productivity
monthly_prod = hours_actual.groupby(pd.Grouper(key='Date', freq='M')).agg({
    'productivity_units': 'mean',
    'productivity_sales': 'mean'
}).reset_index()

axes[0].plot(monthly_prod['Date'], monthly_prod['productivity_units'], 
             marker='o', linewidth=2, label='Units per Hour')
axes[0].axhline(y=config.IPLH_PER_STORE['default'], color='red', 
                linestyle='--', linewidth=2, label=f'Target IPLH ({config.IPLH_PER_STORE["default"]})')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Items per Hour')
axes[0].set_title('Store Productivity: Units per Hour (Monthly Average)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Sales productivity
axes[1].plot(monthly_prod['Date'], monthly_prod['productivity_sales'], 
             marker='s', linewidth=2, color='green', label='Sales per Hour')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Sales ($/hour)')
axes[1].set_title('Store Productivity: Sales per Hour (Monthly Average, Nominal)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / 'productivity_trends.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved productivity trends plot")

# 2. BLS comparison (if data available)
if len(bls_filtered) > 0 and len(yearly_productivity) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Normalize both series to 100 at first year for trend comparison
    bls_normalized = bls_filtered.copy()
    bls_normalized['normalized'] = (bls_normalized['Value'] / bls_normalized['Value'].iloc[0]) * 100
    
    store_normalized = yearly_productivity.copy()
    store_normalized['normalized'] = (
        store_normalized['productivity_sales_agg'] / 
        store_normalized['productivity_sales_agg'].iloc[0]
    ) * 100
    
    ax.plot(bls_normalized['Year'], bls_normalized['normalized'], 
            marker='o', linewidth=2, label='BLS Retail Productivity (Index)')
    ax.plot(store_normalized['year'], store_normalized['normalized'], 
            marker='s', linewidth=2, label='Store Sales/Hour (Normalized)')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Index (First Year = 100)')
    ax.set_title('Productivity Trend Comparison: BLS vs Store (Normalized)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(viz_dir / 'bls_comparison.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"✓ Saved BLS comparison plot")

# 3. Distribution of productivity
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(hours_actual['productivity_units'], bins=50, alpha=0.7, edgecolor='black')
axes[0].axvline(x=config.IPLH_PER_STORE['default'], color='red', 
                linestyle='--', linewidth=2, label=f'Target ({config.IPLH_PER_STORE["default"]})')
axes[0].set_xlabel('Items per Hour')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Units Productivity')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

axes[1].hist(hours_actual['productivity_sales'], bins=50, alpha=0.7, 
             color='green', edgecolor='black')
axes[1].set_xlabel('Sales ($/hour)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Sales Productivity')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(viz_dir / 'productivity_distribution.png', dpi=config.FIGURE_DPI, bbox_inches='tight')
print(f"✓ Saved productivity distribution plot")

# ============================================================================
# SAVE PRODUCTIVITY DATA
# ============================================================================

print("\n--- Saving Productivity Data ---")

productivity_path = config.OUTPUT_DIR / "productivity_analysis.csv"
hours_actual[['Date', 'Store', 'total_units', 'total_sales', 'hours_total',
              'productivity_units', 'productivity_sales']].to_csv(
    productivity_path, index=False
)
print(f"✓ Saved productivity analysis to: {productivity_path}")

print("\n" + "=" * 80)
print("PRODUCTIVITY CALIBRATION COMPLETE")
print("=" * 80)
