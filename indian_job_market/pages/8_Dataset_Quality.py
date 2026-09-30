"""
8_Dataset_Quality.py — Page 8: Dataset & Data Quality
Shows raw dataset statistics, missing value analysis, and data quality metrics.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider,
    apply_chart_style, PRIMARY, SECONDARY, ACCENT_GREEN,
)
from data_loader import load_raw_data, get_dataset_info, DEFAULT_DATA_PATH

st.set_page_config(page_title="Dataset & Data Quality", page_icon="📁", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]  # cleaned df

page_header(
    "📁", "Dataset & Data Quality",
    "Professional data quality report — how was the raw data loaded, cleaned, and prepared for analysis?",
)
divider()

# ── Load raw for comparison ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_raw_info(path: str) -> tuple:
    raw = load_raw_data(path)
    info = get_dataset_info(raw)
    return raw, info

try:
    raw_df, raw_info = load_raw_info(DEFAULT_DATA_PATH)
except Exception:
    raw_df = df
    raw_info = {"rows": len(df), "columns": len(df.columns), "null_counts": {}, "dtypes": {}, "duplicates": 0}

# ── KPIs ───────────────────────────────────────────────────────────────────
section("📌 Dataset Summary")

sal_count   = df["average_salary_lpa"].notna().sum()
exp_count   = df["minimumExperience"].notna().sum()
skill_count = df["tagsAndSkills"].notna().sum()

kpi_row([
    ("Raw Rows",           f"{raw_info['rows']:,}",       "before cleaning"),
    ("Clean Rows",         f"{len(df):,}",                "after deduplication"),
    ("Duplicates Removed", f"{raw_info['duplicates']:,}", "exact duplicate rows"),
    ("Columns",            str(raw_info["columns"]),      "original dataset"),
    ("Companies",          f"{df['companyName'].nunique():,}", "unique employers"),
    ("Locations",          f"{df['primary_location'].nunique():,}", "unique cities"),
])

st.markdown("<br>", unsafe_allow_html=True)
kpi_row([
    ("Salary Records",    f"{sal_count:,}",   f"{sal_count/len(df)*100:.1f}% of clean rows"),
    ("Experience Records",f"{exp_count:,}",   f"{exp_count/len(df)*100:.1f}% of clean rows"),
    ("Skill Records",     f"{skill_count:,}", f"{skill_count/len(df)*100:.1f}% of clean rows"),
    ("Avg Job Rating",    f"{df['AggregateRating'].notna().sum():,}",
                          f"{df['AggregateRating'].notna().sum()/len(df)*100:.1f}% have ratings"),
])

divider()

# ── Missing Value Table ────────────────────────────────────────────────────
section("🔍 Missing Value Analysis (Raw Dataset)")
st.caption("Null counts per column in the raw dataset before any cleaning.")

null_df = pd.DataFrame({
    "Column": list(raw_info["null_counts"].keys()),
    "Null Count": list(raw_info["null_counts"].values()),
    "Data Type": [raw_info["dtypes"].get(c, "?") for c in raw_info["null_counts"].keys()],
})
null_df["% Missing"] = (null_df["Null Count"] / raw_info["rows"] * 100).round(1)
null_df["Status"] = null_df["% Missing"].apply(
    lambda x: "\u2705 Complete" if x == 0 else ("\u26a0\ufe0f Partial" if x < 50 else "\u274c Mostly Missing")
)
null_df = null_df.sort_values("% Missing", ascending=False)

c1, c2 = st.columns([2, 3])
with c1:
    st.dataframe(null_df, hide_index=True, use_container_width=True)
with c2:
    fig = px.bar(
        null_df[null_df["Null Count"] > 0].sort_values("% Missing"),
        x="% Missing",
        y="Column",
        orientation="h",
        color="% Missing",
        color_continuous_scale="Reds",
        labels={"% Missing": "% Missing", "Column": "Column"},
        title="Missing Data by Column (%)",
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    st.plotly_chart(apply_chart_style(fig, 380), use_container_width=True)

divider()

# ── Column Data Types ──────────────────────────────────────────────────────
section("🗂️ Column Data Types (Raw Dataset)")
dtype_df = pd.DataFrame({
    "Column": list(raw_info["dtypes"].keys()),
    "Data Type": list(raw_info["dtypes"].values()),
})
st.dataframe(dtype_df, hide_index=True, use_container_width=True)

divider()

# ── Numeric Summary ────────────────────────────────────────────────────────
section("📊 Numeric Column Summary (Cleaned Data)")
st.caption("Descriptive statistics on key numeric columns after cleaning.")

num_cols = ["minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa",
            "minimumExperience", "maximumExperience", "AggregateRating"]
available = [c for c in num_cols if c in df.columns]
st.dataframe(df[available].describe().round(2).T, use_container_width=True)

divider()

# ── Salary Data Quality ────────────────────────────────────────────────────
section("💰 Salary Data Quality")
sal_disclosed = df["average_salary_lpa"].notna().sum()
sal_zero_raw  = (raw_df["minimumSalary"] == 0).sum() if "minimumSalary" in raw_df.columns else 0

c3, c4 = st.columns(2)
with c3:
    st.markdown("**Salary Disclosure Rate**")
    sal_pie = pd.DataFrame({
        "Status": ["Disclosed", "Not Disclosed"],
        "Count": [sal_disclosed, len(df) - sal_disclosed],
    })
    fig2 = px.pie(
        sal_pie, names="Status", values="Count",
        color_discrete_sequence=[PRIMARY, "#2d3348"],
        hole=0.4,
    )
    fig2.update_traces(
        textinfo="percent+label",
        textfont_color="#e8eaf0",
        marker=dict(line=dict(color="#0f1117", width=2)),
    )
    st.plotly_chart(apply_chart_style(fig2, 300), use_container_width=True)
with c4:
    st.markdown("**Salary Quality Notes**")
    st.info(
        f"""
