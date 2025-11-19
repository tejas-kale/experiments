"""
Section 4-5: Time-Based Evaluation and Random Forest Forecasting

This script implements time-based train/test split, baseline models, and trains
a Random Forest model with hyperparameter tuning.
"""

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
import joblib

from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

# Import configuration
import config

warnings.filterwarnings('ignore')

print("=" * 80)
print("SECTION 4-5: TIME-BASED EVALUATION AND FORECASTING")
print("=" * 80)

# ============================================================================
# LOAD FEATURE-ENGINEERED DATA
# ============================================================================

print("\n--- Loading Feature-Engineered Data ---")

intermediate_dir = config.OUTPUT_DIR / "intermediate"
df = pd.read_csv(intermediate_dir / "features_full.csv", parse_dates=['Date'])

print(f"✓ Loaded data: {df.shape}")
print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")

# ============================================================================
# PREPARE FEATURES AND TARGET
# ============================================================================

print("\n--- Preparing Features and Target ---")

# Sort by date
df = df.sort_values(['Store', 'Date'])

# Define target variable (we'll forecast units/items)
target_col = 'total_units'

# Define feature columns (exclude target, date, identifiers, and categorical columns)
exclude_cols = [
    'Date', 'Store', 'total_sales', 'total_units',  # IDs and targets
    'Type',  # Categorical column (would need encoding)
]

# Get all potential feature columns
feature_cols = [col for col in df.columns if col not in exclude_cols]

print(f"✓ Target variable: {target_col}")
print(f"✓ Number of feature columns: {len(feature_cols)}")

# ============================================================================
# TIME-BASED TRAIN/TEST SPLIT
# ============================================================================

print("\n--- Creating Time-Based Train/Test Split ---")

# Get unique dates sorted
unique_dates = sorted(df['Date'].unique())
n_dates = len(unique_dates)

# Use last N weeks as test set
n_test = config.TEST_WEEKS
test_dates = unique_dates[-n_test:]
train_dates = unique_dates[:-n_test]

# Split data
train_df = df[df['Date'].isin(train_dates)].copy()
test_df = df[df['Date'].isin(test_dates)].copy()

print(f"✓ Total dates: {n_dates}")
print(f"✓ Train dates: {len(train_dates)} ({train_dates[0]} to {train_dates[-1]})")
print(f"✓ Test dates: {len(test_dates)} ({test_dates[0]} to {test_dates[-1]})")
print(f"✓ Train size: {len(train_df)} records")
print(f"✓ Test size: {len(test_df)} records")

# Drop rows with missing target
train_df = train_df.dropna(subset=[target_col])
test_df = test_df.dropna(subset=[target_col])

# ============================================================================
# HANDLE MISSING VALUES IN FEATURES
# ============================================================================

print("\n--- Handling Missing Values in Features ---")

# Fill missing values in lag/rolling features with 0 (conservative approach)
# In practice, we could also use forward fill or drop early records
X_train = train_df[feature_cols].copy()
X_test = test_df[feature_cols].copy()
y_train = train_df[target_col].copy()
y_test = test_df[target_col].copy()

# Fill NaNs with 0 for lag/rolling features
X_train = X_train.fillna(0)
X_test = X_test.fillna(0)

print(f"✓ Training features shape: {X_train.shape}")
print(f"✓ Test features shape: {X_test.shape}")

# ============================================================================
# BASELINE MODELS
# ============================================================================

print("\n--- Baseline Models ---")

# Baseline 1: Naive (use last week's value)
# For each store, predict the last known value from training set
baseline_naive = test_df.merge(
    train_df.groupby('Store')[target_col].last().reset_index().rename(
        columns={target_col: 'pred_naive'}
    ),
    on='Store',
    how='left'
)
baseline_naive['pred_naive'] = baseline_naive['pred_naive'].fillna(y_train.mean())

mae_naive = mean_absolute_error(y_test, baseline_naive['pred_naive'])
rmse_naive = np.sqrt(mean_squared_error(y_test, baseline_naive['pred_naive']))
mape_naive = mean_absolute_percentage_error(y_test, baseline_naive['pred_naive']) * 100

print(f"\nNaive Baseline (last value per store):")
print(f"  MAE: {mae_naive:.2f}")
print(f"  RMSE: {rmse_naive:.2f}")
print(f"  MAPE: {mape_naive:.2f}%")

# Baseline 2: Seasonal Naive (same weekday last week)
# Use the last same-weekday value
def seasonal_naive_predict(train, test):
    predictions = []
    for _, row in test.iterrows():
        store = row['Store']
        dow = row['dayofweek']
        
        # Get last value for this store and day of week
        mask = (train['Store'] == store) & (train['dayofweek'] == dow)
        if mask.any():
            pred = train.loc[mask, target_col].iloc[-1]
        else:
            pred = train[train['Store'] == store][target_col].mean()
        predictions.append(pred)
    return np.array(predictions)

pred_seasonal = seasonal_naive_predict(train_df, test_df)

mae_seasonal = mean_absolute_error(y_test, pred_seasonal)
rmse_seasonal = np.sqrt(mean_squared_error(y_test, pred_seasonal))
mape_seasonal = mean_absolute_percentage_error(y_test, pred_seasonal) * 100

print(f"\nSeasonal Naive Baseline (same weekday):")
print(f"  MAE: {mae_seasonal:.2f}")
print(f"  RMSE: {rmse_seasonal:.2f}")
print(f"  MAPE: {mape_seasonal:.2f}%")

