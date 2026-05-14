import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from typing import Dict, Any, Tuple, List
import joblib
import os
from pathlib import Path

# Define model directory
MODEL_DIR = Path(__file__).parent / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

# Define crop types for Mysuru region
MYSURU_CROPS = [
    "ragi",       # Finger millet - staple crop
    "maize",      # Corn - widely grown
    "sugarcane",  # High value crop
    "paddy"       # Rice in irrigated areas
]

# Define soil types for Mysuru region
MYSURU_SOIL_TYPES = [
    "red_sandy_loam",  # Most common in Mysuru
    "black_cotton",    # Good for cotton and sugarcane
    "laterite",        # Found in some areas
    "clay"             # Found in some areas
]


def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic data for training crop yield prediction models
    for Mysuru region with realistic values.
    """
    np.random.seed(42)
    
    # Generate random data with realistic ranges for Mysuru region
    data = {
        "crop": np.random.choice(MYSURU_CROPS, n_samples),
        "soil_type": np.random.choice(MYSURU_SOIL_TYPES, n_samples),
        "rainfall_mm": np.random.normal(800, 150, n_samples),  # Annual rainfall in mm
        "temperature_c": np.random.normal(25, 3, n_samples),   # Average temperature in Celsius
        "nitrogen_kg_ha": np.random.normal(120, 30, n_samples),  # N in kg/ha
        "phosphorus_kg_ha": np.random.normal(60, 15, n_samples),  # P in kg/ha
        "potassium_kg_ha": np.random.normal(80, 20, n_samples),   # K in kg/ha
        "ndvi": np.random.normal(0.7, 0.1, n_samples).clip(0.3, 0.9),  # NDVI values
        "soil_moisture": np.random.normal(0.6, 0.1, n_samples).clip(0.3, 0.8),  # Soil moisture
        "irrigation": np.random.choice(["drip", "sprinkler", "flood", "rainfed"], n_samples),
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate synthetic yield based on input features with realistic values
    # Base yield values for different crops in tons/hectare
    base_yields = {
        "ragi": 2.5,      # 2-3 tons/ha
        "maize": 5.0,     # 4-6 tons/ha
        "sugarcane": 80.0, # 70-90 tons/ha
        "paddy": 4.0      # 3-5 tons/ha
    }
    
    # Soil type coefficients
    soil_coeffs = {
        "red_sandy_loam": 1.0,
        "black_cotton": 1.1,
        "laterite": 0.8,
        "clay": 0.9
    }
    
    # Irrigation coefficients
    irrigation_coeffs = {
        "drip": 1.2,
        "sprinkler": 1.1,
        "flood": 1.0,
        "rainfed": 0.8
    }
    
    # Calculate yield
    yields = []
    for i in range(n_samples):
        crop = df.iloc[i]["crop"]
        soil = df.iloc[i]["soil_type"]
        irrigation = df.iloc[i]["irrigation"]
        
        # Base yield for the crop
        base_yield = base_yields[crop]
        
        # Apply soil coefficient
        yield_value = base_yield * soil_coeffs[soil]
        
        # Apply irrigation coefficient
        yield_value *= irrigation_coeffs[irrigation]
        
        # Apply NPK effect (simplified)
        n_effect = df.iloc[i]["nitrogen_kg_ha"] / 120  # Normalize to optimal value
        p_effect = df.iloc[i]["phosphorus_kg_ha"] / 60
        k_effect = df.iloc[i]["potassium_kg_ha"] / 80
        npk_effect = (n_effect + p_effect + k_effect) / 3
        yield_value *= 0.7 + 0.6 * npk_effect  # Scale effect
        
        # Apply rainfall and temperature effects
        rainfall_mm = df.iloc[i]["rainfall_mm"]
        temp_c = df.iloc[i]["temperature_c"]
        
        # Optimal ranges vary by crop
        if crop == "ragi":
            # Ragi is drought-resistant
            rainfall_effect = 1.0 if 500 <= rainfall_mm <= 900 else 0.8
            temp_effect = 1.0 if 20 <= temp_c <= 30 else 0.9
        elif crop == "maize":
            rainfall_effect = 1.0 if 700 <= rainfall_mm <= 1100 else 0.8
            temp_effect = 1.0 if 22 <= temp_c <= 28 else 0.85
        elif crop == "sugarcane":
            rainfall_effect = 1.0 if 1000 <= rainfall_mm <= 1500 else 0.75
            temp_effect = 1.0 if 24 <= temp_c <= 30 else 0.8
        elif crop == "paddy":
            rainfall_effect = 1.0 if 1000 <= rainfall_mm <= 1600 else 0.7
            temp_effect = 1.0 if 22 <= temp_c <= 32 else 0.8
        
        yield_value *= rainfall_effect * temp_effect
        
        # Apply NDVI effect
        ndvi = df.iloc[i]["ndvi"]
        ndvi_effect = 0.6 + 0.8 * ndvi  # Higher NDVI generally means better yield
        yield_value *= ndvi_effect
        
        # Add some random noise
        yield_value *= np.random.normal(1.0, 0.05)
        
        yields.append(yield_value)
    
    df["yield_tons_per_ha"] = yields
    
    return df


def preprocess_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocess data for model training
    """
    # One-hot encode categorical features
    df_encoded = pd.get_dummies(df, columns=["crop", "soil_type", "irrigation"], drop_first=False)
    
    # Split features and target
    X = df_encoded.drop("yield_tons_per_ha", axis=1)
    y = df_encoded["yield_tons_per_ha"]
    
    return X, y


