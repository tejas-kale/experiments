"""
Section 1 & 2: Environment Setup and Data Loading with EDA

This script:
1. Sets up the Python environment with all necessary imports
2. Loads the historical retail sales data and BLS labor productivity data
3. Performs exploratory data analysis (EDA)
4. Validates data quality and checks for issues
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
import joblib

# Import configuration
import config

# ============================================================================
# Section 1: Environment Setup
# ============================================================================

print("=" * 80)
print("RETAIL LABOR DEMAND FORECASTING PIPELINE")
print("Section 1 & 2: Environment Setup and Data Loading")
print("=" * 80)
print()

# Set random seeds for reproducibility
np.random.seed(config.RANDOM_SEED)

# Configure plotting
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = config.FIGURE_SIZE
plt.rcParams['figure.dpi'] = config.FIGURE_DPI

# Filter warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

print(f"✓ Environment configured")
print(f"✓ Random seed: {config.RANDOM_SEED}")
print(f"✓ Plot style: {config.PLOT_STYLE}")
print()

# ============================================================================
# Section 2: Load Data
# ============================================================================

print("=" * 80)
print("Loading Data")
print("=" * 80)
print()

# ----------------------------------------------------------------------------
# Load Sales Data
# ----------------------------------------------------------------------------
print(f"Loading sales data from: {config.SALES_PATH}")
sales_df = pd.read_csv(config.SALES_PATH)

# Parse dates
sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='%d/%m/%Y')

# Enforce dtypes
sales_df['Store'] = sales_df['Store'].astype(int)
sales_df['Dept'] = sales_df['Dept'].astype(int)
sales_df['Weekly_Sales'] = sales_df['Weekly_Sales'].astype(float)
sales_df['IsHoliday'] = sales_df['IsHoliday'].astype(bool)

print(f"  Shape: {sales_df.shape}")
print(f"  Date range: {sales_df['Date'].min()} to {sales_df['Date'].max()}")
print(f"  Stores: {sales_df['Store'].nunique()}")
print(f"  Departments: {sales_df['Dept'].nunique()}")
print()

# ----------------------------------------------------------------------------
# Load Stores Data
# ----------------------------------------------------------------------------
print(f"Loading stores data from: {config.STORES_PATH}")
stores_df = pd.read_csv(config.STORES_PATH)

# Enforce dtypes
stores_df['Store'] = stores_df['Store'].astype(int)
stores_df['Type'] = stores_df['Type'].astype(str)
stores_df['Size'] = stores_df['Size'].astype(int)

print(f"  Shape: {stores_df.shape}")
print(f"  Store types: {stores_df['Type'].unique()}")
print(f"  Size range: {stores_df['Size'].min():,} to {stores_df['Size'].max():,} sq ft")
print()

# ----------------------------------------------------------------------------
# Load Features Data
# ----------------------------------------------------------------------------
print(f"Loading features data from: {config.FEATURES_PATH}")
features_df = pd.read_csv(config.FEATURES_PATH)

# Parse dates
features_df['Date'] = pd.to_datetime(features_df['Date'], format='%d/%m/%Y')

# Enforce dtypes
features_df['Store'] = features_df['Store'].astype(int)
features_df['Temperature'] = features_df['Temperature'].astype(float)
features_df['Fuel_Price'] = features_df['Fuel_Price'].astype(float)
features_df['CPI'] = features_df['CPI'].astype(float)
features_df['Unemployment'] = features_df['Unemployment'].astype(float)
features_df['IsHoliday'] = features_df['IsHoliday'].astype(bool)

# Markdown columns (may have missing values)
for i in range(1, 6):
    col = f'MarkDown{i}'
    if col in features_df.columns:
        features_df[col] = pd.to_numeric(features_df[col], errors='coerce')

print(f"  Shape: {features_df.shape}")
print(f"  Date range: {features_df['Date'].min()} to {features_df['Date'].max()}")
print()

# ----------------------------------------------------------------------------
# Load BLS Labor Productivity Data
# ----------------------------------------------------------------------------
print(f"Loading BLS labor productivity data from: {config.BLS_LABOR_PRODUCTIVITY_PATH}")
bls_df = pd.read_csv(config.BLS_LABOR_PRODUCTIVITY_PATH)

# Enforce dtypes
bls_df['Year'] = bls_df['Year'].astype(int)
# Clean Value column (remove % signs and whitespace if present)
bls_df['Value'] = bls_df['Value'].astype(str).str.strip().str.replace('%', '')
bls_df['Value'] = pd.to_numeric(bls_df['Value'], errors='coerce')

print(f"  Shape: {bls_df.shape}")
print(f"  Industry: {bls_df['Industry'].iloc[0]}")
print(f"  NAICS Digit: {bls_df['Digit'].iloc[0]}")
print(f"  Measure: {bls_df['Measure'].iloc[0]}")
print(f"  Units: {bls_df['Units'].iloc[0]}")
print(f"  Year range: {bls_df['Year'].min()} to {bls_df['Year'].max()}")
print()

# ============================================================================
# Exploratory Data Analysis
# ============================================================================

print("=" * 80)
print("Exploratory Data Analysis")
print("=" * 80)
print()

# ----------------------------------------------------------------------------
# Sales Data EDA
# ----------------------------------------------------------------------------
print("Sales Data Summary:")
print("-" * 80)
print(sales_df.describe())
print()

# Check for missing values
print("Missing Values:")
print(sales_df.isnull().sum())
print(f"Missing percentage: {sales_df.isnull().sum().sum() / sales_df.size * 100:.2f}%")
print()

# Check for negative sales (data quality issue)
negative_sales = sales_df[sales_df['Weekly_Sales'] < 0]
print(f"Negative sales records: {len(negative_sales)} ({len(negative_sales)/len(sales_df)*100:.2f}%)")
if len(negative_sales) > 0:
    print("  Note: Negative sales likely represent returns/refunds")
print()

# Holiday weeks
holiday_weeks = sales_df[sales_df['IsHoliday']].groupby('Date').size()
print(f"Holiday weeks: {len(holiday_weeks)}")
print(f"Holiday dates: {sorted(holiday_weeks.index.strftime('%Y-%m-%d').tolist())}")
print()

# ----------------------------------------------------------------------------
# Stores Data EDA
# ----------------------------------------------------------------------------
print("Stores Data Summary:")
print("-" * 80)
print(stores_df.groupby('Type').agg({
    'Store': 'count',
    'Size': ['mean', 'min', 'max']
}))
print()

# ----------------------------------------------------------------------------
# Features Data EDA
# ----------------------------------------------------------------------------
print("Features Data Summary:")
print("-" * 80)
print(features_df.describe())
print()

print("Missing Values in Features:")
missing_features = features_df.isnull().sum()
missing_pct = (missing_features / len(features_df) * 100).round(2)
missing_summary = pd.DataFrame({
    'Missing Count': missing_features,
    'Missing %': missing_pct
})
print(missing_summary[missing_summary['Missing Count'] > 0])
print()

# Markdown availability (only after Nov 2011)
markdown_start = features_df[features_df['MarkDown1'].notna()]['Date'].min()
print(f"MarkDown data available from: {markdown_start}")
print()

# ----------------------------------------------------------------------------
# BLS Data EDA
# ----------------------------------------------------------------------------
print("BLS Labor Productivity Summary:")
print("-" * 80)
print(bls_df[['Year', 'Value']].set_index('Year'))
print()

# Filter to our study period
study_years = bls_df[
    (bls_df['Year'] >= config.BLS_COMPARISON_START_YEAR) &
    (bls_df['Year'] <= config.BLS_COMPARISON_END_YEAR)
]
print(f"BLS Productivity during study period ({config.BLS_COMPARISON_START_YEAR}-{config.BLS_COMPARISON_END_YEAR}):")
print(study_years[['Year', 'Value']].to_string(index=False))
print()

# ============================================================================
# Seasonal Patterns
# ============================================================================

print("=" * 80)
print("Seasonal Patterns Analysis")
print("=" * 80)
print()

# Aggregate to weekly level across all stores
weekly_sales = sales_df.groupby('Date')['Weekly_Sales'].sum().reset_index()
weekly_sales['Year'] = weekly_sales['Date'].dt.year
weekly_sales['Month'] = weekly_sales['Date'].dt.month
weekly_sales['Week'] = weekly_sales['Date'].dt.isocalendar().week

# Monthly seasonality
monthly_avg = weekly_sales.groupby('Month')['Weekly_Sales'].mean()
print("Average Sales by Month:")
print(monthly_avg.to_string())
print()

# Year-over-year growth
yearly_sales = weekly_sales.groupby('Year')['Weekly_Sales'].sum()
print("Total Sales by Year:")
for year, sales in yearly_sales.items():
    print(f"  {year}: ${sales:,.0f}")
if len(yearly_sales) > 1:
    yoy_growth = yearly_sales.pct_change() * 100
    print("\nYear-over-Year Growth:")
    for year, growth in yoy_growth.items():
        if not pd.isna(growth):
            print(f"  {year}: {growth:+.2f}%")
print()

# ============================================================================
# Save Processed Data for Next Steps
# ============================================================================

print("=" * 80)
print("Saving Processed Data")
print("=" * 80)
print()

# Create a combined dataset (we'll need this for feature engineering)
# For now, just save the cleaned dataframes

# Save intermediate files
sales_clean_path = config.OUTPUT_DIR / "sales_clean.pkl"
stores_clean_path = config.OUTPUT_DIR / "stores_clean.pkl"
features_clean_path = config.OUTPUT_DIR / "features_clean.pkl"
bls_clean_path = config.OUTPUT_DIR / "bls_clean.pkl"

joblib.dump(sales_df, sales_clean_path)
joblib.dump(stores_df, stores_clean_path)
joblib.dump(features_df, features_clean_path)
joblib.dump(bls_df, bls_clean_path)

print(f"✓ Saved: {sales_clean_path.name}")
print(f"✓ Saved: {stores_clean_path.name}")
print(f"✓ Saved: {features_clean_path.name}")
print(f"✓ Saved: {bls_clean_path.name}")
print()

# ============================================================================
# Summary Statistics Export
# ============================================================================

# Create summary report
summary = {
    'Sales Records': len(sales_df),
    'Stores': sales_df['Store'].nunique(),
    'Departments': sales_df['Dept'].nunique(),
    'Date Range': f"{sales_df['Date'].min().date()} to {sales_df['Date'].max().date()}",
    'Weeks of Data': sales_df['Date'].nunique(),
    'Total Sales': f"${sales_df['Weekly_Sales'].sum():,.0f}",
    'Average Weekly Sales per Store-Dept': f"${sales_df['Weekly_Sales'].mean():,.2f}",
    'Holiday Weeks': len(holiday_weeks),
    'Negative Sales Records': len(negative_sales),
    'BLS Productivity Years': f"{bls_df['Year'].min()} to {bls_df['Year'].max()}",
}

print("=" * 80)
print("SUMMARY")
print("=" * 80)
for key, value in summary.items():
    print(f"{key:.<50} {value}")
print()

print("✓ Data loading and EDA complete!")
print("=" * 80)
