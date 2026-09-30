"""
app.py — Entry point for the Indian Job Market Intelligence dashboard.

Run with:  streamlit run app.py
"""

import os
import sys

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Make src/ importable from anywhere
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_loader import load_raw_data, get_dataset_info, DEFAULT_DATA_PATH
from data_cleaning import clean_data
from feature_engineering import engineer_features
from skill_extraction import add_skills_list
from analysis import overview_kpis, jobs_over_time, demand_by_experience
from ui_helpers import (
    inject_css, render_sidebar,
    page_header, section, kpi_row, divider,
    insight_card, apply_chart_style,
    QUAL_COLORS, PRIMARY, ACCENT_GREEN,
    SURFACE, TEXT, MUTED, BORDER,
    LOGO_SVG_LARGE,
)

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Indian Job Market Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Load & cache ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _cached_raw(path: str):
    return load_raw_data(path)


@st.cache_data(show_spinner=False)
def get_clean_data(path: str):
    raw = load_raw_data(path)
    cleaned = clean_data(raw)
    featured = engineer_features(cleaned)
    featured = add_skills_list(featured)
    return featured


# ── Shared sidebar ─────────────────────────────────────────────────────────
data_path = render_sidebar(DEFAULT_DATA_PATH)

# ── Load data ──────────────────────────────────────────────────────────────
with st.spinner("Loading & cleaning dataset…"):
    try:
        df = get_clean_data(data_path)
        st.session_state["df"] = df
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error loading data: {e}")
        st.stop()

