"""
feature_engineering.py — Derives new columns used across all pages.
All functions are pure transformers.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Experience buckets
# ---------------------------------------------------------------------------

EXP_BINS = [-0.1, 0, 2, 5, 8, 100]
EXP_LABELS = ["Fresher (0 Yrs)", "0–2 Yrs", "2–5 Yrs", "5–8 Yrs", "8+ Yrs"]


def add_experience_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create 'experience_group' from minimumExperience.
    Fresher = minimumExperience == 0
    """
    df = df.copy()
    df["experience_group"] = pd.cut(
        df["minimumExperience"].fillna(-1),
        bins=EXP_BINS,
        labels=EXP_LABELS,
        right=True,
    ).astype(str)
    df.loc[df["experience_group"] == "nan", "experience_group"] = "Unknown"
    return df


# ---------------------------------------------------------------------------
# Salary bucket (in Lakhs PA for readability)
# ---------------------------------------------------------------------------

def add_salary_lpa(df: pd.DataFrame) -> pd.DataFrame:
    """Convert rupee salary columns to Lakhs Per Annum (LPA) for display."""
    df = df.copy()
    for col in ["minimumSalary", "maximumSalary", "average_salary"]:
        if col in df.columns:
            df[f"{col}_lpa"] = (df[col] / 100_000).round(2)
    return df


# ---------------------------------------------------------------------------
# Fresher flag
# ---------------------------------------------------------------------------

def add_fresher_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Mark rows suitable for freshers (minimumExperience == 0)."""
    df = df.copy()
    df["is_fresher"] = (
        df["minimumExperience"].fillna(99) == 0
    )
    return df


# ---------------------------------------------------------------------------
# Master feature engineer
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run all feature engineering steps."""
    df = add_experience_group(df)
    df = add_salary_lpa(df)
    df = add_fresher_flag(df)
    return df
