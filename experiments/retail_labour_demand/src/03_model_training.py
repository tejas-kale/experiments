"""
Section 4 & 5: Time-Based Evaluation and Random Forest Forecasting

This script:
1. Splits data using time-based train/test split
2. Computes baseline forecasts (naive, seasonal naive, moving average)
3. Trains Random Forest with cross-validation
4. Evaluates model performance
5. Generates forecasts for test period
6. Saves model artifacts and forecast results
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

# Import configuration
import config

warnings.filterwarnings('ignore')

print("=" * 80)
print("Section 4 & 5: Model Training and Forecasting")
print("=" * 80)
print()

# ============================================================================
# Load Feature Matrix
# ============================================================================

print("Loading feature matrix...")
features_df = joblib.load(config.OUTPUT_DIR / "features_train.pkl")
feature_info = joblib.load(config.OUTPUT_DIR / "feature_info.pkl")

print(f"✓ Loaded {len(features_df):,} records")
print(f"✓ Features: {len(feature_info['all_features'])}")
print()

# ============================================================================
# Section 4: Time-Based Train/Test Split
# ============================================================================

print("=" * 80)
print("Time-Based Train/Test Split")
print("=" * 80)
print()

# Sort by date
features_df = features_df.sort_values(['Store', 'Date']).reset_index(drop=True)

# Get unique dates
unique_dates = sorted(features_df['Date'].unique())
print(f"Total weeks: {len(unique_dates)}")
print(f"Date range: {unique_dates[0].date()} to {unique_dates[-1].date()}")
print()

# Last N weeks for testing
test_cutoff_idx = len(unique_dates) - config.TEST_WEEKS
test_cutoff_date = unique_dates[test_cutoff_idx]

print(f"Test period: Last {config.TEST_WEEKS} weeks")
print(f"Test cutoff date: {test_cutoff_date.date()}")
print()

# Split data
train_mask = features_df['Date'] < test_cutoff_date
test_mask = features_df['Date'] >= test_cutoff_date

train_df = features_df[train_mask].copy()
test_df = features_df[test_mask].copy()

print(f"Train set: {len(train_df):,} records ({train_df['Date'].min().date()} to {train_df['Date'].max().date()})")
print(f"Test set:  {len(test_df):,} records ({test_df['Date'].min().date()} to {test_df['Date'].max().date()})")
print()

# ============================================================================
# Prepare Features and Target
# ============================================================================

print("=" * 80)
print("Preparing Features and Target")
print("=" * 80)
print()

# Encode categorical features
categorical_features = ['Type']  # Store type
label_encoders = {}

for col in categorical_features:
    if col in train_df.columns:
        le = LabelEncoder()
        train_df[col] = le.fit_transform(train_df[col].astype(str))
        test_df[col] = le.transform(test_df[col].astype(str))
        label_encoders[col] = le
        print(f"✓ Encoded: {col}")

print()

# Get feature columns (exclude identifiers and target)
feature_cols = [col for col in feature_info['all_features']
                if col in train_df.columns]

# Additional categorical encoding
if 'Size_Bin' in train_df.columns:
    # Already encoded as Small/Medium/Large, encode numerically
    size_map = {'Small': 0, 'Medium': 1, 'Large': 2}
    train_df['Size_Bin'] = train_df['Size_Bin'].map(size_map)
    test_df['Size_Bin'] = test_df['Size_Bin'].map(size_map)
    feature_cols.append('Size_Bin')

# Prepare X and y
X_train = train_df[feature_cols].copy()
y_train = train_df['Target'].copy()

X_test = test_df[feature_cols].copy()
y_test = test_df['Target'].copy()

# Store identifiers for later
train_ids = train_df[['Store', 'Date']].copy()
test_ids = test_df[['Store', 'Date']].copy()

print(f"Training features: {X_train.shape}")
print(f"Training target: {y_train.shape}")
print(f"Test features: {X_test.shape}")
print(f"Test target: {y_test.shape}")
print()

# Check for any remaining NaN values
if X_train.isnull().any().any():
    print("Warning: NaN values detected in training features")
    print(X_train.isnull().sum()[X_train.isnull().sum() > 0])
    # Fill with median
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())  # Use train median for test
    print("✓ Filled with median")
    print()

# ============================================================================
# Section 4: Baseline Models
# ============================================================================

print("=" * 80)
print("Baseline Models")
print("=" * 80)
print()

# Merge test with historical data for baseline calculation
test_with_history = test_df.copy()

def calculate_metrics(y_true, y_pred, model_name):
    """Calculate and print regression metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)

    print(f"{model_name}:")
    print(f"  MAE:  ${mae:,.2f}")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  R²:   {r2:.4f}")
    print()

    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape, 'R2': r2}

