"""
Section 3: Feature Engineering

This script:
1. Aggregates sales data to daily store-level targets
2. Creates calendar features (day of week, month, etc.)
3. Adds holiday flags and promotional features
4. Creates lag features and rolling averages (preventing leakage)
5. Joins with store metadata and external features
6. Saves the final feature matrix for modeling
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import joblib
from datetime import timedelta

# Import configuration
import config

print("=" * 80)
print("Section 3: Feature Engineering")
print("=" * 80)
print()

# ============================================================================
# Load Cleaned Data
# ============================================================================

print("Loading cleaned data...")
sales_df = joblib.load(config.OUTPUT_DIR / "sales_clean.pkl")
stores_df = joblib.load(config.OUTPUT_DIR / "stores_clean.pkl")
features_df = joblib.load(config.OUTPUT_DIR / "features_clean.pkl")
print("✓ Data loaded")
print()

# ============================================================================
# Aggregate to Store-Level Daily Targets
# ============================================================================

print("=" * 80)
print("Aggregating to Store-Level Targets")
print("=" * 80)
print()

# Note: The data is already at weekly granularity
# We'll treat each week as a "day" in our forecasting context
# In the labor conversion step, we'll distribute weekly sales to daily hours

# Aggregate across all departments to get store-level weekly sales
print("Aggregating sales across departments to store level...")
store_sales = sales_df.groupby(['Store', 'Date']).agg({
    'Weekly_Sales': 'sum',  # Total sales for the store
    'IsHoliday': 'first',   # Holiday flag (same for all depts in a store-week)
}).reset_index()

# Also keep department-level data for optional hierarchical analysis
dept_sales = sales_df.copy()

print(f"✓ Store-level aggregation complete")
print(f"  Original records: {len(sales_df):,}")
print(f"  Store-level records: {len(store_sales):,}")
print(f"  Stores: {store_sales['Store'].nunique()}")
print(f"  Weeks: {store_sales['Date'].nunique()}")
print()

# ============================================================================
# Merge with Store Metadata
# ============================================================================

print("Merging with store metadata...")
store_sales = store_sales.merge(stores_df, on='Store', how='left')
print(f"✓ Store metadata merged")
print()

# ============================================================================
# Calendar Features
# ============================================================================

print("=" * 80)
print("Creating Calendar Features")
print("=" * 80)
print()

print("Extracting date components...")
store_sales['Year'] = store_sales['Date'].dt.year
store_sales['Month'] = store_sales['Date'].dt.month
store_sales['Week'] = store_sales['Date'].dt.isocalendar().week
store_sales['DayOfWeek'] = store_sales['Date'].dt.dayofweek  # 0=Monday, 6=Sunday
store_sales['Quarter'] = store_sales['Date'].dt.quarter
store_sales['WeekOfMonth'] = (store_sales['Date'].dt.day - 1) // 7 + 1

# Create cyclical features for month and week
# This helps the model learn seasonal patterns
store_sales['Month_Sin'] = np.sin(2 * np.pi * store_sales['Month'] / 12)
store_sales['Month_Cos'] = np.cos(2 * np.pi * store_sales['Month'] / 12)
store_sales['Week_Sin'] = np.sin(2 * np.pi * store_sales['Week'] / 52)
store_sales['Week_Cos'] = np.cos(2 * np.pi * store_sales['Week'] / 52)

print(f"✓ Calendar features created")
print()

# ============================================================================
# Merge with External Features
# ============================================================================

print("=" * 80)
print("Merging with External Features")
print("=" * 80)
print()

print("Merging temperature, fuel price, CPI, unemployment, and markdowns...")
store_sales = store_sales.merge(
    features_df,
    on=['Store', 'Date'],
    how='left',
    suffixes=('', '_feat')
)

# Use IsHoliday from sales (more reliable)
if 'IsHoliday_feat' in store_sales.columns:
    store_sales.drop('IsHoliday_feat', axis=1, inplace=True)

print(f"✓ External features merged")
print()

# ============================================================================
# Promotional Features
# ============================================================================

print("=" * 80)
print("Creating Promotional Features")
print("=" * 80)
print()

# Markdown intensity: sum of all markdowns
markdown_cols = [f'MarkDown{i}' for i in range(1, 6)]
existing_markdown_cols = [col for col in markdown_cols if col in store_sales.columns]

if existing_markdown_cols:
    print(f"Creating markdown intensity from: {existing_markdown_cols}")
    # Fill NaN with 0 for markdown columns
    store_sales[existing_markdown_cols] = store_sales[existing_markdown_cols].fillna(0)
    store_sales['MarkDown_Total'] = store_sales[existing_markdown_cols].sum(axis=1)

    # Binary flag: any markdown active
    store_sales['Has_MarkDown'] = (store_sales['MarkDown_Total'] > 0).astype(int)

    print(f"✓ Markdown features created")
    print(f"  Weeks with markdowns: {store_sales['Has_MarkDown'].sum():,} ({store_sales['Has_MarkDown'].mean()*100:.1f}%)")
else:
    print("! No markdown columns found")
    store_sales['MarkDown_Total'] = 0
    store_sales['Has_MarkDown'] = 0

print()

# ============================================================================
# Lag Features (Preventing Leakage)
# ============================================================================

print("=" * 80)
print("Creating Lag Features")
print("=" * 80)
print()

# Sort by store and date to ensure proper time order
store_sales = store_sales.sort_values(['Store', 'Date']).reset_index(drop=True)

# Create lag features for each store
print(f"Creating lags for periods: {config.LAG_PERIODS}")

for lag in config.LAG_PERIODS:
    print(f"  Lag {lag} weeks...")
    store_sales[f'Sales_Lag_{lag}'] = store_sales.groupby('Store')['Weekly_Sales'].shift(lag)

print(f"✓ Lag features created")
print()

# ============================================================================
# Rolling Features (Preventing Leakage)
# ============================================================================

print("=" * 80)
print("Creating Rolling Features")
print("=" * 80)
print()

print(f"Creating rolling averages for windows: {config.ROLLING_WINDOWS}")

for window in config.ROLLING_WINDOWS:
    print(f"  Rolling {window}-week mean...")
    # Use shift(1) to prevent leakage: we only use past data
    store_sales[f'Sales_RollingMean_{window}'] = (
        store_sales.groupby('Store')['Weekly_Sales']
        .shift(1)  # Shift by 1 to exclude current week
        .rolling(window=window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    print(f"  Rolling {window}-week std...")
    store_sales[f'Sales_RollingStd_{window}'] = (
        store_sales.groupby('Store')['Weekly_Sales']
        .shift(1)
        .rolling(window=window, min_periods=1)
        .std()
        .reset_index(level=0, drop=True)
    )

print(f"✓ Rolling features created")
print()

# ============================================================================
# Trend Features
# ============================================================================

print("=" * 80)
print("Creating Trend Features")
print("=" * 80)
print()

# Days since start (numeric time trend)
min_date = store_sales['Date'].min()
store_sales['Days_Since_Start'] = (store_sales['Date'] - min_date).dt.days

# Week number (continuous)
store_sales['Week_Number'] = store_sales.groupby('Store').cumcount()

print(f"✓ Trend features created")
print()

# ============================================================================
# Store Size per Capita (Relative Size)
# ============================================================================

print("Creating store size features...")

# Normalize store size (helps with generalization)
store_sales['Size_Normalized'] = (
    (store_sales['Size'] - store_sales['Size'].mean()) /
    store_sales['Size'].std()
)

# Size bin (small, medium, large)
store_sales['Size_Bin'] = pd.qcut(
    store_sales['Size'],
    q=3,
    labels=['Small', 'Medium', 'Large']
)

print(f"✓ Store size features created")
print()

# ============================================================================
# Holiday Interaction Features
# ============================================================================

print("Creating holiday interaction features...")

# Holiday + Month (holiday timing matters)
store_sales['Holiday_Month'] = (
    store_sales['IsHoliday'].astype(int) * store_sales['Month']
)

# Pre-holiday weeks (week before holiday)
store_sales['Is_PreHoliday'] = False
for store in store_sales['Store'].unique():
    store_mask = store_sales['Store'] == store
    store_dates = store_sales[store_mask].sort_values('Date')

    # Find holiday dates
    holiday_dates = store_dates[store_dates['IsHoliday']]['Date'].values

    for holiday_date in holiday_dates:
        # Mark the week before (7 days)
        pre_holiday_date = pd.Timestamp(holiday_date) - timedelta(days=7)
        pre_holiday_mask = (
            (store_sales['Store'] == store) &
            (store_sales['Date'] == pre_holiday_date)
        )
        store_sales.loc[pre_holiday_mask, 'Is_PreHoliday'] = True

store_sales['Is_PreHoliday'] = store_sales['Is_PreHoliday'].astype(int)

print(f"✓ Holiday interaction features created")
print(f"  Pre-holiday weeks: {store_sales['Is_PreHoliday'].sum()}")
print()

# ============================================================================
# Data Quality: Handle Missing Values
# ============================================================================

print("=" * 80)
print("Handling Missing Values")
print("=" * 80)
print()

# Check missing values
missing_summary = store_sales.isnull().sum()
missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)

if len(missing_summary) > 0:
    print("Missing values by column:")
    print(missing_summary)
    print()

    # Lag and rolling features will have NaN for early periods
    # Fill with 0 or median
    lag_rolling_cols = [col for col in store_sales.columns
                       if 'Lag_' in col or 'Rolling' in col]

    print(f"Filling {len(lag_rolling_cols)} lag/rolling features with forward fill then 0...")
    for col in lag_rolling_cols:
        store_sales[col] = store_sales.groupby('Store')[col].fillna(method='ffill').fillna(0)

    # Temperature, fuel price: fill with median
    for col in ['Temperature', 'Fuel_Price', 'CPI', 'Unemployment']:
        if col in store_sales.columns and store_sales[col].isnull().any():
            median_val = store_sales[col].median()
            store_sales[col].fillna(median_val, inplace=True)
            print(f"  {col}: filled with median {median_val:.2f}")

    print()
else:
    print("✓ No missing values")
    print()

# ============================================================================
# Create Target Variable
# ============================================================================

print("=" * 80)
print("Creating Target Variable")
print("=" * 80)
print()

# Our target is Weekly_Sales (continuous variable)
# For time series forecasting, we'll predict the next week's sales

store_sales['Target'] = store_sales['Weekly_Sales']

print(f"✓ Target variable: Weekly_Sales")
print(f"  Mean: ${store_sales['Target'].mean():,.2f}")
print(f"  Std: ${store_sales['Target'].std():,.2f}")
print(f"  Min: ${store_sales['Target'].min():,.2f}")
print(f"  Max: ${store_sales['Target'].max():,.2f}")
print()

# ============================================================================
# Feature Selection and Final Dataset
# ============================================================================

print("=" * 80)
print("Feature Selection")
print("=" * 80)
print()

# Define feature groups
calendar_features = [
    'Year', 'Month', 'Week', 'DayOfWeek', 'Quarter', 'WeekOfMonth',
    'Month_Sin', 'Month_Cos', 'Week_Sin', 'Week_Cos'
]

external_features = [
    'Temperature', 'Fuel_Price', 'CPI', 'Unemployment'
]

promotional_features = existing_markdown_cols + [
    'MarkDown_Total', 'Has_MarkDown'
]

lag_features = [f'Sales_Lag_{lag}' for lag in config.LAG_PERIODS]

rolling_features = []
for window in config.ROLLING_WINDOWS:
    rolling_features.extend([
        f'Sales_RollingMean_{window}',
        f'Sales_RollingStd_{window}'
    ])

store_features = [
    'Type', 'Size', 'Size_Normalized'
]

holiday_features = [
    'IsHoliday', 'Is_PreHoliday', 'Holiday_Month'
]

trend_features = [
    'Days_Since_Start', 'Week_Number'
]

# All features for modeling (excluding identifiers and target)
feature_columns = (
    ['Store', 'Date'] +  # Identifiers (not used in model but kept for tracking)
    calendar_features +
    external_features +
    promotional_features +
    lag_features +
    rolling_features +
    store_features +
    holiday_features +
    trend_features +
    ['Target']  # Target variable
)

# Filter to existing columns
feature_columns = [col for col in feature_columns if col in store_sales.columns]

features_final = store_sales[feature_columns].copy()

print(f"Final feature count: {len(feature_columns) - 3}")  # Minus Store, Date, Target
print(f"  Calendar: {len(calendar_features)}")
print(f"  External: {len(external_features)}")
print(f"  Promotional: {len(promotional_features)}")
print(f"  Lag: {len(lag_features)}")
print(f"  Rolling: {len(rolling_features)}")
print(f"  Store: {len(store_features)}")
print(f"  Holiday: {len(holiday_features)}")
print(f"  Trend: {len(trend_features)}")
print()

# ============================================================================
# Save Feature Matrix
# ============================================================================

print("=" * 80)
print("Saving Feature Matrix")
print("=" * 80)
print()

# Save as CSV
features_final.to_csv(config.FEATURES_TRAIN_CSV, index=False)
print(f"✓ Saved: {config.FEATURES_TRAIN_CSV}")

# Also save as pickle for faster loading
features_pkl_path = config.OUTPUT_DIR / "features_train.pkl"
joblib.dump(features_final, features_pkl_path)
print(f"✓ Saved: {features_pkl_path}")

# Save feature column names for reference
feature_names = [col for col in feature_columns if col not in ['Store', 'Date', 'Target']]
feature_info = {
    'all_features': feature_names,
    'calendar_features': calendar_features,
    'external_features': external_features,
    'promotional_features': promotional_features,
    'lag_features': lag_features,
    'rolling_features': rolling_features,
    'store_features': store_features,
    'holiday_features': holiday_features,
    'trend_features': trend_features,
}
joblib.dump(feature_info, config.OUTPUT_DIR / "feature_info.pkl")
print(f"✓ Saved: feature_info.pkl")
print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total records: {len(features_final):,}")
print(f"Stores: {features_final['Store'].nunique()}")
print(f"Date range: {features_final['Date'].min().date()} to {features_final['Date'].max().date()}")
print(f"Features: {len(feature_names)}")
print(f"Target: Weekly_Sales (mean: ${features_final['Target'].mean():,.2f})")
print()
print("✓ Feature engineering complete!")
print("=" * 80)
