"""
Main Runner Script

This script executes all analysis scripts in sequence to ensure end-to-end
reproducibility of the retail labor demand forecasting pipeline.
"""

import sys
import subprocess
from pathlib import Path
import time

def run_script(script_path, script_name):
    """Run a Python script and handle errors."""
    print("\n" + "=" * 80)
    print(f"RUNNING: {script_name}")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,
            text=True
        )
        elapsed = time.time() - start_time
        print(f"\n✓ {script_name} completed successfully in {elapsed:.2f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n✗ {script_name} failed after {elapsed:.2f} seconds")
        print(f"Error: {e}")
        return False

def main():
    """Execute all scripts in the pipeline."""
    print("=" * 80)
    print("RETAIL LABOR DEMAND FORECASTING PIPELINE")
    print("=" * 80)
    print()
    print("This pipeline will execute the following steps:")
    print("  1. Environment setup and data loading")
    print("  2. Feature engineering")
    print("  3. Model training and forecasting")
    print("  4. Labor hour conversion")
    print("  5. Productivity calibration")
    print("  6. Diagnostics and sensitivity analysis")
    print("  7. Report generation")
    print()
    
    # Define scripts in execution order
    base_dir = Path(__file__).parent
    scripts = [
        ("01_environment_and_data_loading.py", "Environment Setup & Data Loading"),
        ("02_feature_engineering.py", "Feature Engineering"),
        ("03_forecasting.py", "Model Training & Forecasting"),
        ("04_labor_conversion.py", "Labor Hour Conversion"),
        ("05_productivity_calibration.py", "Productivity Calibration"),
        ("06_diagnostics.py", "Diagnostics & Sensitivity Analysis"),
        ("07_generate_report.py", "Report Generation"),
    ]
    
    # Execute scripts
    overall_start = time.time()
    success_count = 0
    
    for script_file, script_name in scripts:
        script_path = base_dir / script_file
        
        if not script_path.exists():
            print(f"\n✗ Script not found: {script_path}")
            continue
        
        success = run_script(script_path, script_name)
        
        if success:
            success_count += 1
        else:
            print(f"\nPipeline stopped due to error in {script_name}")
            print("Please check the error messages above.")
            sys.exit(1)
    
    # Summary
    overall_elapsed = time.time() - overall_start
    
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"\nTotal scripts executed: {success_count}/{len(scripts)}")
    print(f"Total time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.2f} minutes)")
    
    if success_count == len(scripts):
        print("\n✓ All scripts completed successfully!")
        print("\nOutput files are available in the 'output' directory.")
        print("See README_report.md for detailed results and methodology.")
    else:
        print(f"\n✗ Pipeline incomplete: {len(scripts) - success_count} script(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