baseline_results = {}

# 1. Naive Forecast: last observed value
print("1. Naive Forecast (last week)")
naive_pred = []
for _, row in test_with_history.iterrows():
    # Get last week's sales for this store
    last_week = train_df[
        (train_df['Store'] == row['Store']) &
        (train_df['Date'] == train_df['Date'].max())
    ]['Target'].values
    if len(last_week) > 0:
        naive_pred.append(last_week[0])
    else:
        naive_pred.append(y_train.mean())

naive_pred = np.array(naive_pred)
baseline_results['Naive'] = calculate_metrics(y_test, naive_pred, "Naive")

# 2. Seasonal Naive: same week last year (or closest)
print("2. Seasonal Naive (same week, 52 weeks ago)")
seasonal_pred = []
for _, row in test_with_history.iterrows():
    # Get sales from 52 weeks ago for this store
    target_date = row['Date'] - pd.Timedelta(weeks=52)
    historical = train_df[
        (train_df['Store'] == row['Store']) &
        (train_df['Date'] == target_date)
    ]['Target'].values

    if len(historical) > 0:
        seasonal_pred.append(historical[0])
    else:
        # Fallback to mean
        seasonal_pred.append(y_train.mean())

seasonal_pred = np.array(seasonal_pred)
baseline_results['Seasonal Naive'] = calculate_metrics(y_test, seasonal_pred, "Seasonal Naive")

# 3. Moving Average: 4-week average
print("3. Moving Average (last 4 weeks)")
ma_pred = []
for _, row in test_with_history.iterrows():
    # Get last 4 weeks for this store
    recent = train_df[
        train_df['Store'] == row['Store']
    ].sort_values('Date').tail(4)['Target'].values

    if len(recent) > 0:
        ma_pred.append(recent.mean())
    else:
        ma_pred.append(y_train.mean())

ma_pred = np.array(ma_pred)
baseline_results['Moving Average'] = calculate_metrics(y_test, ma_pred, "Moving Average")

# ============================================================================
# Section 5: Random Forest Training
# ============================================================================

print("=" * 80)
print("Random Forest Training")
print("=" * 80)
print()

print("Hyperparameters:")
for key, value in config.RF_PARAMS.items():
    print(f"  {key}: {value}")
print()

# Initialize Random Forest
rf = RandomForestRegressor(**config.RF_PARAMS)

# Train model
print("Training Random Forest...")
rf.fit(X_train, y_train)
print("✓ Training complete")
print()

# Feature importance
print("Top 10 Feature Importances:")
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': rf.feature_importances_
}).sort_values('Importance', ascending=False)

print(feature_importance.head(10).to_string(index=False))
print()

# Save feature importance
feature_importance.to_csv(config.OUTPUT_DIR / "feature_importance.csv", index=False)
print(f"✓ Saved: feature_importance.csv")
print()

# ============================================================================
# Model Evaluation
# ============================================================================

print("=" * 80)
print("Model Evaluation")
print("=" * 80)
print()

# Predictions
print("Generating predictions...")
y_train_pred = rf.predict(X_train)
y_test_pred = rf.predict(X_test)
print("✓ Predictions generated")
print()

# Training set performance
print("Training Set Performance:")
train_metrics = calculate_metrics(y_train, y_train_pred, "Random Forest")
baseline_results['Random Forest (Train)'] = train_metrics

# Test set performance
print("Test Set Performance:")
test_metrics = calculate_metrics(y_test, y_test_pred, "Random Forest")
baseline_results['Random Forest (Test)'] = test_metrics

# Compare to baselines
print("=" * 80)
print("Model Comparison (Test Set)")
print("=" * 80)
comparison_df = pd.DataFrame(baseline_results).T
comparison_df = comparison_df[['MAE', 'RMSE', 'MAPE', 'R2']]
print(comparison_df.to_string())
print()

# Save comparison
comparison_df.to_csv(config.OUTPUT_DIR / "model_comparison.csv")
print(f"✓ Saved: model_comparison.csv")
print()

# ============================================================================
# Generate Forecast DataFrame
# ============================================================================

print("=" * 80)
print("Generating Forecast Output")
print("=" * 80)
print()

# Create forecast dataframe
forecasts = pd.DataFrame({
    'Store': test_ids['Store'],
    'Date': test_ids['Date'],
    'y_true': y_test,
    'y_pred': y_test_pred,
    'error': y_test_pred - y_test,
    'abs_error': np.abs(y_test_pred - y_test),
    'pct_error': (y_test_pred - y_test) / y_test * 100
})

