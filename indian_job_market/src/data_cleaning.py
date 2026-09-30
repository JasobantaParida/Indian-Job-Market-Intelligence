"""
data_cleaning.py — All preprocessing and cleaning logic.
Every function is pure: takes a DataFrame, returns a cleaned DataFrame.
"""

import re
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Salary cleaning
# ---------------------------------------------------------------------------

def _clean_salary_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace 0 salary values with NaN (0 means 'Not disclosed' in this dataset).
    Convert INR salaries in USD to INR where currency == USD.
    Derive average_salary = (minimumSalary + maximumSalary) / 2.
    """
    df = df.copy()

    # Convert USD salaries to INR (approximate: 1 USD ≈ 83 INR)
    usd_mask = df["currency"] == "USD"
    for col in ["minimumSalary", "maximumSalary"]:
        df.loc[usd_mask, col] = df.loc[usd_mask, col] * 83

    # Zero salary means undisclosed
    for col in ["minimumSalary", "maximumSalary"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[df[col] == 0, col] = np.nan

    # Sanity check: min should not exceed max
    swap_mask = df["minimumSalary"] > df["maximumSalary"]
    df.loc[swap_mask, ["minimumSalary", "maximumSalary"]] = (
        df.loc[swap_mask, ["maximumSalary", "minimumSalary"]].values
    )

    # Derived average salary
    df["average_salary"] = (df["minimumSalary"] + df["maximumSalary"]) / 2

    # Cap extreme outliers at 99th percentile (keeps realistic values)
    cap = df["average_salary"].quantile(0.99)
    df.loc[df["average_salary"] > cap, "average_salary"] = np.nan

    return df


# ---------------------------------------------------------------------------
# Experience cleaning
# ---------------------------------------------------------------------------

def _clean_experience_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure numeric experience columns are valid.
    Replace 0-0 (both zero) with NaN.
    Derive average_experience.
    """
    df = df.copy()
    for col in ["minimumExperience", "maximumExperience"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # If both are 0 it likely means undisclosed
    both_zero = (df["minimumExperience"] == 0) & (df["maximumExperience"] == 0)
    df.loc[both_zero, ["minimumExperience", "maximumExperience"]] = np.nan

    df["average_experience"] = (
        df["minimumExperience"].fillna(0) + df["maximumExperience"].fillna(0)
    ) / 2

    return df


# ---------------------------------------------------------------------------
# Location cleaning
# ---------------------------------------------------------------------------

def _clean_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the primary city from a multi-city location string.
    E.g. 'Noida, Greater Noida' → 'Noida'
         'Kolkata(Chinar Park)' → 'Kolkata'
    """
    df = df.copy()
    df["location"] = df["location"].astype(str).str.strip()

    def extract_city(loc: str) -> str:
        # Take first city before comma
        city = loc.split(",")[0].strip()
        # Remove parenthetical sub-areas
        city = re.sub(r"\(.*?\)", "", city).strip()
        return city if city else "Unknown"

    df["primary_location"] = df["location"].apply(extract_city)
    return df


# ---------------------------------------------------------------------------
# Title / company cleaning
# ---------------------------------------------------------------------------

def _clean_titles(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise job titles: strip extra spaces, fix common casing."""
    df = df.copy()
    df["title"] = df["title"].astype(str).str.strip()
    df["title"] = df["title"].str.replace(r"\s+", " ", regex=True)
    return df


def _clean_company_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip and normalise company names."""
    df = df.copy()
    df["companyName"] = df["companyName"].astype(str).str.strip()
    df.loc[df["companyName"].isin(["nan", "None", ""]), "companyName"] = "Unknown"
    return df


# ---------------------------------------------------------------------------
# Date / upload time
# ---------------------------------------------------------------------------

def _parse_job_uploaded(df: pd.DataFrame) -> pd.DataFrame:
    """
    'jobUploaded' contains relative strings like '4 Days Ago', 'Just Now'.
    Convert to approximate numeric days_ago for time-series approximation.
    """
    df = df.copy()

    def to_days_ago(s: str) -> int:
        s = str(s).strip().lower()
        if s in ("just now", "today", "few hours ago"):
            return 0
        m = re.search(r"(\d+)\s*day", s)
        if m:
            return int(m.group(1))
        if "1 day" in s:
            return 1
        # "Starts in …" — treat as future / unknown
        return np.nan

    df["days_ago"] = df["jobUploaded"].apply(to_days_ago)
    return df


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------

def _clean_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Keep AggregateRating as float; leave NaN where unavailable."""
    df = df.copy()
    df["AggregateRating"] = pd.to_numeric(df["AggregateRating"], errors="coerce")
    df["ReviewsCount"] = pd.to_numeric(df["ReviewsCount"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Master cleaner
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all cleaning steps in order and return a cleaned DataFrame.
    """
    df = df.copy()

    # 1. Drop exact duplicates
    df = df.drop_duplicates()

    # 2. Column-level cleaning
    df = _clean_salary_column(df)
    df = _clean_experience_columns(df)
    df = _clean_location(df)
    df = _clean_titles(df)
    df = _clean_company_names(df)
    df = _parse_job_uploaded(df)
    df = _clean_ratings(df)

    # 3. Drop rows where both title and companyName are missing
    df = df.dropna(subset=["title"])

    return df.reset_index(drop=True)