def train_random_forest_model(X: np.ndarray, y: np.ndarray) -> Pipeline:
    """
    Train a Random Forest model for crop yield prediction
    """
    # Create pipeline with preprocessing and model
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X, y)
    
    return pipeline


def train_xgboost_model(X: np.ndarray, y: np.ndarray) -> Pipeline:
    """
    Train an XGBoost model for crop yield prediction
    """
    # Create pipeline with preprocessing and model
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X, y)
    
    return pipeline


def train_lightgbm_model(X: np.ndarray, y: np.ndarray) -> Pipeline:
    """
    Train a LightGBM model for crop yield prediction
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LGBMRegressor(n_estimators=100, learning_rate=0.1, random_state=42))
    ])
    pipeline.fit(X, y)
    return pipeline


def train_mlp_model(X: np.ndarray, y: np.ndarray) -> Pipeline:
    """
    Train a Multi-Layer Perceptron (Neural Network) for crop yield prediction
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42))
    ])
    pipeline.fit(X, y)
    return pipeline


def train_and_save_models() -> Dict[str, str]:
    """
    Train and save Random Forest and XGBoost models
    """
    # Generate synthetic data
    df = generate_synthetic_data(n_samples=2000)
    
    # Preprocess data
    X, y = preprocess_data(df)
    
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest model
    rf_model = train_random_forest_model(X_train, y_train)
    rf_score = rf_model.score(X_test, y_test)
    
    # Train XGBoost model
    xgb_model = train_xgboost_model(X_train, y_train)
    xgb_score = xgb_model.score(X_test, y_test)
    
    # Train LightGBM model
    lgbm_model = train_lightgbm_model(X_train, y_train)
    lgbm_score = lgbm_model.score(X_test, y_test)
    
    # Train MLP model
    mlp_model = train_mlp_model(X_train, y_train)
    mlp_score = mlp_model.score(X_test, y_test)
    
    # Save models
    rf_model_path = MODEL_DIR / "random_forest_yield_model.joblib"
    xgb_model_path = MODEL_DIR / "xgboost_yield_model.joblib"
    lgbm_model_path = MODEL_DIR / "lightgbm_yield_model.joblib"
    mlp_model_path = MODEL_DIR / "mlp_yield_model.joblib"
    feature_names_path = MODEL_DIR / "feature_names.joblib"
    
    joblib.dump(rf_model, rf_model_path)
    joblib.dump(xgb_model, xgb_model_path)
    joblib.dump(lgbm_model, lgbm_model_path)
    joblib.dump(mlp_model, mlp_model_path)
    
    # Save feature names for later use in predictions
    feature_names = X.columns.tolist()
    joblib.dump(feature_names, feature_names_path)
    
    return {
        "random_forest": str(rf_model_path),
        "xgboost": str(xgb_model_path),
        "lightgbm": str(lgbm_model_path),
        "mlp": str(mlp_model_path),
        "rf_score": rf_score,
        "xgb_score": xgb_score,
        "lgbm_score": lgbm_score,
        "mlp_score": mlp_score,
    }


def load_models() -> Dict[str, Any]:
    """
    Load trained models
    """
    rf_path = MODEL_DIR / "random_forest_yield_model.joblib"
    xgb_path = MODEL_DIR / "xgboost_yield_model.joblib"
    lgbm_path = MODEL_DIR / "lightgbm_yield_model.joblib"
    mlp_path = MODEL_DIR / "mlp_yield_model.joblib"
    feature_names_path = MODEL_DIR / "feature_names.joblib"
    
    # Check if models exist
    if not rf_path.exists() or not xgb_path.exists() or not lgbm_path.exists() or not mlp_path.exists():
        print("Models not found or incomplete. Training new models...")
        train_and_save_models()
    
    # Load models
    rf_model = joblib.load(rf_path)
    xgb_model = joblib.load(xgb_path)
    lgbm_model = joblib.load(lgbm_path)
    mlp_model = joblib.load(mlp_path)
    
    # Load feature names if available, otherwise generate from training
    if feature_names_path.exists():
        feature_names = joblib.load(feature_names_path)
    else:
        print("Feature names not found. Generating from training data...")
        # Generate synthetic data to get feature names
        df = generate_synthetic_data(n_samples=100)
        X, _ = preprocess_data(df)
        feature_names = X.columns.tolist()
        joblib.dump(feature_names, feature_names_path)
    
    return {
        "random_forest": rf_model,
        "xgboost": xgb_model,
        "lightgbm": lgbm_model,
        "mlp": mlp_model,
        "feature_names": feature_names
    }


def get_feature_importance(model_name: str = "random_forest") -> Dict[str, float]:
    """
    Get feature importance from the trained model
    """
    models = load_models()
    model = models[model_name]
    feature_names = models["feature_names"]
    
    # Extract feature importance
    if model_name == "random_forest":
        importance = model.named_steps["model"].feature_importances_
    else:  # xgboost
        importance = model.named_steps["model"].feature_importances_
    
    # Create dictionary of feature importance
    importance_dict = {feature: float(imp) for feature, imp in zip(feature_names, importance)}
    
    # Sort by importance
    importance_dict = {k: v for k, v in sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)}
    
    return importance_dict


if __name__ == "__main__":
    # Train and save models if run directly
    results = train_and_save_models()
    print(f"Models saved to {MODEL_DIR}")
    print(f"Random Forest R² score: {results['rf_score']:.4f}")
    print(f"XGBoost R² score: {results['xgb_score']:.4f}")
    print(f"LightGBM R² score: {results['lgbm_score']:.4f}")
    print(f"MLP (Neural Net) R² score: {results['mlp_score']:.4f}")