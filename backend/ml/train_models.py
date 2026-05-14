import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import our models module
from ml.models import train_and_save_models


def main():
    """Train and save crop yield prediction models"""
    print("Training crop yield prediction models for Mysuru region...")
    results = train_and_save_models()
    
    print("✅ Models saved successfully!")
    print(f"Random Forest R² score: {results['rf_score']:.4f}")
    print(f"XGBoost R² score: {results['xgb_score']:.4f}")
    print("Model files:")
    print(f"  - {results['random_forest']}")
    print(f"  - {results['xgboost']}")


if __name__ == "__main__":
    main()