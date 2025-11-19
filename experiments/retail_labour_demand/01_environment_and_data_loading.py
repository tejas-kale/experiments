"""
Section 1-2: Environment Setup and Data Loading

This script sets up the environment, loads the Favorita dataset and BLS labor 
productivity data, and performs initial exploratory data analysis (EDA).
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import configuration
import config

# ============================================================================
# SECTION 1: ENVIRONMENT SETUP
# ============================================================================

print("=" * 80)
print("SECTION 1: ENVIRONMENT SETUP")
print("=" * 80)

# Set random seeds for reproducibility
np.random.seed(config.RANDOM_STATE)

# Set plotting style
try:
    plt.style.use(config.PLOT_STYLE)
except:
    plt.style.use('seaborn-v0_8')
    
sns.set_palette("husl")

# Configure warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

print(f"✓ Random seed set to: {config.RANDOM_STATE}")
print(f"✓ Plotting style configured")
print(f"✓ Warnings filtered")
print()

# ============================================================================
# SECTION 2: DATA LOADING AND EDA
# ============================================================================

print("=" * 80)
print("SECTION 2: DATA LOADING AND EDA")
print("=" * 80)

# ----------------------------------------------------------------------------
# Load Favorita dataset
# ----------------------------------------------------------------------------

print("\n--- Loading Favorita Dataset ---")

# Load sales data
print(f"Loading sales data from: {config.SALES_PATH}")
sales_df = pd.read_csv(config.SALES_PATH)
# Parse dates - handle DD/MM/YYYY format
sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='%d/%m/%Y', errors='coerce')
# Check for any parsing failures
if sales_df['Date'].isna().any():
    print(f"Warning: {sales_df['Date'].isna().sum()} dates could not be parsed")
sales_df = sales_df.dropna(subset=['Date'])
print(f"  Shape: {sales_df.shape}")
print(f"  Columns: {list(sales_df.columns)}")
print(f"  Date range: {sales_df['Date'].min()} to {sales_df['Date'].max()}")

# Load stores data
print(f"\nLoading stores data from: {config.STORES_PATH}")
stores_df = pd.read_csv(config.STORES_PATH)
print(f"  Shape: {stores_df.shape}")
print(f"  Columns: {list(stores_df.columns)}")
print(f"  Number of stores: {stores_df['Store'].nunique()}")
print(f"  Store types: {stores_df['Type'].unique()}")

# Load features data
print(f"\nLoading features data from: {config.FEATURES_PATH}")
features_df = pd.read_csv(config.FEATURES_PATH)
# Parse dates
features_df['Date'] = pd.to_datetime(features_df['Date'], format='%d/%m/%Y', errors='coerce')
features_df = features_df.dropna(subset=['Date'])
print(f"  Shape: {features_df.shape}")
print(f"  Columns: {list(features_df.columns)}")
print(f"  Date range: {features_df['Date'].min()} to {features_df['Date'].max()}")

# ----------------------------------------------------------------------------
# Quick EDA on Favorita data
# ----------------------------------------------------------------------------

print("\n--- Exploratory Data Analysis: Sales Data ---")

# Missingness check
print("\nMissingness in sales data:")
missing_pct = (sales_df.isna().sum() / len(sales_df) * 100).round(2)
print(missing_pct[missing_pct > 0])

# Unique counts
print("\nUnique values:")
print(f"  Unique stores: {sales_df['Store'].nunique()}")
print(f"  Unique departments: {sales_df['Dept'].nunique()}")
print(f"  Unique dates: {sales_df['Date'].nunique()}")

# Sales statistics
print("\nWeekly sales statistics:")
print(sales_df['Weekly_Sales'].describe())

# Check for negative sales (returns/adjustments)
negative_sales = sales_df[sales_df['Weekly_Sales'] < 0]
if len(negative_sales) > 0:
    print(f"\n  Warning: {len(negative_sales)} records with negative sales found")
    print(f"  These may represent returns or adjustments")

# Holiday distribution
print("\nHoliday distribution:")
print(sales_df['IsHoliday'].value_counts())

print("\n--- Exploratory Data Analysis: Features Data ---")

# Missingness in features
print("\nMissingness in features data:")
missing_pct = (features_df.isna().sum() / len(features_df) * 100).round(2)
print(missing_pct[missing_pct > 0])

# Temperature, Fuel Price, CPI, Unemployment stats
print("\nNumerical feature statistics:")
numeric_cols = ['Temperature', 'Fuel_Price', 'CPI', 'Unemployment']
for col in numeric_cols:
    if col in features_df.columns:
        print(f"\n{col}:")
        print(f"  Mean: {features_df[col].mean():.2f}")
        print(f"  Min: {features_df[col].min():.2f}")
        print(f"  Max: {features_df[col].max():.2f}")

# Markdown availability
markdown_cols = [col for col in features_df.columns if 'MarkDown' in col]
print(f"\nMarkdown columns: {markdown_cols}")
for col in markdown_cols:
    non_null_pct = (features_df[col].notna().sum() / len(features_df) * 100)
    print(f"  {col}: {non_null_pct:.1f}% non-null")

# ----------------------------------------------------------------------------
# Load BLS Labor Productivity Data
# ----------------------------------------------------------------------------

print("\n--- Loading BLS Labor Productivity Data ---")

print(f"Loading BLS data from: {config.BLS_LABOR_PRODUCTIVITY_PATH}")
bls_df = pd.read_csv(config.BLS_LABOR_PRODUCTIVITY_PATH)
print(f"  Shape: {bls_df.shape}")
print(f"  Columns: {list(bls_df.columns)}")

# Display first few rows
print("\nFirst few rows of BLS data:")
print(bls_df.head())

# Check data properties
if 'Industry' in bls_df.columns:
    print(f"\nIndustry: {bls_df['Industry'].unique()}")
if 'Measure' in bls_df.columns:
    print(f"Measure: {bls_df['Measure'].unique()}")
if 'Units' in bls_df.columns:
    print(f"Units: {bls_df['Units'].unique()}")
if 'Year' in bls_df.columns:
    print(f"Year range: {bls_df['Year'].min()} to {bls_df['Year'].max()}")

# Display recent productivity values
if 'Year' in bls_df.columns and 'Value' in bls_df.columns:
    print("\nRecent labor productivity values:")
    recent = bls_df.nlargest(10, 'Year')[['Year', 'Value']]
    print(recent)

# ----------------------------------------------------------------------------
# Basic Seasonal Patterns
# ----------------------------------------------------------------------------

print("\n--- Basic Seasonal Patterns ---")

# Aggregate sales by date to see overall trend
daily_sales = sales_df.groupby('Date')['Weekly_Sales'].sum().reset_index()
daily_sales = daily_sales.sort_values('Date')

# Add temporal features for seasonality check
daily_sales['Year'] = daily_sales['Date'].dt.year
daily_sales['Month'] = daily_sales['Date'].dt.month
daily_sales['DayOfWeek'] = daily_sales['Date'].dt.dayofweek

# Monthly aggregation
monthly_sales = daily_sales.groupby(['Year', 'Month'])['Weekly_Sales'].sum().reset_index()
print("\nMonthly sales aggregation (first 12 months):")
print(monthly_sales.head(12))

# Day of week pattern
dow_sales = daily_sales.groupby('DayOfWeek')['Weekly_Sales'].mean().reset_index()
dow_sales['DayName'] = dow_sales['DayOfWeek'].map({
    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
    4: 'Friday', 5: 'Saturday', 6: 'Sunday'
})
print("\nAverage sales by day of week:")
print(dow_sales[['DayName', 'Weekly_Sales']])

# ----------------------------------------------------------------------------
# Save processed datasets for next step
# ----------------------------------------------------------------------------

print("\n--- Saving Processed Data ---")

# Create a data directory for intermediate outputs if needed
intermediate_dir = config.OUTPUT_DIR / "intermediate"
intermediate_dir.mkdir(exist_ok=True)

# Save cleaned datasets
sales_clean_path = intermediate_dir / "sales_clean.csv"
stores_clean_path = intermediate_dir / "stores_clean.csv"
features_clean_path = intermediate_dir / "features_clean.csv"
bls_clean_path = intermediate_dir / "bls_clean.csv"

sales_df.to_csv(sales_clean_path, index=False)
stores_df.to_csv(stores_clean_path, index=False)
features_df.to_csv(features_clean_path, index=False)
bls_df.to_csv(bls_clean_path, index=False)

print(f"✓ Saved cleaned sales data to: {sales_clean_path}")
print(f"✓ Saved cleaned stores data to: {stores_clean_path}")
print(f"✓ Saved cleaned features data to: {features_clean_path}")
print(f"✓ Saved cleaned BLS data to: {bls_clean_path}")

print("\n" + "=" * 80)
print("DATA LOADING COMPLETE")
print("=" * 80)
