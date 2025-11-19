#!/usr/bin/env python3
"""
Master Script: Run Complete Retail Labor Demand Forecasting Pipeline

This script executes all stages of the pipeline in sequence:
1. Data loading and EDA
2. Feature engineering
3. Model training and forecasting
4. Labor conversion (actuals and forecasts)
5. Productivity calibration vs BLS
6. Report generation

Usage:
    python run_all.py

All outputs are saved to the output/ and models/ directories.
"""

import sys
import subprocess
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config

print("=" * 80)
print("RETAIL LABOR DEMAND FORECASTING PIPELINE")
print("Master Script - Running All Stages")
print("=" * 80)
print()

# Define scripts to run in order
scripts = [
    ("01: Data Loading & EDA", "src/01_setup_and_load.py"),
    ("02: Feature Engineering", "src/02_feature_engineering.py"),
    ("03: Model Training & Forecasting", "src/03_model_training.py"),
    ("04: Labor Conversion", "src/04_labor_conversion.py"),
    ("05: Productivity Calibration", "src/05_productivity_calibration.py"),
    ("06: Report Generation", "src/06_generate_report.py"),
]

# Track timing
start_time = time.time()
stage_times = []

# Run each script
for stage_name, script_path in scripts:
    print("=" * 80)
    print(f"STAGE: {stage_name}")
    print(f"Script: {script_path}")
    print("=" * 80)
    print()

    script_start = time.time()

    # Run script
    full_path = project_root / script_path
    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=project_root,
        capture_output=False,  # Print output directly
    )

    script_end = time.time()
    elapsed = script_end - script_start
    stage_times.append((stage_name, elapsed))

    # Check for errors
    if result.returncode != 0:
        print()
        print("=" * 80)
        print(f"ERROR: {stage_name} failed with return code {result.returncode}")
        print("=" * 80)
        sys.exit(1)

    print()
    print(f"✓ {stage_name} completed in {elapsed:.2f} seconds")
    print()

# Total time
total_time = time.time() - start_time

# Summary
print("=" * 80)
print("PIPELINE COMPLETE")
print("=" * 80)
print()

print("Stage Timing:")
for stage_name, elapsed in stage_times:
    print(f"  {stage_name:<40} {elapsed:>8.2f}s")
print(f"  {'TOTAL':<40} {total_time:>8.2f}s")
print()

print("Outputs:")
print(f"  Data CSVs:      {config.OUTPUT_DIR}/")
print(f"  Model artifacts: {config.MODELS_DIR}/")
print(f"  Report:         {config.REPORT_PATH}")
print()

print("Key Deliverables:")
deliverables = [
    config.FEATURES_TRAIN_CSV,
    config.FORECASTS_CSV,
    config.HOURS_ACTUAL_CSV,
    config.HOURS_FORECAST_CSV,
    config.HOURS_COMPARISON_CSV,
    config.REPORT_PATH,
    config.RF_MODEL_PATH,
]

for deliverable in deliverables:
    if deliverable.exists():
        size_kb = deliverable.stat().st_size / 1024
        print(f"  ✓ {deliverable.name:<30} ({size_kb:.1f} KB)")
    else:
        print(f"  ✗ {deliverable.name:<30} (NOT FOUND)")

print()
print("=" * 80)
print("SUCCESS! All stages completed successfully.")
print("=" * 80)
print()
print(f"Read the full report: {config.REPORT_PATH}")
print()
