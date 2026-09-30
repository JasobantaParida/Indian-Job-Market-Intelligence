"""
9_SQL_Analytics.py — Page 9: SQL Analytics
Run practical analytical SQL queries against an in-memory SQLite database.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, divider, hbar,
    apply_chart_style, download_csv_button, PRIMARY,
)
from sql_analysis import build_sqlite_connection, QUERIES, run_query

st.set_page_config(page_title="SQL Analytics", page_icon="🗄️", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🗄️", "SQL Analytics",
    "Explore job market patterns through structured SQL queries against an in-memory SQLite database.",
)
divider()

# ── Cached SQLite connection ───────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _get_conn(_df, df_hash: int):
    """Cache key is df_hash; _df is prefixed so Streamlit skips hashing the DataFrame."""
    return build_sqlite_connection(_df)


# ── Build SQLite connection ────────────────────────────────────────────────
with st.spinner("Preparing SQL database\u2026"):
    df_hash = hash(len(df))
    conn = _get_conn(df, df_hash)

st.success(
    "\u2705 In-memory SQLite database ready with **97,682 clean job records**.",
    icon="\U0001f5c4\ufe0f",
)
divider()

# ── Query selector ─────────────────────────────────────────────────────────
section("📋 Pre-built Analytical Queries")
st.caption("Select a query to see the business question, SQL code, and results.")

query_name = st.selectbox(
    "Choose a query",
    options=list(QUERIES.keys()),
    help="Select from 12 analytical queries covering demand, salary, skills, and more.",
)

query_data = QUERIES[query_name]

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("**\U0001f4a1 Business Question**")
    st.info(query_data["question"])

with col2:
    st.markdown("**\U0001f4dd SQL Query**")
    st.code(query_data["sql"], language="sql")

# ── Execute & display ──────────────────────────────────────────────────────
with st.spinner("Running query\u2026"):
    result_df = run_query(conn, query_data["sql"])

st.markdown(f"**Results \u2014 {len(result_df):,} rows returned**")

if "Error" in result_df.columns:
    st.error(f"Query error: {result_df['Error'].iloc[0]}")
elif result_df.empty:
    st.info("No rows returned by this query.")
else:
    st.dataframe(result_df, use_container_width=True, hide_index=True)
    download_csv_button(result_df, label=f"Download '{query_name}' results as CSV", key="sql_dl")

    # Auto-visualize simple 2-column results
    if len(result_df.columns) == 2 and len(result_df) >= 3:
        col_names = result_df.columns.tolist()
        x_col, y_col = col_names[1], col_names[0]
        try:
            fig = hbar(
                result_df.head(20),
                x_col=x_col, y_col=y_col,
                title=query_name,
                color=PRIMARY,
                height=max(300, min(len(result_df), 20) * 28),
                x_label=x_col, y_label=y_col,
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass  # Silently skip chart if columns aren't numeric

divider()

# ── Custom SQL editor ──────────────────────────────────────────────────────
section("\u270f\ufe0f Custom SQL Query")
st.caption(
    "Write your own SQL against the `jobs` table. "
    "Available columns: title, companyName, primary_location, experience_group, "
    "minimumExperience, maximumExperience, average_experience, "
    "minimumSalary_lpa, maximumSalary_lpa, average_salary_lpa, "
    "tagsAndSkills, AggregateRating, ReviewsCount, days_ago, is_fresher"
)

default_sql = """\
SELECT   primary_location,
         COUNT(*)                             AS total_jobs,
         ROUND(AVG(average_salary_lpa), 2)   AS avg_salary_lpa
FROM     jobs
WHERE    average_salary_lpa IS NOT NULL
GROUP BY primary_location
HAVING   total_jobs >= 50
ORDER BY avg_salary_lpa DESC
LIMIT    10;"""

custom_sql = st.text_area("SQL", value=default_sql, height=180, key="custom_sql")

if st.button("\u25b6\ufe0f Run Query", type="primary"):
    with st.spinner("Running\u2026"):
        custom_result = run_query(conn, custom_sql)
    if "Error" in custom_result.columns:
        st.error(f"SQL error: {custom_result['Error'].iloc[0]}")
    elif custom_result.empty:
        st.info("Query returned no rows.")
    else:
        st.dataframe(custom_result, use_container_width=True, hide_index=True)
        download_csv_button(custom_result, label="Download custom query results", key="custom_dl")

divider()

# ── Table schema reference ─────────────────────────────────────────────────
with st.expander("\U0001f4d6 Table Schema Reference"):
    schema = pd.DataFrame({
        "Column": [
            "title", "companyName", "primary_location", "experience_group",
            "minimumExperience", "maximumExperience", "average_experience",
            "minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa",
            "tagsAndSkills", "AggregateRating", "ReviewsCount", "days_ago", "is_fresher",
        ],
        "Type": [
            "TEXT", "TEXT", "TEXT", "TEXT",
            "REAL", "REAL", "REAL",
            "REAL", "REAL", "REAL",
            "TEXT", "REAL", "REAL", "REAL", "INTEGER",
        ],
        "Description": [
            "Job title / role name",
            "Employer company name",
            "Primary city (extracted from location string)",
            "Experience bucket: Fresher (0 Yrs) / 0\u20132 Yrs / 2\u20135 Yrs / 5\u20138 Yrs / 8+ Yrs",
            "Minimum years experience required",
            "Maximum years experience required",
            "Average of min/max experience",
            "Minimum salary in Lakhs Per Annum (LPA)",
            "Maximum salary in Lakhs Per Annum (LPA)",
            "Average salary in LPA \u2014 NULL if undisclosed",
            "Comma-separated skills / tags from job posting",
            "Company rating (1\u20135) \u2014 NULL if unavailable",
            "Number of company reviews \u2014 NULL if unavailable",
            "Days since job was posted (0=today) \u2014 NULL if unknown",
            "1 if minimumExperience = 0 (entry-level), else 0",
        ],
    })
    st.dataframe(schema, hide_index=True, use_container_width=True)
