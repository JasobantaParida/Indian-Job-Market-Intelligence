"""
statistics_analysis.py — Statistical summaries and comparisons for the
Indian Job Market dataset.  All functions are pure (DataFrame in → result out).
"""

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------

def numeric_summary(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Full descriptive stat table for a single numeric column."""
    s = df[col].dropna()
    if len(s) == 0:
        return pd.DataFrame({"Statistic": ["No data"], "Value": [None]})

    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1

    rows = [
        ("Count",      len(s)),
        ("Mean",       round(s.mean(), 3)),
        ("Median",     round(s.median(), 3)),
        ("Mode",       round(s.mode().iloc[0], 3) if len(s.mode()) > 0 else None),
        ("Std Dev",    round(s.std(), 3)),
        ("Variance",   round(s.var(), 3)),
        ("Min",        round(s.min(), 3)),
        ("P10",        round(s.quantile(0.10), 3)),
        ("Q1 (P25)",   round(q1, 3)),
        ("Q3 (P75)",   round(q3, 3)),
        ("P90",        round(s.quantile(0.90), 3)),
        ("P95",        round(s.quantile(0.95), 3)),
        ("P99",        round(s.quantile(0.99), 3)),
        ("Max",        round(s.max(), 3)),
        ("IQR",        round(iqr, 3)),
        ("Skewness",   round(s.skew(), 3)),
        ("Kurtosis",   round(s.kurtosis(), 3)),
    ]
    return pd.DataFrame(rows, columns=["Statistic", "Value"])


def outlier_summary(df: pd.DataFrame, col: str) -> dict:
    """Return count and bounds of IQR-based outliers."""
    s = df[col].dropna()
    if len(s) == 0:
        return {}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo = q1 - 1.5 * iqr
    hi = q3 + 1.5 * iqr
    outliers = s[(s < lo) | (s > hi)]
    return {
        "lower_fence": round(lo, 2),
        "upper_fence": round(hi, 2),
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(s) * 100, 1),
    }


# ---------------------------------------------------------------------------
# Grouped salary comparisons
# ---------------------------------------------------------------------------

def salary_stats_by_group(df: pd.DataFrame, group_col: str, min_n: int = 10) -> pd.DataFrame:
    """Return mean, median, std, count per group for average_salary_lpa."""
    sal = df.dropna(subset=["average_salary_lpa"])
    agg = (
        sal.groupby(group_col)["average_salary_lpa"]
        .agg(
            Count="count",
            Mean="mean",
            Median="median",
            Std="std",
            Min="min",
            Max="max",
        )
        .reset_index()
        .rename(columns={group_col: "Group"})
    )
    agg = agg[agg["Count"] >= min_n]
    agg[["Mean", "Median", "Std", "Min", "Max"]] = agg[
        ["Mean", "Median", "Std", "Min", "Max"]
    ].round(2)
    return agg.sort_values("Mean", ascending=False)


# ---------------------------------------------------------------------------
# Correlation matrix
# ---------------------------------------------------------------------------

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation among key numeric columns."""
    num_cols = [
        "minimumExperience", "maximumExperience", "average_experience",
        "minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa",
        "AggregateRating", "ReviewsCount",
    ]
    available = [c for c in num_cols if c in df.columns]
    return df[available].corr(method="pearson").round(3)


# ---------------------------------------------------------------------------
# One-way ANOVA: salary across experience groups
# ---------------------------------------------------------------------------

def anova_salary_by_experience(df: pd.DataFrame) -> dict:
    """
    One-way ANOVA: does average salary differ across experience groups?
    Returns F-stat, p-value, and an interpretation caveat.
    IMPORTANT: ANOVA assumes roughly equal variances and normal distribution
    within groups. With n≈100K, almost any difference will be 'significant'.
    Treat as descriptive evidence, not causal proof.
    """
    exp_order = [
        "Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs",
        "5\u20138 Yrs", "8+ Yrs",
    ]
    groups = []
    for grp in exp_order:
        s = df[df["experience_group"] == grp]["average_salary_lpa"].dropna()
        if len(s) >= 30:
            groups.append(s.values)

    if len(groups) < 2:
        return {"error": "Insufficient data for ANOVA"}

    f_stat, p_val = scipy_stats.f_oneway(*groups)
    return {
        "f_statistic": round(float(f_stat), 3),
        "p_value": float(p_val),
        "significant": p_val < 0.05,
        "caveat": (
            "With ~100K records even tiny differences become statistically significant. "
            "Treat this as descriptive evidence of salary trends, not causal proof."
        ),
    }


# ---------------------------------------------------------------------------
# Percentile table
# ---------------------------------------------------------------------------

def salary_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """Return salary percentile table at useful breakpoints."""
    s = df["average_salary_lpa"].dropna()
    pts = [5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99]
    rows = [{"Percentile": f"P{p}", "Salary (LPA)": round(s.quantile(p / 100), 2)} for p in pts]
    return pd.DataFrame(rows)