# Add store metadata
stores_df = joblib.load(config.OUTPUT_DIR / "stores_clean.pkl")
forecasts = forecasts.merge(stores_df, on='Store', how='left')

# Save forecasts
forecasts.to_csv(config.FORECASTS_CSV, index=False)
print(f"✓ Saved: {config.FORECASTS_CSV}")
print(f"  Records: {len(forecasts):,}")
print()

# Summary statistics
print("Forecast Summary:")
print(f"  Mean actual sales:    ${forecasts['y_true'].mean():,.2f}")
print(f"  Mean predicted sales: ${forecasts['y_pred'].mean():,.2f}")
print(f"  Mean absolute error:  ${forecasts['abs_error'].mean():,.2f}")
print(f"  Median abs error:     ${forecasts['abs_error'].median():,.2f}")
print()

# By store type
print("Forecast Performance by Store Type:")
by_type = forecasts.groupby('Type').agg({
    'abs_error': 'mean',
    'pct_error': lambda x: np.abs(x).mean()
}).round(2)
by_type.columns = ['Mean Abs Error ($)', 'Mean Abs % Error']
print(by_type.to_string())
print()

# ============================================================================
# Save Model Artifacts
# ============================================================================

print("=" * 80)
print("Saving Model Artifacts")
print("=" * 80)
print()

# Save Random Forest model
joblib.dump(rf, config.RF_MODEL_PATH)
print(f"✓ Saved: {config.RF_MODEL_PATH}")

# Save label encoders
joblib.dump(label_encoders, config.MODELS_DIR / "label_encoders.pkl")
print(f"✓ Saved: label_encoders.pkl")

# Save feature columns
joblib.dump(feature_cols, config.MODELS_DIR / "feature_columns.pkl")
print(f"✓ Saved: feature_columns.pkl")

# Save train/test split info
split_info = {
    'test_cutoff_date': test_cutoff_date,
    'train_start': train_df['Date'].min(),
    'train_end': train_df['Date'].max(),
    'test_start': test_df['Date'].min(),
    'test_end': test_df['Date'].max(),
    'n_train': len(train_df),
    'n_test': len(test_df),
}
joblib.dump(split_info, config.OUTPUT_DIR / "split_info.pkl")
print(f"✓ Saved: split_info.pkl")
print()

# ============================================================================
# Visualization
# ============================================================================

if config.SAVE_PLOTS:
    print("=" * 80)
    print("Generating Visualizations")
    print("=" * 80)
    print()

    # 1. Actual vs Predicted
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(forecasts['y_true'], forecasts['y_pred'], alpha=0.3)
    ax.plot([forecasts['y_true'].min(), forecasts['y_true'].max()],
            [forecasts['y_true'].min(), forecasts['y_true'].max()],
            'r--', lw=2)
    ax.set_xlabel('Actual Sales ($)')
    ax.set_ylabel('Predicted Sales ($)')
    ax.set_title('Random Forest: Actual vs Predicted Sales')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'actual_vs_predicted.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: actual_vs_predicted.png")

    # 2. Feature Importance
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features = feature_importance.head(15)
    ax.barh(top_features['Feature'], top_features['Importance'])
    ax.set_xlabel('Importance')
    ax.set_title('Top 15 Feature Importances')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'feature_importance.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: feature_importance.png")

    # 3. Forecast time series for sample stores
    sample_stores = forecasts['Store'].unique()[:5]
    fig, axes = plt.subplots(5, 1, figsize=(14, 12))
    for idx, store in enumerate(sample_stores):
        store_data = forecasts[forecasts['Store'] == store].sort_values('Date')
        ax = axes[idx]
        ax.plot(store_data['Date'], store_data['y_true'], 'o-', label='Actual', alpha=0.7)
        ax.plot(store_data['Date'], store_data['y_pred'], 's-', label='Predicted', alpha=0.7)
        ax.set_title(f'Store {store}')
        ax.set_ylabel('Sales ($)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel('Date')
    plt.tight_layout()
    plt.savefig(config.OUTPUT_DIR / 'forecast_time_series.png', dpi=config.FIGURE_DPI)
    plt.close()
    print("✓ Saved: forecast_time_series.png")

    print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Model: Random Forest")
print(f"Training samples: {len(X_train):,}")
print(f"Test samples: {len(X_test):,}")
print(f"Features: {len(feature_cols)}")
print(f"Test RMSE: ${test_metrics['RMSE']:,.2f}")
print(f"Test MAE: ${test_metrics['MAE']:,.2f}")
print(f"Test MAPE: {test_metrics['MAPE']:.2f}%")
print(f"Test R²: {test_metrics['R2']:.4f}")
print()
print("✓ Model training and forecasting complete!")
print("=" * 80)