# Baseline 3: Moving Average (mean of last 4 weeks)
# Group by store and get mean of last 4 observations
ma_preds = train_df.groupby('Store').apply(
    lambda x: x[target_col].tail(4).mean()
).reset_index().rename(columns={0: 'pred_ma'})

baseline_ma = test_df.merge(ma_preds, on='Store', how='left')
baseline_ma['pred_ma'] = baseline_ma['pred_ma'].fillna(y_train.mean())

mae_ma = mean_absolute_error(y_test, baseline_ma['pred_ma'])
rmse_ma = np.sqrt(mean_squared_error(y_test, baseline_ma['pred_ma']))
mape_ma = mean_absolute_percentage_error(y_test, baseline_ma['pred_ma']) * 100

print(f"\nMoving Average Baseline (last 4 weeks):")
print(f"  MAE: {mae_ma:.2f}")
print(f"  RMSE: {rmse_ma:.2f}")
print(f"  MAPE: {mape_ma:.2f}%")

# ============================================================================
# RANDOM FOREST WITH HYPERPARAMETER TUNING
# ============================================================================

print("\n--- Random Forest Model Training ---")

# Define parameter grid for GridSearchCV
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
}

# Use TimeSeriesSplit for cross-validation
tscv = TimeSeriesSplit(n_splits=config.N_SPLITS)

print(f"Using TimeSeriesSplit with {config.N_SPLITS} splits")
print("Performing hyperparameter search...")

# Initialize Random Forest
rf = RandomForestRegressor(random_state=config.RANDOM_STATE, n_jobs=-1)

# Grid search
grid_search = GridSearchCV(
    rf,
    param_grid,
    cv=tscv,
    scoring='neg_mean_absolute_error',
    n_jobs=-1,
    verbose=1
)

# Fit
grid_search.fit(X_train, y_train)

print(f"\n✓ Grid search complete")
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV MAE: {-grid_search.best_score_:.2f}")

# Get best model
best_rf = grid_search.best_estimator_

# ============================================================================
# FEATURE IMPORTANCES
# ============================================================================

print("\n--- Feature Importances ---")

# Get feature importances
importances = best_rf.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': importances
}).sort_values('importance', ascending=False)

print("\nTop 20 most important features:")
print(feature_importance_df.head(20))

# Save feature importances
importance_path = config.OUTPUT_DIR / "feature_importances.csv"
feature_importance_df.to_csv(importance_path, index=False)
print(f"\n✓ Saved feature importances to: {importance_path}")

# ============================================================================
# GENERATE PREDICTIONS
# ============================================================================

print("\n--- Generating Predictions ---")

# Predict on test set
y_pred = best_rf.predict(X_test)

# Create forecasts dataframe
forecasts = test_df[['Date', 'Store']].copy()
forecasts['y_true'] = y_test.values
forecasts['y_pred'] = y_pred

# Calculate metrics
mae_rf = mean_absolute_error(y_test, y_pred)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred))
mape_rf = mean_absolute_percentage_error(y_test, y_pred) * 100

print(f"\nRandom Forest Performance:")
print(f"  MAE: {mae_rf:.2f}")
print(f"  RMSE: {rmse_rf:.2f}")
print(f"  MAPE: {mape_rf:.2f}%")

# ============================================================================
# COMPARISON OF ALL MODELS
# ============================================================================

print("\n--- Model Comparison Summary ---")

comparison = pd.DataFrame({
    'Model': ['Naive', 'Seasonal Naive', 'Moving Average', 'Random Forest'],
    'MAE': [mae_naive, mae_seasonal, mae_ma, mae_rf],
    'RMSE': [rmse_naive, rmse_seasonal, rmse_ma, rmse_rf],
    'MAPE': [mape_naive, mape_seasonal, mape_ma, mape_rf]
})

print(comparison.to_string(index=False))

# Calculate improvement over best baseline
best_baseline_mae = min(mae_naive, mae_seasonal, mae_ma)
improvement = ((best_baseline_mae - mae_rf) / best_baseline_mae) * 100
print(f"\nRandom Forest improvement over best baseline: {improvement:.2f}%")

# ============================================================================
# SAVE OUTPUTS
# ============================================================================

print("\n--- Saving Outputs ---")

# Save forecasts
forecasts.to_csv(config.FORECASTS_PATH, index=False)
print(f"✓ Saved forecasts to: {config.FORECASTS_PATH}")

# Save features_train for reference
train_features = train_df[['Date', 'Store'] + feature_cols + [target_col]].copy()
train_features.to_csv(config.FEATURES_TRAIN_PATH, index=False)
print(f"✓ Saved training features to: {config.FEATURES_TRAIN_PATH}")

# Save model artifacts
joblib.dump(best_rf, config.MODEL_PATH)
print(f"✓ Saved model to: {config.MODEL_PATH}")

# Save feature names
joblib.dump(feature_cols, config.FEATURE_NAMES_PATH)
print(f"✓ Saved feature names to: {config.FEATURE_NAMES_PATH}")

# Save model comparison
comparison_path = config.OUTPUT_DIR / "model_comparison.csv"
comparison.to_csv(comparison_path, index=False)
print(f"✓ Saved model comparison to: {comparison_path}")

print("\n" + "=" * 80)
print("FORECASTING COMPLETE")
print("=" * 80)
