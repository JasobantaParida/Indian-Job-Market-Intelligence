"""
career_analysis.py — Career Skill Gap Analyzer.
Given a target role, identifies the most-requested skills in the dataset
and compares them against a user-supplied skill set.
"""

import pandas as pd
from collections import Counter
from skill_extraction import SKILL_MAP, extract_skills_from_row


# ---------------------------------------------------------------------------
# Supported target roles (mapped from dataset job titles)
# ---------------------------------------------------------------------------

ROLE_KEYWORDS = {
    "Data Analyst": ["data analyst", "data analysis"],
    "Business Analyst": ["business analyst", "business analysis"],
    "Data Scientist": ["data scientist"],
    "Machine Learning Engineer": ["machine learning", "ml engineer"],
    "Data Engineer": ["data engineer"],
    "Software Developer / Engineer": ["software developer", "software engineer", "sde", "swe"],
    "Python Developer": ["python developer", "python engineer"],
    "Java Developer": ["java developer", "java engineer"],
    "Full Stack Developer": ["full stack", "fullstack"],
    "Backend Developer": ["backend developer", "back-end developer"],
    "Frontend Developer": ["frontend developer", "front-end developer", "ui developer"],
    "DevOps Engineer": ["devops", "sre", "site reliability"],
    "Business Development": ["business development"],
    "Sales Executive": ["sales executive", "sales manager"],
    "HR / Recruiter": ["hr executive", "recruiter", "talent acquisition"],
    "Financial Analyst": ["financial analyst", "finance analyst"],
    "Accountant": ["accountant", "accounting"],
    "Project Manager": ["project manager", "program manager"],
}

ALL_CANONICAL_SKILLS = sorted(set(SKILL_MAP.values()))


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def filter_by_role(df: pd.DataFrame, role_name: str) -> pd.DataFrame:
    """Return rows matching the selected role (case-insensitive keyword match)."""
    keywords = ROLE_KEYWORDS.get(role_name, [role_name.lower()])
    pattern = "|".join(keywords)
    return df[df["title"].str.lower().str.contains(pattern, na=False, regex=True)].copy()


def get_role_skill_demand(role_df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    """
    For a role-filtered DataFrame, return the top-n most frequently
    requested canonical skills with counts and percentage.
    """
    all_skills = [skill for skills in role_df["skills_list"] for skill in skills]
    if not all_skills:
        return pd.DataFrame(columns=["skill", "count", "pct_of_postings"])
    total = len(role_df)
    counts = Counter(all_skills)
    top = pd.DataFrame(counts.most_common(top_n), columns=["skill", "count"])
    top["pct_of_postings"] = (top["count"] / total * 100).round(1)
    return top


def skill_gap_analysis(role_df: pd.DataFrame, user_skills: list[str], top_n: int = 25) -> dict:
    """
    Compare user's current skills against what the market demands for a role.

    Returns a dict with:
      - demand   : top-n skill demand DataFrame (skill, count, pct_of_postings)
      - covered  : skills user already has that are in the top-n
      - gaps     : top-n skills the user doesn't have
      - coverage : % of top-n demand skills the user already has
    """
    demand_df = get_role_skill_demand(role_df, top_n=top_n)
    if demand_df.empty:
        return {"demand": demand_df, "covered": [], "gaps": [], "coverage": 0.0}

    demanded_skills = demand_df["skill"].tolist()
    user_set = set(user_skills)

    covered = [s for s in demanded_skills if s in user_set]
    gaps    = [s for s in demanded_skills if s not in user_set]
    coverage = round(len(covered) / len(demanded_skills) * 100, 1)

    return {
        "demand":   demand_df,
        "covered":  covered,
        "gaps":     gaps,
        "coverage": coverage,
    }


def get_common_skill_combos(role_df: pd.DataFrame, top_n_skills: int = 15, top_combos: int = 10) -> pd.DataFrame:
    """
    Return the most common 2-skill pairs for the role
    (limited to top_n_skills to keep computation fast).
    """
    from itertools import combinations

    top_skills = get_role_skill_demand(role_df, top_n_skills)["skill"].tolist()
    top_set    = set(top_skills)
    co: dict   = {}

    for skills in role_df["skills_list"]:
        filtered = sorted([s for s in skills if s in top_set])
        for a, b in combinations(filtered, 2):
            co[(a, b)] = co.get((a, b), 0) + 1

    if not co:
        return pd.DataFrame(columns=["Skill A", "Skill B", "Co-occurrences"])

    rows = [{"Skill A": a, "Skill B": b, "Co-occurrences": c} for (a, b), c in co.items()]
    return pd.DataFrame(rows).sort_values("Co-occurrences", ascending=False).head(top_combos)
