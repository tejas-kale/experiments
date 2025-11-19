"""
Configuration file for Retail Labour Demand Forecasting.
All paths and planning parameters are defined here.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "models"

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA PATHS
# ============================================================================

# Favorita historical data paths
SALES_PATH = DATA_DIR / "historical_sales_data" / "sales data-set.csv"
STORES_PATH = DATA_DIR / "historical_sales_data" / "stores data-set.csv"
FEATURES_PATH = DATA_DIR / "historical_sales_data" / "Features data set.csv"

# BLS labor productivity data
BLS_LABOR_PRODUCTIVITY_PATH = DATA_DIR / "labour_productivity.csv"

# ============================================================================
# PLANNING PARAMETERS
# ============================================================================

# Labor conversion mode: "SPLH" (Sales per Labor Hour) or "IPLH" (Items per Labor Hour)
CONVERSION_MODE = "IPLH"  # Using IPLH since we have units sold

# SPLH values (Sales per Labor Hour) - example values for retail grocery
# These are per-store average targets; adjust based on actual store performance data
SPLH_PER_STORE = {
    "default": 150.0,  # Default: $150 in sales per labor hour
}

# IPLH values (Items per Labor Hour) - example values for retail grocery
# These are per-store average targets; adjust based on actual operational data
IPLH_PER_STORE = {
    "default": 50.0,  # Default: 50 items processed per labor hour
}

# Baseline hours for fixed tasks (e.g., opening/closing, management)
# These are daily baseline hours that don't scale with demand
BASELINE_HOURS_PER_STORE_DAY = 8.0  # 8 hours of fixed tasks per day per store

# ============================================================================
# MODEL PARAMETERS
# ============================================================================

# Random Forest parameters
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 20
RF_MIN_SAMPLES_SPLIT = 5
RF_MIN_SAMPLES_LEAF = 2
RF_RANDOM_STATE = 42

# Time series split parameters
N_SPLITS = 3  # Number of splits for TimeSeriesSplit
TEST_WEEKS = 4  # Last N weeks for test set

# Feature engineering parameters
LAG_DAYS = [7, 14, 28]  # Lag features to create
ROLLING_WINDOWS = [7, 14, 28]  # Rolling mean windows

# ============================================================================
# OUTPUT PATHS
# ============================================================================

# Output CSV files
FEATURES_TRAIN_PATH = OUTPUT_DIR / "features_train.csv"
FORECASTS_PATH = OUTPUT_DIR / "forecasts.csv"
HOURS_ACTUAL_PATH = OUTPUT_DIR / "hours_actual.csv"
HOURS_FORECAST_PATH = OUTPUT_DIR / "hours_forecast.csv"
HOURS_COMPARISON_PATH = OUTPUT_DIR / "hours_comparison.csv"

# Model artifacts
MODEL_PATH = MODELS_DIR / "random_forest_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.joblib"

# Report
REPORT_PATH = BASE_DIR / "README_report.md"

# ============================================================================
# GLOBAL SETTINGS
# ============================================================================

# Random seed for reproducibility
RANDOM_STATE = 42

# Plotting style
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FIGURE_DPI = 100
