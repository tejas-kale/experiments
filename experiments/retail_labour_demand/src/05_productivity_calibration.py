"""
Section 9: Productivity Calibration vs BLS

This script:
1. Computes implied store productivity from our labor hours and sales
2. Compares implied productivity trajectory to BLS industry benchmark
3. Flags periods where implied productivity deviates from industry norms
4. Explains the distinction between labor productivity (output/hour) and output per worker
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
from scipy import stats

# Import configuration
import config

print("=" * 80)
print("Section 9: Productivity Calibration vs BLS")
print("=" * 80)
print()

# ============================================================================
# Load Data
# ============================================================================

print("Loading data...")
hours_comparison = pd.read_csv(config.HOURS_COMPARISON_CSV)
hours_comparison['Date'] = pd.to_datetime(hours_comparison['Date'])

bls_df = joblib.load(config.OUTPUT_DIR / "bls_clean.pkl")

print(f"✓ Loaded {len(hours_comparison):,} hours records")
print(f"✓ Loaded {len(bls_df)} BLS productivity records")
print()

# ============================================================================
# BLS Labor Productivity Overview
# ============================================================================

print("=" * 80)
print("BLS Labor Productivity Benchmark")
print("=" * 80)
print()

print("BLS Definition:")
print("  Labor Productivity (LP) = Real Output / Hours Worked")
print("  • Measures output per hour, NOT output per worker")
print("  • Output per worker = Output / Employment (can diverge when hours/worker change)")
print("  • Real output is deflated by industry price index")
print()

print(f"Industry: {bls_df['Industry'].iloc[0]}")
print(f"NAICS Level: {bls_df['Digit'].iloc[0]}")
print(f"Measure: {bls_df['Measure'].iloc[0]}")
print(f"Units: {bls_df['Units'].iloc[0]}")
print()

# Filter to study period
bls_study = bls_df[
    (bls_df['Year'] >= config.BLS_COMPARISON_START_YEAR) &
    (bls_df['Year'] <= config.BLS_COMPARISON_END_YEAR)
].copy()

print(f"BLS Productivity during study period:")
print(bls_study[['Year', 'Value']].to_string(index=False))
print()

# Calculate year-over-year growth
bls_study['YoY_Growth'] = bls_study['Value'].pct_change() * 100

print("Year-over-Year Productivity Growth:")
for _, row in bls_study.iterrows():
    if pd.notna(row['YoY_Growth']):
        print(f"  {row['Year']}: {row['YoY_Growth']:+.2f}%")
print()

# ============================================================================
# Compute Implied Store Productivity
# ============================================================================

print("=" * 80)
print("Compute Implied Store Productivity")
print("=" * 80)
print()

print("Approach:")
print("  1. We have: Sales ($) and Hours (from our conversion)")
print("  2. Implied Productivity = Sales / Hours ($/hour)")
print("  3. Note: This is nominal sales per hour, not real output per hour")
print("  4. We'll deflate using CPI to approximate real productivity")
print()

# Add year and quarter for aggregation
hours_comparison['Year'] = hours_comparison['Date'].dt.year
hours_comparison['Quarter'] = hours_comparison['Date'].dt.quarter
hours_comparison['YearQuarter'] = (
    hours_comparison['Year'].astype(str) + '-Q' +
    hours_comparison['Quarter'].astype(str)
)

# Compute implied productivity (nominal)
hours_comparison['Implied_Productivity_Nominal'] = (
    hours_comparison['y_true'] / hours_comparison['Hours_Actual']
)

print("Implied Nominal Productivity ($/hour):")
print(f"  Mean: ${hours_comparison['Implied_Productivity_Nominal'].mean():.2f}/hour")
print(f"  Median: ${hours_comparison['Implied_Productivity_Nominal'].median():.2f}/hour")
print(f"  Std: ${hours_comparison['Implied_Productivity_Nominal'].std():.2f}/hour")
print()

# ============================================================================
# Deflate to Real Terms
# ============================================================================

print("Deflating to real terms using CPI...")

# Load CPI from features
features_df = joblib.load(config.OUTPUT_DIR / "features_clean.pkl")
features_df['Date'] = pd.to_datetime(features_df['Date'])

# Get CPI for each store-date
cpi_data = features_df[['Store', 'Date', 'CPI']].drop_duplicates()

# Merge CPI into hours_comparison
hours_comparison = hours_comparison.merge(
    cpi_data,
    on=['Store', 'Date'],
    how='left'
)

# Use forward fill for any missing CPI
hours_comparison['CPI'] = hours_comparison.groupby('Store')['CPI'].fillna(method='ffill')

# Calculate reference CPI (earliest period)
reference_cpi = hours_comparison['CPI'].min()
print(f"  Reference CPI (base): {reference_cpi:.2f}")
print()

# Deflate sales
hours_comparison['y_true_real'] = (
    hours_comparison['y_true'] * (reference_cpi / hours_comparison['CPI'])
)

# Compute real productivity
hours_comparison['Implied_Productivity_Real'] = (
    hours_comparison['y_true_real'] / hours_comparison['Hours_Actual']
)

print("Implied Real Productivity (constant $, per hour):")
print(f"  Mean: ${hours_comparison['Implied_Productivity_Real'].mean():.2f}/hour")
print(f"  Median: ${hours_comparison['Implied_Productivity_Real'].median():.2f}/hour")
print(f"  Std: ${hours_comparison['Implied_Productivity_Real'].std():.2f}/hour")
print()

# ============================================================================
# Aggregate to Quarterly Level
# ============================================================================

print("Aggregating to quarterly level for comparison with BLS...")

# Aggregate to year-quarter
quarterly = hours_comparison.groupby(['Year', 'Quarter', 'YearQuarter']).agg({
    'y_true': 'sum',
    'y_true_real': 'sum',
    'Hours_Actual': 'sum',
    'Implied_Productivity_Nominal': 'mean',
    'Implied_Productivity_Real': 'mean',
}).reset_index()

print(f"✓ Aggregated to {len(quarterly)} quarters")
print()

print("Quarterly Implied Productivity:")
print(quarterly[['YearQuarter', 'Implied_Productivity_Real']].to_string(index=False))
print()

# ============================================================================
# Normalize to Index (Base = 100)
# ============================================================================

print("Normalizing to index (first quarter = 100) for comparison...")

# Our baseline: first quarter
baseline_productivity = quarterly['Implied_Productivity_Real'].iloc[0]

quarterly['Productivity_Index'] = (
    quarterly['Implied_Productivity_Real'] / baseline_productivity * 100
)

print("Store Productivity Index:")
print(quarterly[['YearQuarter', 'Productivity_Index']].to_string(index=False))
print()

# ============================================================================
# Compare with BLS
# ============================================================================

print("=" * 80)
print("Comparison with BLS Industry Benchmark")
print("=" * 80)
print()

# Merge BLS data (annual) with our quarterly data
quarterly = quarterly.merge(
    bls_study[['Year', 'Value']].rename(columns={'Value': 'BLS_Index'}),
    on='Year',
    how='left'
)

# Normalize BLS to same baseline
bls_baseline_year = quarterly['Year'].min()
bls_baseline_value = bls_study[bls_study['Year'] == bls_baseline_year]['Value'].values[0]
quarterly['BLS_Index_Normalized'] = quarterly['BLS_Index'] / bls_baseline_value * 100

print("Side-by-Side Comparison:")
comparison_table = quarterly[[
    'YearQuarter', 'Productivity_Index', 'BLS_Index_Normalized'
]].copy()
comparison_table['Deviation'] = (
    comparison_table['Productivity_Index'] - comparison_table['BLS_Index_Normalized']
)
comparison_table['Deviation_Pct'] = (
    (comparison_table['Productivity_Index'] / comparison_table['BLS_Index_Normalized'] - 1) * 100
)

print(comparison_table.to_string(index=False))
print()

# ============================================================================
# Flag Deviations
# ============================================================================

print("=" * 80)
print("Flagging Significant Deviations")
print("=" * 80)
print()

# Define threshold: ±10% deviation
deviation_threshold = 10.0

flags = comparison_table[
    abs(comparison_table['Deviation_Pct']) > deviation_threshold
].copy()

if len(flags) > 0:
    print(f"Periods with >±{deviation_threshold}% deviation from BLS:")
    print(flags[['YearQuarter', 'Productivity_Index', 'BLS_Index_Normalized', 'Deviation_Pct']].to_string(index=False))
    print()
    print("Interpretation:")
    print("  • Positive deviation: Implied productivity higher than industry (optimistic)")
    print("  • Negative deviation: Implied productivity lower than industry (conservative)")
else:
    print(f"✓ No quarters with deviation >±{deviation_threshold}%")
    print()

# ============================================================================
# Caveats and Limitations
# ============================================================================

print("=" * 80)
print("Caveats and Limitations")
print("=" * 80)
print()

print("Important Notes:")
print("  1. BLS productivity is real output per hour (deflated by industry price index)")
print("  2. Our implied productivity is sales per hour (deflated by CPI)")
print("  3. Sales ≠ Real Output:")
print("     - Sales include markups and don't reflect value-added")
print("     - Different product mixes affect sales/output relationship")
print("  4. SPLH/IPLH are operational metrics, not economic productivity measures")
print("  5. BLS data is industry aggregate; individual stores vary widely")
print("  6. Store hours include all tasks; BLS may have different scope")
print()

print("Labor Productivity vs Output Per Worker:")
print("  • Labor Productivity = Output / Hours Worked")
print("  • Output Per Worker = Output / Number of Employees")
print("  • These can diverge when:")
print("    - Part-time vs full-time mix changes")
print("    - Average hours per worker changes")
print("    - Overtime increases/decreases")
print("  • BLS tracks both separately; we focus on output per hour")
print()

# ============================================================================
# Save Results
# ============================================================================

print("=" * 80)
print("Saving Results")
print("=" * 80)
print()

# Save comparison table
comparison_table.to_csv(config.OUTPUT_DIR / "productivity_comparison.csv", index=False)
print(f"✓ Saved: productivity_comparison.csv")

# Save store-level productivity
store_productivity = hours_comparison[[
    'Store', 'Date', 'Year', 'YearQuarter',
    'y_true', 'y_true_real', 'Hours_Actual',
    'Implied_Productivity_Nominal', 'Implied_Productivity_Real', 'CPI'
]].copy()
store_productivity.to_csv(config.OUTPUT_DIR / "store_productivity.csv", index=False)
print(f"✓ Saved: store_productivity.csv")

# Save quarterly aggregates
quarterly.to_csv(config.OUTPUT_DIR / "quarterly_productivity.csv", index=False)
print(f"✓ Saved: quarterly_productivity.csv")

print()

# ============================================================================
# Visualizations
# ============================================================================

if config.SAVE_PLOTS:
    print("=" * 80)
    print("Generating Visualizations")
    print("=" * 80)
    print()

    # 1. Productivity Index Comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(quarterly))
    width = 0.35

    ax.bar([i - width/2 for i in x], quarterly['Productivity_Index'],
           width, label='Store Productivity (Implied)', alpha=0.8)
    ax.bar([i + width/2 for i in x], quarterly['BLS_Index_Normalized'],
           width, label='BLS Industry Benchmark', alpha=0.8)

    ax.set_xlabel('Quarter')
    ax.set_ylabel('Productivity Index (Base = 100)')
    ax.set_title('Store Productivity vs BLS Industry Benchmark')
    ax.set_xticks(x)
    ax.set_xticklabels(quarterly['YearQuarter'], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'productivity_comparison.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: productivity_comparison.png")

    # 2. Productivity Time Series
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(quarterly['YearQuarter'], quarterly['Productivity_Index'],
            'o-', lw=2, label='Store Productivity', markersize=8)
    ax.plot(quarterly['YearQuarter'], quarterly['BLS_Index_Normalized'],
            's-', lw=2, label='BLS Benchmark', markersize=8)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Baseline (Q1)')
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Productivity Index')
    ax.set_title('Productivity Trends: Store vs Industry')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'productivity_trends.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: productivity_trends.png")

    # 3. Deviation from BLS
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['red' if abs(x) > deviation_threshold else 'gray'
              for x in comparison_table['Deviation_Pct']]
    ax.bar(comparison_table['YearQuarter'], comparison_table['Deviation_Pct'],
           color=colors, alpha=0.7)
    ax.axhline(y=deviation_threshold, color='red', linestyle='--',
               alpha=0.5, label=f'±{deviation_threshold}% threshold')
    ax.axhline(y=-deviation_threshold, color='red', linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='black', linestyle='-', lw=1)
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Deviation from BLS (%)')
    ax.set_title('Store Productivity Deviation from Industry Benchmark')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'productivity_deviation.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: productivity_deviation.png")

    # 4. Store-level productivity distribution over time
    fig, ax = plt.subplots(figsize=(12, 6))
    store_productivity_pivot = store_productivity.pivot_table(
        index='Date',
        values='Implied_Productivity_Real',
        aggfunc=['mean', 'std']
    )
    store_productivity_pivot.columns = ['Mean', 'Std']
    store_productivity_pivot = store_productivity_pivot.sort_index()

    ax.plot(store_productivity_pivot.index, store_productivity_pivot['Mean'],
            'o-', lw=2, label='Mean Productivity')
    ax.fill_between(
        store_productivity_pivot.index,
        store_productivity_pivot['Mean'] - store_productivity_pivot['Std'],
        store_productivity_pivot['Mean'] + store_productivity_pivot['Std'],
        alpha=0.3, label='±1 Std Dev'
    )
    ax.set_xlabel('Date')
    ax.set_ylabel('Real Productivity ($/hour)')
    ax.set_title('Store-Level Productivity Distribution Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'store_productivity_distribution.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: store_productivity_distribution.png")

    print()

# ============================================================================
# Statistical Tests
# ============================================================================

print("=" * 80)
print("Statistical Tests")
print("=" * 80)
print()

# Correlation between store and BLS productivity trends
if len(quarterly) > 2:
    corr, p_value = stats.pearsonr(
        quarterly['Productivity_Index'],
        quarterly['BLS_Index_Normalized']
    )
    print(f"Correlation between store and BLS productivity:")
    print(f"  Pearson r: {corr:.3f}")
    print(f"  P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("  → Significant correlation (p < 0.05)")
    else:
        print("  → No significant correlation (p ≥ 0.05)")
    print()

# Mean deviation test
mean_deviation = comparison_table['Deviation_Pct'].mean()
print(f"Mean deviation from BLS: {mean_deviation:+.2f}%")
if abs(mean_deviation) > 5:
    print("  → Store productivity systematically differs from industry")
else:
    print("  → Store productivity aligns well with industry average")
print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Quarters analyzed: {len(quarterly)}")
print(f"Mean store productivity index: {quarterly['Productivity_Index'].mean():.2f}")
print(f"Mean BLS productivity index: {quarterly['BLS_Index_Normalized'].mean():.2f}")
print(f"Mean deviation: {mean_deviation:+.2f}%")
print(f"Periods flagged (>±{deviation_threshold}%): {len(flags)}")
print()
print("Key Takeaway:")
print("  Labor productivity (output/hour) is distinct from output/worker.")
print("  Our SPLH-based hours imply productivity levels that should be")
print("  calibrated against industry benchmarks to ensure realistic plans.")
print()
print("✓ Productivity calibration complete!")
print("=" * 80)
