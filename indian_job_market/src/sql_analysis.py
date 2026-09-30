"""
sql_analysis.py — Loads the cleaned DataFrame into an in-memory SQLite
database and provides ready-to-run analytical queries.

NOTE: No Streamlit imports here. The page (9_SQL_Analytics.py) applies
@st.cache_resource so this module stays import-safe.
"""

import sqlite3
import statistics
import pandas as pd


class _MedianAgg:
    """SQLite aggregate function that computes the median."""
    def __init__(self):
        self._vals = []
    def step(self, value):
        if value is not None:
            self._vals.append(value)
    def finalize(self):
        if not self._vals:
            return None
        return statistics.median(self._vals)


def build_sqlite_connection(df: pd.DataFrame) -> sqlite3.Connection:
    """
    Create an in-memory SQLite database from the cleaned DataFrame.
    Pure function — no Streamlit dependency. Callers apply caching.
    Registers a custom MEDIAN aggregate function.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.create_aggregate("MEDIAN", 1, _MedianAgg)

    # Write only the columns we actually need to keep memory low
    cols = [
        "title", "companyName", "primary_location", "experience_group",
        "minimumExperience", "maximumExperience", "average_experience",
        "minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa",
        "tagsAndSkills", "AggregateRating", "ReviewsCount",
        "days_ago", "is_fresher", "currency",
    ]
    existing = [c for c in cols if c in df.columns]
    df[existing].to_sql("jobs", conn, if_exists="replace", index=False)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Pre-defined analytical queries
# ---------------------------------------------------------------------------

QUERIES = {
    "1. Top 10 Job Roles by Postings": {
        "sql": """\
SELECT title,
       COUNT(*) AS job_count
FROM   jobs
GROUP  BY title
ORDER  BY job_count DESC
LIMIT  10;""",
        "question": "Which job roles appear most frequently in the dataset?",
    },

    "2. Top 10 Companies by Postings": {
        "sql": """\
SELECT companyName,
       COUNT(*) AS job_count
FROM   jobs
GROUP  BY companyName
ORDER  BY job_count DESC
LIMIT  10;""",
        "question": "Which employers are posting the highest number of jobs?",
    },

    "3. Top 10 Locations by Postings": {
        "sql": """\
SELECT primary_location,
       COUNT(*) AS job_count
FROM   jobs
GROUP  BY primary_location
ORDER  BY job_count DESC
LIMIT  10;""",
        "question": "Which cities have the highest concentration of job postings?",
    },

    "4. Average Salary by Location (Top 15)": {
        "sql": """\
SELECT primary_location,
       ROUND(AVG(average_salary_lpa), 2) AS avg_salary_lpa,
       COUNT(*)                          AS total_jobs,
       COUNT(average_salary_lpa)         AS jobs_with_salary,
       ROUND(MIN(average_salary_lpa), 2) AS min_salary_lpa,
       ROUND(MAX(average_salary_lpa), 2) AS max_salary_lpa
FROM   jobs
WHERE  average_salary_lpa IS NOT NULL
GROUP  BY primary_location
HAVING COUNT(average_salary_lpa) >= 10
ORDER  BY avg_salary_lpa DESC
LIMIT  15;""",
        "question": "Which cities offer the highest average salaries (where salary was disclosed)?",
    },

    "5. Average Salary by Experience Group": {
        "sql": """\
SELECT experience_group,
       ROUND(AVG(average_salary_lpa), 2) AS avg_salary_lpa,
       COUNT(*)                          AS total_jobs,
       COUNT(average_salary_lpa)         AS jobs_with_salary,
       ROUND(MIN(average_salary_lpa), 2) AS min_salary_lpa,
       ROUND(MAX(average_salary_lpa), 2) AS max_salary_lpa
FROM   jobs
WHERE  experience_group NOT IN ('Unknown')
  AND  average_salary_lpa IS NOT NULL
GROUP  BY experience_group
ORDER  BY avg_salary_lpa DESC;""",
        "question": "How does average salary vary across experience levels?",
    },

    "6. Jobs Requiring Python": {
        "sql": """\
