"""
Configuration file for retail labor demand forecasting pipeline.
All paths and planning parameters are centralized here for easy modification.
"""

import os
from pathlib import Path

# ============================================================================
# Directory Structure
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
MODELS_DIR = PROJECT_ROOT / "models"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
MODELS_DIR.mkdir(exist_ok=True, parents=True)

# ============================================================================
# Input Data Paths
# ============================================================================
# Historical sales data (Walmart/retail dataset)
SALES_PATH = DATA_DIR / "historical_sales_data" / "sales data-set.csv"
STORES_PATH = DATA_DIR / "historical_sales_data" / "stores data-set.csv"
FEATURES_PATH = DATA_DIR / "historical_sales_data" / "Features data set.csv"

# BLS labor productivity benchmark
BLS_LABOR_PRODUCTIVITY_PATH = DATA_DIR / "labour_productivity.csv"

# Note: This dataset does not have separate items, holidays, or transactions files
# The features dataset contains holiday flags and other promotional information

# ============================================================================
# Output Paths
# ============================================================================
FEATURES_TRAIN_CSV = OUTPUT_DIR / "features_train.csv"
FORECASTS_CSV = OUTPUT_DIR / "forecasts.csv"
HOURS_ACTUAL_CSV = OUTPUT_DIR / "hours_actual.csv"
HOURS_FORECAST_CSV = OUTPUT_DIR / "hours_forecast.csv"
HOURS_COMPARISON_CSV = OUTPUT_DIR / "hours_comparison.csv"
REPORT_PATH = OUTPUT_DIR / "README_report.md"

# Model artifacts
RF_MODEL_PATH = MODELS_DIR / "random_forest_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"

# ============================================================================
# Planning Parameters - Labor Conversion
# ============================================================================

# Conversion mode: "SPLH" (Sales Per Labor Hour) or "IPLH" (Items Per Labor Hour)
# Since this dataset has sales but not item counts, we'll use SPLH
CONVERSION_MODE = "SPLH"  # Options: "SPLH", "IPLH"

# SPLH/IPLH parameters by store type
# These are example values - in practice, calibrate based on operational data
# SPLH: dollars of sales per labor hour
# For grocery/retail, typical SPLH ranges from $100-$300 depending on format

PRODUCTIVITY_BY_STORE_TYPE = {
    "A": {  # Large format stores
        "SPLH": 200.0,  # $200 in sales per labor hour
        "IPLH": 50.0,   # 50 items per labor hour (if available)
    },
    "B": {  # Medium format stores
        "SPLH": 180.0,  # Slightly lower productivity
        "IPLH": 45.0,
    },
    "C": {  # Small format stores
        "SPLH": 150.0,  # Lower productivity in smaller stores
        "IPLH": 40.0,
    },
}

# Department-level adjustments (multiplicative factors)
# Some departments may have different productivity profiles
DEPARTMENT_PRODUCTIVITY_FACTORS = {
    # Example: department 1 might be grocery with higher throughput
    # department 95 might be pharmacy with lower throughput
    # Default is 1.0 (use store-level productivity)
}

# Baseline hours: fixed daily tasks independent of sales volume
# Examples: opening/closing procedures, cleaning, restocking, administration
# These are daily hours per store, regardless of sales
BASELINE_HOURS_PER_DAY = 8.0  # Manager/supervisor minimum coverage

# ============================================================================
# Forecasting Parameters
# ============================================================================

# Random seed for reproducibility
RANDOM_SEED = 42

# Train/test split
# We'll use the last N weeks as the test set
TEST_WEEKS = 8  # Hold out last 8 weeks (2 months) for testing

# Random Forest hyperparameters
RF_PARAMS = {
    "n_estimators": 200,
    "max_depth": 20,
    "min_samples_split": 10,
    "min_samples_leaf": 5,
    "max_features": "sqrt",
    "random_state": RANDOM_SEED,
    "n_jobs": -1,
    "verbose": 0,
}

# TimeSeriesSplit for cross-validation
N_SPLITS = 5  # Number of CV folds

# Feature engineering parameters
LAG_PERIODS = [7, 14, 28]  # Weekly lags (7, 14, 28 days back)
ROLLING_WINDOWS = [7, 28]  # Rolling averages (1 week, 4 weeks)

# ============================================================================
# BLS Calibration Parameters
# ============================================================================

# Year range to compare with BLS data
BLS_COMPARISON_START_YEAR = 2010
BLS_COMPARISON_END_YEAR = 2012

# Inflation adjustment (if needed)
# We'll use CPI from the features dataset as a deflator
USE_CPI_DEFLATOR = True

# ============================================================================
# Visualization and Reporting
# ============================================================================

# Plotting style
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FIGURE_DPI = 100
FIGURE_SIZE = (12, 6)

# Top N stores to highlight in visualizations
TOP_N_STORES = 10

# Sensitivity analysis: SPLH/IPLH variation range
SENSITIVITY_RANGE = [0.8, 0.9, 1.0, 1.1, 1.2]  # ±20% around baseline

# ============================================================================
# Data Quality Checks
# ============================================================================

# Minimum required data points per store-department combination
MIN_OBSERVATIONS = 20

# Maximum allowed missing percentage
MAX_MISSING_PCT = 0.3  # 30%

# ============================================================================
# Logging and Verbosity
# ============================================================================

VERBOSE = True  # Print progress messages
SHOW_PLOTS = False  # Set to True to display plots interactively
SAVE_PLOTS = True  # Save plots to disk