# ── Hero ───────────────────────────────────────────────────────────────────
hero_col, logo_col = st.columns([4, 1])
with hero_col:
    st.markdown(
        """
        <div style="padding:1.6rem 0 0.8rem 0;">
            <div style="font-size:0.75rem;color:#4f8ef7;font-weight:600;
                        letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.55rem;">
                IJMI &nbsp;·&nbsp; ANALYTICS PLATFORM &nbsp;·&nbsp; INDIA
            </div>
            <div style="font-size:2.3rem;font-weight:800;color:#f8fafc;line-height:1.15;
                        margin-bottom:0.6rem;letter-spacing:-0.01em;">
                Indian Job Market<br>
                <span style="color:#38bdf8;">Intelligence</span>
            </div>
            <div style="font-size:0.95rem;color:#94a3b8;max-width:560px;line-height:1.65;">
                A professional analytics platform built on&nbsp;<strong style="color:#cbd5e1;">97,682</strong>
                real job postings from Naukri.com. Explore demand trends, salary patterns,
                skill gaps, and career insights&nbsp;&#8212; all in one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with logo_col:
    st.markdown(LOGO_SVG_LARGE, unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────
kpis = overview_kpis(df)
avg_sal = float(kpis["avg_salary_lpa"]) if kpis.get("avg_salary_lpa") is not None else 0.0

kpi_row([
    ("Total Job Postings",    f"{kpis['total_jobs']:,}",      "Cleaned & deduplicated"),
    ("Unique Companies",      f"{kpis['total_companies']:,}", "Hiring across India"),
    ("Locations Covered",     f"{kpis['total_locations']:,}", "Cities & regions"),
    ("Avg Advertised Salary", f"\u20b9{avg_sal:.1f} LPA",     "Where salary disclosed"),
])

divider()

# ── Two-column charts ──────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    section("Job Posting Activity")
    jot = jobs_over_time(df)
    if not jot.empty:
        fig_trend = px.area(
            jot,
            x="days_ago",
            y="job_count",
            color_discrete_sequence=[PRIMARY],
            labels={"days_ago": "Days Ago", "job_count": "Postings"},
        )
        fig_trend.update_traces(
            line_color=PRIMARY,
            fillcolor="rgba(79,142,247,0.14)",
            hovertemplate="<b>%{x} days ago</b><br>%{y:,} postings<extra></extra>",
        )
        fig_trend.update_xaxes(autorange="reversed")
        fig_trend.update_layout(title="How recent are the job postings?")
        st.plotly_chart(apply_chart_style(fig_trend, 295), use_container_width=True)

with col_right:
    section("Experience Distribution")
    exp_df = demand_by_experience(df)
    exp_df = exp_df[exp_df["experience_group"] != "Unknown"]
    if not exp_df.empty:
        fig_exp = px.pie(
            exp_df,
            names="experience_group",
            values="count",
            color_discrete_sequence=QUAL_COLORS,
            hole=0.46,
        )
        fig_exp.update_traces(
            textfont_size=11,
            textfont_color="#e8eaf0",
            marker=dict(line=dict(color="#0f1117", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:,} postings (%{percent})<extra></extra>",
        )
        fig_exp.update_layout(title="How are jobs distributed by seniority?")
        st.plotly_chart(apply_chart_style(fig_exp, 295), use_container_width=True)

divider()

# ── Three-column mini charts ───────────────────────────────────────────────
section("Quick Snapshot")
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:600;color:#8b92a8;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>Top Roles</div>",
        unsafe_allow_html=True,
    )
    top_roles = df["title"].value_counts().head(8).reset_index()
    top_roles.columns = ["title", "count"]
    fig_r = px.bar(
        top_roles.sort_values("count"),
        x="count", y="title",
        orientation="h",
        color_discrete_sequence=[PRIMARY],
        labels={"count": "Postings", "title": ""},
    )
    fig_r.update_traces(marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>")
    st.plotly_chart(apply_chart_style(fig_r, 310), use_container_width=True)

with c2:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:600;color:#8b92a8;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>Top Locations</div>",
        unsafe_allow_html=True,
    )
    top_locs = df["primary_location"].value_counts().head(8).reset_index()
    top_locs.columns = ["primary_location", "count"]
    fig_l = px.bar(
        top_locs.sort_values("count"),
        x="count", y="primary_location",
        orientation="h",
        color_discrete_sequence=[ACCENT_GREEN],
        labels={"count": "Postings", "primary_location": ""},
    )
    fig_l.update_traces(marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>")
    st.plotly_chart(apply_chart_style(fig_l, 310), use_container_width=True)

with c3:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:600;color:#8b92a8;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>Top Skills</div>",
        unsafe_allow_html=True,
    )
    from collections import Counter
    skill_counts = Counter(
        skill.strip()
        for skills in df["skills_list"].dropna()
        for skill in skills
        if skill.strip()
    )
    top_skills_df = pd.DataFrame(skill_counts.most_common(8), columns=["skill", "count"])
    top_skills_df = top_skills_df.sort_values("count")
    fig_s = px.bar(
        top_skills_df,
        x="count", y="skill",
        orientation="h",
        color_discrete_sequence=["#f59e0b"],
        labels={"count": "Mentions", "skill": ""},
    )
    fig_s.update_traces(marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>")
    st.plotly_chart(apply_chart_style(fig_s, 310), use_container_width=True)

divider()

# ── Key Insights ───────────────────────────────────────────────────────────
section("Key Insights")

top_role_name  = df["title"].value_counts().index[0]           if not df.empty else "\u2014"
top_role_count = int(df["title"].value_counts().iloc[0])       if not df.empty else 0
top_city       = df["primary_location"].value_counts().index[0] if not df.empty else "\u2014"
top_city_count = int(df["primary_location"].value_counts().iloc[0]) if not df.empty else 0
fresher_pct    = round(df["is_fresher"].mean() * 100, 1) if "is_fresher" in df.columns else 0
sal_coverage   = round(df["average_salary_lpa"].notna().mean() * 100, 1)

insight_card(
    f"<b>{top_role_name}</b> is the most-posted role with "
    f"<b>{top_role_count:,}</b> listings, accounting for "
    f"{top_role_count / kpis['total_jobs'] * 100:.1f}% of all postings in the dataset.",
    "\U0001f4cc",
)
insight_card(
    f"<b>{top_city}</b> leads hiring with <b>{top_city_count:,}</b> postings, "
    f"making it the #1 city by job volume in the dataset.",
    "\U0001f3d9\ufe0f",
)
insight_card(
    f"<b>{fresher_pct}%</b> of postings require 0 years of minimum experience, "
    f"indicating a meaningful share of entry-level roles in the dataset.",
    "\U0001f331",
)
insight_card(
    f"Salary data is available for <b>{sal_coverage}%</b> of postings. "
    f"The average advertised salary is <b>\u20b9{avg_sal:.1f} LPA</b> across disclosed roles.",
    "\U0001f4b0",
)

divider()

# ── Navigation grid ────────────────────────────────────────────────────────
section("Explore the Dashboard")

pages = [
    ("📊", "Job Market Overview",    "pages/1_Job_Market_Overview.py",  "Jobs, top roles, companies & trends"),
    ("🔍", "Job Demand Analysis",    "pages/2_Job_Demand.py",           "Demanded roles, cities & experience"),
    ("\U0001f9e0", "Skill Intelligence", "pages/3_Skill_Intelligence.py", "Top skills, gaps & co-occurrence"),
    ("💰", "Salary Intelligence",    "pages/4_Salary_Intelligence.py",  "Salary distributions by role & city"),
    ("📈", "Experience Analysis",    "pages/5_Experience_Analysis.py",  "Jobs by seniority & salary trends"),
    ("🌱", "Fresher Opportunities",  "pages/6_Fresher_Jobs.py",         "Entry-level jobs & top companies"),
    ("🏢", "Company & Location",     "pages/7_Company_Location.py",     "Top employers, cities & ratings"),
    ("🔎", "Job Explorer",           "pages/13_Job_Explorer.py",        "Search & filter 97K+ postings"),
    ("\U0001f5c4\ufe0f", "SQL Analytics", "pages/9_SQL_Analytics.py",   "Analytical SQL on in-memory SQLite"),
    ("📐", "Statistical Insights",   "pages/10_Statistical_Insights.py","Descriptive stats & correlations"),
    ("🤖", "Salary Prediction",      "pages/11_Salary_Prediction.py",   "ML model to estimate salary"),
    ("🎯", "Career Skill Gap",       "pages/12_Career_Skill_Gap.py",    "Your skills vs employer demand"),
    ("📁", "Dataset & Quality",      "pages/8_Dataset_Quality.py",      "Data quality & cleaning report"),
]

nav_cols = st.columns(4, gap="small")
for i, (icon, title, page_path, desc) in enumerate(pages):
    nav_cols[i % 4].page_link(
        page_path,
        label=f"{icon} **{title}**",
        help=desc,
    )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='dash-footer'>"
    "<strong style='color:#c4c9d8;'>Indian Job Market Intelligence</strong>"
    "&nbsp;&nbsp;·&nbsp;&nbsp;"
    "Data Analytics Portfolio Project"
    "<br>"
    "Python &nbsp;\u00b7&nbsp; Pandas &nbsp;\u00b7&nbsp; SQL &nbsp;\u00b7&nbsp; "
    "Plotly &nbsp;\u00b7&nbsp; Streamlit &nbsp;\u00b7&nbsp; Scikit-learn"
    "<br>"
    "<span style='opacity:0.6;'>"
    "Dataset represents collected job postings and should not be interpreted "
    "as a complete representation of the entire Indian job market."
    "</span>"
    "</div>",
    unsafe_allow_html=True,
)
