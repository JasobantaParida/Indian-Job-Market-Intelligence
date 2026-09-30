"""
ml_salary_prediction.py — Salary prediction pipeline for the Indian
Job Market dataset.

Target : average_salary_lpa
Features: minimumExperience, maximumExperience, title (top-N), primary_location (top-N)
Models  : Linear Regression (baseline), Random Forest, Gradient Boosting

NOTE: No Streamlit imports here. The page (11_Salary_Prediction.py) applies
@st.cache_data so this module stays import-safe.
"""

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TARGET = "average_salary_lpa"
TOP_N_ROLES = 50
TOP_N_LOCS  = 50
RARE_LABEL  = "__other__"

MODELS = {
    "Linear Regression (Baseline)": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
}


# ---------------------------------------------------------------------------
# Feature preparation
# ---------------------------------------------------------------------------

def _prepare_features(df: pd.DataFrame):
    """
    Return X (feature DataFrame) and y (target Series) after
    - filtering to rows with salary disclosed
    - reducing high-cardinality categoricals to top-N + RARE_LABEL
    """
    sal = df.dropna(subset=[TARGET]).copy()
    if len(sal) < 200:
        raise ValueError("Insufficient salary data to train a model (need ≥ 200 rows).")

    # Reduce cardinality
    for col, top_n in [("title", TOP_N_ROLES), ("primary_location", TOP_N_LOCS)]:
        top_vals = sal[col].value_counts().head(top_n).index
        sal[col] = sal[col].where(sal[col].isin(top_vals), other=RARE_LABEL)

    feature_cols = ["minimumExperience", "maximumExperience", "title", "primary_location"]
    X = sal[feature_cols].copy()
    y = sal[TARGET]
    return X, y, sal[feature_cols + [TARGET]]


def _build_pipeline(model) -> Pipeline:
    numeric_features  = ["minimumExperience", "maximumExperience"]
    categoric_features = ["title", "primary_location"]

    numeric_transformer = SimpleImputer(strategy="median")
    categoric_transformer = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value=RARE_LABEL)),
        ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categoric_transformer, categoric_features),
    ])

    return Pipeline([("preprocessor", preprocessor), ("model", model)])


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_models(df: pd.DataFrame) -> dict:
    """
    Train all models and return a results dict.
    Pure function — no Streamlit dependency. Callers apply @st.cache_data.
    """
    try:
        X, y, _ = _prepare_features(df)
    except ValueError as e:
        return {"error": str(e)}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = {}
    for name, model in MODELS.items():
        pipe = _build_pipeline(model)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        mae  = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2   = r2_score(y_test, y_pred)

        results[name] = {
            "pipeline": pipe,
            "mae":  round(mae,  3),
            "rmse": round(rmse, 3),
            "r2":   round(r2,   3),
            "y_test":  y_test.values,
            "y_pred":  y_pred,
        }

    return results


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict_salary(pipeline, title: str, location: str,
                   min_exp: float, max_exp: float) -> float:
    """Return a salary estimate in LPA for one job profile."""
    row = pd.DataFrame([{
        "title": title,
        "primary_location": location,
        "minimumExperience": min_exp,
        "maximumExperience": max_exp,
    }])
    return float(pipeline.predict(row)[0])


# ---------------------------------------------------------------------------
# Helpers for UI dropdowns
# ---------------------------------------------------------------------------

def get_top_roles(df: pd.DataFrame, n: int = TOP_N_ROLES) -> list:
    return sorted(df["title"].value_counts().head(n).index.tolist())


def get_top_locations(df: pd.DataFrame, n: int = TOP_N_LOCS) -> list:
    return sorted(df["primary_location"].value_counts().head(n).index.tolist())
