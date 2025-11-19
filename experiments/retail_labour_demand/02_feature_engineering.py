"""
Section 3: Feature Engineering

This script aggregates sales data to daily store-level targets, creates calendar
features, holiday flags, promotion intensity metrics, and safe lagged/rolling features.
"""

import numpy as np
import pandas as pd
import warnings
from pathlib import Path

# Import configuration
import config

warnings.filterwarnings('ignore')

print("=" * 80)
print("SECTION 3: FEATURE ENGINEERING")
print("=" * 80)

# ============================================================================
# LOAD CLEANED DATA
# ============================================================================

print("\n--- Loading Cleaned Data ---")

intermediate_dir = config.OUTPUT_DIR / "intermediate"
sales_df = pd.read_csv(intermediate_dir / "sales_clean.csv", parse_dates=['Date'])
stores_df = pd.read_csv(intermediate_dir / "stores_clean.csv")
features_df = pd.read_csv(intermediate_dir / "features_clean.csv", parse_dates=['Date'])

print(f"✓ Loaded sales data: {sales_df.shape}")
print(f"✓ Loaded stores data: {stores_df.shape}")
print(f"✓ Loaded features data: {features_df.shape}")

# ============================================================================
# AGGREGATE TO DAILY STORE-LEVEL TARGETS
# ============================================================================

print("\n--- Aggregating to Daily Store-Level ---")

# The data is weekly, but we'll treat each week's date as a data point
# Aggregate by Store and Date to get total sales and units
# Note: Weekly_Sales appears to be in dollars, we'll use count of transactions as proxy for units

# First, let's aggregate by store and date
# We need to infer units - since we have weekly sales in dollars, 
# we can use number of departments as a proxy for activity level
# Or better: count the number of department records as units sold

store_daily = sales_df.groupby(['Store', 'Date']).agg({
    'Weekly_Sales': 'sum',  # Total sales across all departments
    'Dept': 'count',  # Number of department records (proxy for units/activity)
    'IsHoliday': 'max'  # Holiday flag
}).reset_index()

# Rename for clarity
store_daily = store_daily.rename(columns={
    'Weekly_Sales': 'total_sales',
    'Dept': 'total_units',  # Using dept count as units proxy
    'IsHoliday': 'is_holiday'
})

print(f"Store-daily aggregation shape: {store_daily.shape}")
print(f"Date range: {store_daily['Date'].min()} to {store_daily['Date'].max()}")
print(f"Number of stores: {store_daily['Store'].nunique()}")
print(f"Average sales per store-day: ${store_daily['total_sales'].mean():.2f}")
print(f"Average units per store-day: {store_daily['total_units'].mean():.2f}")

# Merge store metadata
store_daily = store_daily.merge(stores_df, on='Store', how='left')
print(f"✓ Merged store metadata")

# Merge features data
store_daily = store_daily.merge(
    features_df,
    on=['Store', 'Date'],
    how='left',
    suffixes=('', '_feat')
)
# Keep the is_holiday from sales data (more reliable)
if 'IsHoliday_feat' in store_daily.columns:
    store_daily = store_daily.drop('IsHoliday_feat', axis=1)

print(f"✓ Merged features data")
print(f"Final shape after merges: {store_daily.shape}")

# ============================================================================
# CREATE CALENDAR FEATURES
# ============================================================================

print("\n--- Creating Calendar Features ---")

store_daily['year'] = store_daily['Date'].dt.year
store_daily['month'] = store_daily['Date'].dt.month
store_daily['day'] = store_daily['Date'].dt.day
store_daily['dayofweek'] = store_daily['Date'].dt.dayofweek
store_daily['quarter'] = store_daily['Date'].dt.quarter
store_daily['weekofyear'] = store_daily['Date'].dt.isocalendar().week.astype(int)
store_daily['dayofyear'] = store_daily['Date'].dt.dayofyear

# Cyclic encoding for month and dayofweek
store_daily['month_sin'] = np.sin(2 * np.pi * store_daily['month'] / 12)
store_daily['month_cos'] = np.cos(2 * np.pi * store_daily['month'] / 12)
store_daily['dow_sin'] = np.sin(2 * np.pi * store_daily['dayofweek'] / 7)
store_daily['dow_cos'] = np.cos(2 * np.pi * store_daily['dayofweek'] / 7)

# Weekend flag
store_daily['is_weekend'] = (store_daily['dayofweek'] >= 5).astype(int)

print(f"✓ Created {7 + 4 + 1} calendar features")

# ============================================================================
# HOLIDAY FLAGS
# ============================================================================

print("\n--- Creating Holiday Flags ---")

# The is_holiday column from the dataset indicates special holiday weeks
# We already have this, just ensure it's properly encoded
store_daily['is_holiday'] = store_daily['is_holiday'].fillna(False).astype(int)

# Create pre/post holiday indicators
store_daily = store_daily.sort_values(['Store', 'Date'])

# For each store, create lead/lag holiday indicators
def add_holiday_windows(group):
    group = group.sort_values('Date').copy()
    group['is_pre_holiday'] = group['is_holiday'].shift(-1, fill_value=0)
    group['is_post_holiday'] = group['is_holiday'].shift(1, fill_value=0)
    return group