SELECT title,
       companyName,
       primary_location,
       experience_group,
       average_salary_lpa
FROM   jobs
WHERE  LOWER(tagsAndSkills) LIKE '%python%'
ORDER  BY average_salary_lpa DESC NULLS LAST
LIMIT  50;""",
        "question": "Which Python job openings are available and what salaries do they offer?",
    },

    "7. Jobs Requiring SQL": {
        "sql": """\
SELECT title,
       companyName,
       primary_location,
       experience_group,
       average_salary_lpa
FROM   jobs
WHERE  LOWER(tagsAndSkills) LIKE '%sql%'
ORDER  BY average_salary_lpa DESC NULLS LAST
LIMIT  50;""",
        "question": "Which SQL-related job openings are available?",
    },

    "8. Jobs Mentioning Both Python & SQL": {
        "sql": """\
SELECT title,
       companyName,
       primary_location,
       experience_group,
       average_salary_lpa
FROM   jobs
WHERE  LOWER(tagsAndSkills) LIKE '%python%'
  AND  LOWER(tagsAndSkills) LIKE '%sql%'
ORDER  BY average_salary_lpa DESC NULLS LAST
LIMIT  50;""",
        "question": "Which roles require both Python and SQL — the core data analyst skill stack?",
    },

    "9. Top Companies for Fresher Roles": {
        "sql": """\
SELECT companyName,
       COUNT(*)                          AS fresher_jobs,
       ROUND(AVG(average_salary_lpa), 2) AS avg_salary_lpa
FROM   jobs
WHERE  is_fresher = 1
GROUP  BY companyName
HAVING fresher_jobs >= 5
ORDER  BY fresher_jobs DESC
LIMIT  20;""",
        "question": "Which companies hire the most entry-level/fresher candidates?",
    },

    "10. Fresher Jobs by Location": {
        "sql": """\
SELECT primary_location,
       COUNT(*) AS fresher_jobs
FROM   jobs
WHERE  is_fresher = 1
GROUP  BY primary_location
ORDER  BY fresher_jobs DESC
LIMIT  15;""",
        "question": "Which cities have the most fresher/entry-level opportunities?",
    },

    "11. Salary Comparison Across Experience Groups (CTE)": {
        "sql": """\
WITH salary_stats AS (
    SELECT experience_group,
           COUNT(*)                          AS total_jobs,
           COUNT(average_salary_lpa)         AS salary_disclosed,
           ROUND(AVG(average_salary_lpa), 2) AS avg_lpa,
           ROUND(MIN(average_salary_lpa), 2) AS min_lpa,
           ROUND(MAX(average_salary_lpa), 2) AS max_lpa
    FROM   jobs
    WHERE  experience_group NOT IN ('Unknown')
    GROUP  BY experience_group
)
SELECT *,
       ROUND(CAST(salary_disclosed AS FLOAT) / total_jobs * 100, 1) AS pct_disclosed
FROM   salary_stats
ORDER  BY avg_lpa DESC;""",
        "question": "Comprehensive salary statistics by experience level including disclosure rates.",
    },

    "12. Top Roles With Highest Average Salary": {
        "sql": """\
WITH role_stats AS (
    SELECT title,
           COUNT(*)                          AS total_jobs,
           COUNT(average_salary_lpa)         AS salary_count,
           ROUND(AVG(average_salary_lpa), 2) AS avg_salary_lpa,
           ROUND(MIN(average_salary_lpa), 2) AS min_salary_lpa,
           ROUND(MAX(average_salary_lpa), 2) AS max_salary_lpa
    FROM   jobs
    WHERE  average_salary_lpa IS NOT NULL
    GROUP  BY title
    HAVING salary_count >= 10
)
SELECT *
FROM   role_stats
ORDER  BY avg_salary_lpa DESC
LIMIT  20;""",
        "question": "Which job roles command the highest average salaries (minimum 10 postings with salary)?",
    },
}


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a DataFrame."""
    try:
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})
