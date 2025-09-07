import os
import sys
import subprocess
from pathlib import Path

def run_pipeline():
    """Automates setup and execution of the analysis pipeline."""
    
    print("Starting reproducible run for Telangana Governance Analyst...")

    # --- Step 1: Install Dependencies ---
    print("\nInstalling dependencies from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return

    # --- Step 2: Validate API Key and Dataset ---
    print("\nChecking for API key and dataset...")
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it before running. Ex: set GEMINI_API_KEY=YOUR_KEY")
        return
    
    dataset_path = Path("data/birth_data.csv")
    if not dataset_path.is_file():
        print(f"Error: '{dataset_path}' not found.")
        print("Please place the dataset in the 'data' directory.")
        return

    # --- Step 3: Run the Analysis Pipeline ---
    print("\nExecuting the analysis pipeline...")
    try:
        subprocess.run([sys.executable, "-m", "analyst.main"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Analysis pipeline failed with error: {e}")
        return

    print("\nReproducible run complete. Outputs are in the 'outputs/' directory.")

if __name__ == "__main__":
    run_pipeline()