store_daily = store_daily.groupby('Store', group_keys=False).apply(add_holiday_windows)

print(f"✓ Created holiday flags")
print(f"  Holiday weeks: {store_daily['is_holiday'].sum()}")
print(f"  Pre-holiday weeks: {store_daily['is_pre_holiday'].sum()}")
print(f"  Post-holiday weeks: {store_daily['is_post_holiday'].sum()}")

# ============================================================================
# PROMOTION INTENSITY
# ============================================================================

print("\n--- Creating Promotion Intensity Features ---")

# Fill missing markdown values with 0
markdown_cols = [col for col in store_daily.columns if 'MarkDown' in col]
for col in markdown_cols:
    store_daily[col] = store_daily[col].fillna(0)

# Total promotion intensity (sum of all markdowns)
if markdown_cols:
    store_daily['total_markdown'] = store_daily[markdown_cols].sum(axis=1)
    # Promotion flag (any markdown > 0)
    store_daily['has_promotion'] = (store_daily['total_markdown'] > 0).astype(int)
    print(f"✓ Created promotion features from {len(markdown_cols)} markdown columns")
    print(f"  Weeks with promotions: {store_daily['has_promotion'].sum()}")
else:
    store_daily['total_markdown'] = 0
    store_daily['has_promotion'] = 0
    print("  No markdown columns found")

# ============================================================================
# LAGGED FEATURES (Safe - respecting time order)
# ============================================================================

print("\n--- Creating Lagged Features ---")

# Sort by store and date to ensure proper time ordering
store_daily = store_daily.sort_values(['Store', 'Date'])

# Create lagged features for each store separately
def add_lag_features(group):
    group = group.sort_values('Date').copy()
    
    for lag in config.LAG_DAYS:
        group[f'sales_lag_{lag}'] = group['total_sales'].shift(lag)
        group[f'units_lag_{lag}'] = group['total_units'].shift(lag)
    
    return group

store_daily = store_daily.groupby('Store', group_keys=False).apply(add_lag_features)

print(f"✓ Created lagged features for lags: {config.LAG_DAYS}")

# ============================================================================
# ROLLING MEANS (Safe - respecting time order)
# ============================================================================

print("\n--- Creating Rolling Mean Features ---")

def add_rolling_features(group):
    group = group.sort_values('Date').copy()
    
    for window in config.ROLLING_WINDOWS:
        # Use min_periods to handle edge cases
        group[f'sales_roll_mean_{window}'] = group['total_sales'].rolling(
            window=window, min_periods=1
        ).mean().shift(1)  # Shift to prevent leakage
        
        group[f'units_roll_mean_{window}'] = group['total_units'].rolling(
            window=window, min_periods=1
        ).mean().shift(1)  # Shift to prevent leakage
    
    return group

store_daily = store_daily.groupby('Store', group_keys=False).apply(add_rolling_features)

print(f"✓ Created rolling mean features for windows: {config.ROLLING_WINDOWS}")

# ============================================================================
# HANDLE MISSING VALUES IN FEATURES
# ============================================================================

print("\n--- Handling Missing Values ---")

# Fill missing values in numeric features
numeric_cols = ['Temperature', 'Fuel_Price', 'CPI', 'Unemployment']
for col in numeric_cols:
    if col in store_daily.columns:
        # Forward fill then backward fill
        store_daily[col] = store_daily.groupby('Store')[col].fillna(method='ffill').fillna(method='bfill')
        # If still missing, fill with overall mean
        if store_daily[col].isna().any():
            store_daily[col] = store_daily[col].fillna(store_daily[col].mean())

# For lagged and rolling features, keep NaN for now (will handle in modeling)
# These NaNs represent the beginning of the time series where we don't have enough history

print(f"✓ Handled missing values")

# Check remaining missingness
missing_summary = store_daily.isna().sum()
missing_summary = missing_summary[missing_summary > 0]
if len(missing_summary) > 0:
    print("\nRemaining missing values (mostly lag/rolling at series start):")
    print(missing_summary)
else:
    print("  No missing values remaining")

# ============================================================================
# SAVE FEATURE ENGINEERED DATASET
# ============================================================================

print("\n--- Saving Feature-Engineered Dataset ---")

# Save the full dataset
features_full_path = intermediate_dir / "features_full.csv"
store_daily.to_csv(features_full_path, index=False)

print(f"✓ Saved feature-engineered data to: {features_full_path}")
print(f"  Shape: {store_daily.shape}")
print(f"  Columns: {len(store_daily.columns)}")

# Display column summary
print("\nColumn categories:")
print(f"  Target variables: total_sales, total_units")
print(f"  Store metadata: Store, Type, Size")
print(f"  Calendar features: year, month, day, dayofweek, quarter, etc.")
print(f"  Holiday features: is_holiday, is_pre_holiday, is_post_holiday")
print(f"  Promotion features: total_markdown, has_promotion")
print(f"  Economic features: Temperature, Fuel_Price, CPI, Unemployment")
print(f"  Lag features: {len([c for c in store_daily.columns if 'lag' in c])} columns")
print(f"  Rolling features: {len([c for c in store_daily.columns if 'roll' in c])} columns")

# Display sample rows
print("\nSample of feature-engineered data:")
print(store_daily.head(3).T)

print("\n" + "=" * 80)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 80)
