"""
skill_extraction.py — Parses the comma-separated tagsAndSkills column and
maps raw skill strings to canonical technology names.
"""

import re
from collections import Counter
from itertools import combinations

import pandas as pd

# ---------------------------------------------------------------------------
# Canonical skill map  (raw substring → display name)
# Longer / more-specific patterns should appear before shorter ones.
# ---------------------------------------------------------------------------

SKILL_MAP = {
    # Data & Analytics
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language": "NLP",
    "nlp": "NLP",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analytics",
    "data science": "Data Science",
    "data engineering": "Data Engineering",
    "data visualization": "Data Visualization",
    "data visualisation": "Data Visualization",
    "business intelligence": "Business Intelligence",
    "business analytics": "Business Analytics",
    "statistical analysis": "Statistical Analysis",
    "statistics": "Statistics",
    "predictive": "Predictive Modeling",
    # Languages
    "python": "Python",
    "r programming": "R",
    " r ": "R",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "c#": "C#",
    "scala": "Scala",
    "go lang": "Go",
    "golang": "Go",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "php": "PHP",
    "ruby": "Ruby",
    "perl": "Perl",
    "shell": "Shell/Bash",
    "bash": "Shell/Bash",
    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "oracle": "Oracle DB",
    "mongodb": "MongoDB",
    "nosql": "NoSQL",
    "cassandra": "Cassandra",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "hadoop": "Hadoop",
    "hive": "Hive",
    "spark": "Apache Spark",
    # Cloud
    "aws": "AWS",
    "amazon web": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    # BI Tools
    "power bi": "Power BI",
    "tableau": "Tableau",
    "looker": "Looker",
    "qlik": "Qlik",
    "excel": "Excel",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    # ML Libraries
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "keras": "Keras",
    "xgboost": "XGBoost",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    # DevOps / Infra
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "jenkins": "Jenkins",
    "git": "Git",
    "ci/cd": "CI/CD",
    "terraform": "Terraform",
    "ansible": "Ansible",
    # Web / APIs
    "react": "React",
    "angular": "Angular",
    "vue": "Vue.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "rest api": "REST API",
    "restful": "REST API",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    # General / Soft
    "communication": "Communication",
    "leadership": "Leadership",
    "project management": "Project Management",
    "agile": "Agile",
    "scrum": "Scrum",
    "teamwork": "Teamwork",
    "problem solving": "Problem Solving",
    "analytical": "Analytical Skills",
    "ms office": "MS Office",
    "microsoft office": "MS Office",
    "salesforce": "Salesforce",
    "erp": "ERP",
    "sap": "SAP",
}


def _normalize(text: str) -> str:
    return text.lower().strip()


def extract_skills_from_row(raw: str) -> list[str]:
    """
    Parse a comma-separated tagsAndSkills cell and return a list of
    canonical skill names (deduplicated, in insertion order).
    """
    if not isinstance(raw, str) or raw.strip() == "":
        return []

    tokens = [t.strip() for t in raw.split(",")]
    found = []
    seen = set()
    for token in tokens:
        norm = _normalize(token)
        for pattern, canonical in SKILL_MAP.items():
            if pattern in norm and canonical not in seen:
                found.append(canonical)
                seen.add(canonical)
                break
    return found


def add_skills_list(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'skills_list' column (list of canonical skills per row)."""
    df = df.copy()
    df["skills_list"] = df["tagsAndSkills"].apply(extract_skills_from_row)
    return df


def get_top_skills(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    """
    Explode skills_list and return the top-n most frequent skills with counts.
    """
    all_skills = [skill for skills in df["skills_list"] for skill in skills]
    counts = Counter(all_skills)
    top = pd.DataFrame(counts.most_common(n), columns=["skill", "count"])
    return top


def get_skill_by_column(df: pd.DataFrame, col: str, n_skills: int = 15) -> pd.DataFrame:
    """
    Return a pivot-style DataFrame: skill vs. category (col values) with counts.
    Useful for skill vs. job role, skill vs. experience, etc.
    """
    rows = []
    for _, row in df[[col, "skills_list"]].dropna(subset=[col]).iterrows():
        for skill in row["skills_list"]:
            rows.append({"category": row[col], "skill": skill})
    if not rows:
        return pd.DataFrame(columns=["category", "skill", "count"])
    result = (
        pd.DataFrame(rows)
        .groupby(["category", "skill"])
        .size()
        .reset_index(name="count")
    )
    # Keep only top skills overall for readability
    top_skills = get_top_skills(df, n_skills)["skill"].tolist()
    result = result[result["skill"].isin(top_skills)]
    return result


def get_skill_cooccurrence(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Return a co-occurrence matrix for the top-n skills.
    """
    top_skills = set(get_top_skills(df, top_n)["skill"].tolist())
    co: dict = {}
    for skills in df["skills_list"]:
        filtered = [s for s in skills if s in top_skills]
        for a, b in combinations(sorted(filtered), 2):
            key = (a, b)
            co[key] = co.get(key, 0) + 1
    if not co:
        return pd.DataFrame(columns=["skill_a", "skill_b", "count"])
    rows = [{"skill_a": a, "skill_b": b, "count": c} for (a, b), c in co.items()]
    return pd.DataFrame(rows).sort_values("count", ascending=False)