- **{sal_zero_raw:,}** rows had `minimumSalary = 0` in the raw dataset — treated as undisclosed (\u2192 NaN)
- **USD salaries** were converted to INR using a fixed rate of \u20b983/USD
- The 99th percentile cap was applied to remove extreme outliers
- Salary shown in **Lakhs Per Annum (LPA)** = original INR \u00f7 100,000
- After cleaning: **{sal_disclosed:,}** rows have salary data ({sal_disclosed/len(df)*100:.1f}%)
        """
    )

divider()

# ── Experience Data Quality ────────────────────────────────────────────────
section("🎓 Experience Data Quality")
exp_disclosed = df["minimumExperience"].notna().sum()

c5, c6 = st.columns(2)
with c5:
    st.markdown("**Experience Group Distribution**")
    exp_counts = df["experience_group"].value_counts().reset_index()
    fig3 = px.bar(
        exp_counts.sort_values("count"),
        x="count", y="experience_group",
        orientation="h",
        color_discrete_sequence=[SECONDARY],
        labels={"count": "Postings", "experience_group": "Experience Group"},
    )
    st.plotly_chart(apply_chart_style(fig3, 300), use_container_width=True)
with c6:
    st.markdown("**Experience Quality Notes**")
    st.info(
        f"""
- `minimumExperience = 0` AND `maximumExperience = 0` was treated as undisclosed (\u2192 NaN)
- **{exp_disclosed:,}** rows have experience data ({exp_disclosed/len(df)*100:.1f}%)
- Experience groups are derived from `minimumExperience` using fixed bins:
  - Fresher: 0 years, 0\u20132 Yrs, 2\u20135 Yrs, 5\u20138 Yrs, 8+ Yrs
- **{(df['experience_group']=='Fresher (0 Yrs)').sum():,}** fresher postings
        """
    )

divider()

# ── Methodology ────────────────────────────────────────────────────────────
section("🔬 Data Cleaning Methodology")
st.markdown(
    """
    The following steps were applied to the raw dataset before analysis:

    1. **Duplicate removal** — exact duplicate rows were identified and dropped
    2. **Salary normalization** — `minimumSalary = 0` treated as undisclosed; USD amounts converted to INR (\u20b983 fixed rate); values divided by 100,000 to get LPA
    3. **99th percentile cap** — applied to `average_salary_lpa` to remove extreme outliers
    4. **Experience grouping** — `minimumExperience` bucketed into Fresher / 0\u20132 / 2\u20135 / 5\u20138 / 8+ Yrs
    5. **Location extraction** — `primary_location` parsed from raw location strings
    6. **Skill parsing** — `tagsAndSkills` split and canonicalized into `skills_list`
    7. **Fresher flag** — `is_fresher = True` where `minimumExperience == 0`
    """
)

divider()

# ── Dataset Disclaimer ─────────────────────────────────────────────────────
section("\u26a0\ufe0f Dataset Disclaimer")
st.warning(
    "**Insights in this application describe patterns within the provided job-posting dataset "
    "and should not be interpreted as a complete representation of the entire Indian job market.**\n\n"
    "- Data was scraped from Naukri.com and may not cover all job portals or industries.\n"
    "- Salary values are disclosed for approximately 34% of postings and may reflect employer preferences, not actual paid salaries.\n"
    "- Relative posting times (e.g. '4 Days Ago') are not absolute dates and cannot be used to derive posting volumes over real calendar periods.\n"
    "- USD-to-INR conversion uses a fixed rate (\u20b983) and does not account for exchange rate fluctuations.\n"
    "- Duplicate postings (247 removed) may mean some companies posted the same role multiple times."
)
