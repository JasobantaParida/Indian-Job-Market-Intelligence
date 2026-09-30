"""
analysis.py — Reusable aggregation helpers used by the page modules.
All functions accept a (possibly pre-filtered) DataFrame and return
a results DataFrame ready for plotting.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def top_n_by_count(df: pd.DataFrame, col: str, n: int = 10) -> pd.DataFrame:
    """Return top-n values of col by frequency, as a DataFrame."""
    return (
        df[col]
        .value_counts()
        .head(n)
        .reset_index()
        .rename(columns={"index": col, "count": "count", col: col})
    )


def mean_salary_by(df: pd.DataFrame, group_col: str, min_count: int = 5) -> pd.DataFrame:
    """
    Return mean average_salary_lpa grouped by group_col.
    Only include groups with at least min_count rows with salary data.
    """
    sal_df = df.dropna(subset=["average_salary_lpa"])
    agg = (
        sal_df.groupby(group_col)["average_salary_lpa"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_salary_lpa", "median": "median_salary_lpa", "count": "n"})
    )
    return agg[agg["n"] >= min_count].sort_values("avg_salary_lpa", ascending=False)


# ---------------------------------------------------------------------------
# Overview page
# ---------------------------------------------------------------------------

def overview_kpis(df: pd.DataFrame) -> dict:
    """Return KPI values for the overview page."""
    sal = df.dropna(subset=["average_salary_lpa"])
    return {
        "total_jobs": len(df),
        "total_companies": df["companyName"].nunique(),
        "total_locations": df["primary_location"].nunique(),
        "avg_salary_lpa": round(sal["average_salary_lpa"].mean(), 2),
        "median_salary_lpa": round(sal["average_salary_lpa"].median(), 2),
    }


def jobs_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate job postings by days_ago (0 = today, 10 = 10 days ago)."""
    return (
        df.dropna(subset=["days_ago"])
        .groupby("days_ago")
        .size()
        .reset_index(name="job_count")
        .sort_values("days_ago")
    )


# ---------------------------------------------------------------------------
# Demand page
# ---------------------------------------------------------------------------

def demand_by_role(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    return top_n_by_count(df, "title", top_n)


def demand_by_location(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    return top_n_by_count(df, "primary_location", top_n)


def demand_by_experience(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Fresher (0 Yrs)", "0–2 Yrs", "2–5 Yrs", "5–8 Yrs", "8+ Yrs", "Unknown"]
    counts = (
        df["experience_group"]
        .value_counts()
        .reset_index()
        .rename(columns={"experience_group": "experience_group", "count": "count"})
    )
    counts["sort_key"] = counts["experience_group"].apply(
        lambda x: order.index(x) if x in order else len(order)
    )
    return counts.sort_values("sort_key").drop(columns="sort_key")


# ---------------------------------------------------------------------------
# Salary page
# ---------------------------------------------------------------------------

def salary_distribution(df: pd.DataFrame) -> pd.Series:
    return df["average_salary_lpa"].dropna()


def salary_by_role(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    # Limit to top-n roles by total postings for readability
    top_roles = df["title"].value_counts().head(top_n).index.tolist()
    sub = df[df["title"].isin(top_roles)].dropna(subset=["average_salary_lpa"])
    return sub[["title", "average_salary_lpa"]]


def salary_by_location(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    top_locs = df["primary_location"].value_counts().head(top_n).index.tolist()
    sub = df[df["primary_location"].isin(top_locs)].dropna(subset=["average_salary_lpa"])
    return sub[["primary_location", "average_salary_lpa"]]


def salary_by_experience(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Fresher (0 Yrs)", "0–2 Yrs", "2–5 Yrs", "5–8 Yrs", "8+ Yrs"]
    sub = df[df["experience_group"].isin(order)].dropna(subset=["average_salary_lpa"])
    return sub[["experience_group", "average_salary_lpa"]]


# ---------------------------------------------------------------------------
# Experience page
# ---------------------------------------------------------------------------

def roles_by_experience(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    order = ["Fresher (0 Yrs)", "0–2 Yrs", "2–5 Yrs", "5–8 Yrs", "8+ Yrs"]
    top_roles = df["title"].value_counts().head(top_n).index.tolist()
    sub = df[df["title"].isin(top_roles) & df["experience_group"].isin(order)]
    return (
        sub.groupby(["title", "experience_group"])
        .size()
        .reset_index(name="count")
    )


# ---------------------------------------------------------------------------
# Fresher page
# ---------------------------------------------------------------------------

def fresher_kpis(df: pd.DataFrame) -> dict:
    fr = df[df["is_fresher"]]
    sal = fr.dropna(subset=["average_salary_lpa"])
    return {
        "total_fresher_jobs": len(fr),
        "top_roles": fr["title"].value_counts().head(10).reset_index().rename(
            columns={"title": "role", "count": "count"}),
        "top_cities": fr["primary_location"].value_counts().head(10).reset_index().rename(
            columns={"primary_location": "city", "count": "count"}),
        "top_companies": fr["companyName"].value_counts().head(10).reset_index().rename(
            columns={"companyName": "company", "count": "count"}),
        "avg_salary_lpa": round(sal["average_salary_lpa"].mean(), 2) if len(sal) > 0 else None,
    }


# ---------------------------------------------------------------------------
# Company & Location page
# ---------------------------------------------------------------------------

def top_companies(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    return top_n_by_count(df, "companyName", n)


def top_locations(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    return top_n_by_count(df, "primary_location", n)


def avg_salary_by_location(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    return mean_salary_by(df, "primary_location").head(top_n)


def company_ratings(df: pd.DataFrame, min_reviews: int = 10) -> pd.DataFrame:
    """Return companies with at least min_reviews, sorted by AggregateRating."""
    sub = df.dropna(subset=["AggregateRating"]).copy()
    agg = (
        sub.groupby("companyName")
        .agg(
            avg_rating=("AggregateRating", "mean"),
            total_reviews=("ReviewsCount", "sum"),
            job_postings=("title", "count"),
        )
        .reset_index()
    )
    return (
        agg[agg["total_reviews"] >= min_reviews]
        .sort_values("avg_rating", ascending=False)
        .head(20)
    )
