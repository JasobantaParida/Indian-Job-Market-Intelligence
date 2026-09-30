"""
4_Salary_Intelligence.py — Page 4: Salary Intelligence
Answers: What salary ranges exist? How does salary vary by role, city, experience, and skill?
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, hbar, box_plot,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY, ACCENT_GREEN,
)
from analysis import (
    salary_distribution, salary_by_role, salary_by_location,
    salary_by_experience, mean_salary_by,
)
from skill_extraction import get_top_skills

st.set_page_config(page_title="Salary Intelligence", page_icon="💰", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]
sal_df = df.dropna(subset=["average_salary_lpa"])

page_header(
    "💰", "Salary Intelligence",
    "How are advertised salaries structured across roles and locations? — Distributions, role gaps & skill premiums.",
)

st.warning(
    "⚠️ **Salary Disclaimer:** Salary values reflect advertised ranges in job postings (~34% disclosure rate), "
    "not actual paid salaries. These are directional indicators only and may vary by negotiation and employer."
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔧 Filters</div>",
        unsafe_allow_html=True,
    )
    search_role = st.text_input("Search Job Role", placeholder="e.g. Software Engineer")
    all_locs = sorted(df["primary_location"].dropna().unique().tolist())
    sel_locs = st.multiselect("Location", all_locs, placeholder="All locations")
    all_exp = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")
    sal_range = st.slider(
        "Salary Range (LPA)", 0.0, 50.0, (0.0, 50.0), step=0.5
    )
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if search_role:
    fdf = fdf[fdf["title"].str.contains(search_role, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]
if sel_exp:
    fdf = fdf[fdf["experience_group"].isin(sel_exp)]

fdf_sal = fdf.dropna(subset=["average_salary_lpa"])
fdf_sal = fdf_sal[
    (fdf_sal["average_salary_lpa"] >= sal_range[0]) &
    (fdf_sal["average_salary_lpa"] <= sal_range[1])
]

disclosed = len(fdf_sal)
total = len(fdf)

# ── KPIs ───────────────────────────────────────────────────────────────────
section("📌 Salary Summary")
if disclosed > 0:
    min_sal_str = f"₹{fdf_sal['minimumSalary_lpa'].min():.1f} LPA" if "minimumSalary_lpa" in fdf_sal.columns and fdf_sal["minimumSalary_lpa"].notna().any() else "–"
    max_sal_str = f"₹{fdf_sal['maximumSalary_lpa'].max():.1f} LPA" if "maximumSalary_lpa" in fdf_sal.columns and fdf_sal["maximumSalary_lpa"].notna().any() else "–"
    kpi_row([
        ("Jobs with Salary Disclosed", f"{disclosed:,}",                                  f"{disclosed/max(1,total)*100:.0f}% of filtered"),
        ("Average Salary",             f"₹{fdf_sal['average_salary_lpa'].mean():.1f} LPA", "mean"),
        ("Median Salary",              f"₹{fdf_sal['average_salary_lpa'].median():.1f} LPA", "50th percentile"),
        ("Lowest Salary",              min_sal_str,                                        "min disclosed"),
        ("Highest Salary",             max_sal_str,                                        "max (99th pct cap)"),
    ])
else:
    st.warning("No salary data available for the current filters.")

divider()

# ── Section 1: Salary Distribution ────────────────────────────────────────
section("📊 What is the shape of the salary distribution?")

if disclosed > 0:
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(
            fdf_sal,
            x="average_salary_lpa",
            nbins=40,
            labels={"average_salary_lpa": "Average Salary (LPA)"},
            color_discrete_sequence=[PRIMARY],
        )
        fig_hist.update_traces(
            hovertemplate="Salary: ₹%{x:.1f} LPA<br>Count: %{y}<extra></extra>"
        )
        fig_hist.add_vline(
            x=fdf_sal["average_salary_lpa"].mean(),
            line_dash="dash", line_color="#ef4444",
            annotation_text=f"Mean: ₹{fdf_sal['average_salary_lpa'].mean():.1f}",
            annotation_position="top right",
            annotation_font_color="#ef4444",
        )
        fig_hist.add_vline(
            x=fdf_sal["average_salary_lpa"].median(),
            line_dash="dot", line_color="#22c55e",
            annotation_text=f"Median: ₹{fdf_sal['average_salary_lpa'].median():.1f}",
            annotation_position="top left",
            annotation_font_color="#22c55e",
        )
        st.plotly_chart(apply_chart_style(fig_hist, 360), use_container_width=True)

    with c2:
        fig_box = px.box(
            fdf_sal,
            y="average_salary_lpa",
            labels={"average_salary_lpa": "Salary (LPA)"},
            color_discrete_sequence=[PRIMARY],
            points=False,
        )
        fig_box.update_traces(
            hovertemplate="Q1: %{q1:.1f} LPA<br>Median: %{median:.1f} LPA<br>Q3: %{q3:.1f} LPA<extra></extra>"
        )
        st.plotly_chart(apply_chart_style(fig_box, 360), use_container_width=True)
        st.dataframe(
            fdf_sal["average_salary_lpa"].describe().rename("LPA").to_frame().round(2),
            use_container_width=True,
        )

divider()

# ── Section 2: Salary by Role ─────────────────────────────────────────────
section("🏆 Which roles advertise the highest salaries?")

role_sal = salary_by_role(fdf, 15)
if not role_sal.empty:
    fig_role = box_plot(role_sal, "title", "average_salary_lpa",
                        "Salary Distribution by Job Role", height=480)
    fig_role.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_role, use_container_width=True)

    # Also show mean table
    role_mean = (
        role_sal.groupby("title")["average_salary_lpa"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "Avg LPA", "median": "Median LPA", "count": "N"})
        .sort_values("Avg LPA", ascending=False)
        .round(2)
    )
    st.dataframe(role_mean, hide_index=True, use_container_width=True)
else:
    st.info("No salary data for current filters.")

divider()

# ── Section 3: Salary by Location ─────────────────────────────────────────
section("📍 Which cities advertise the highest salaries?")

loc_sal = salary_by_location(fdf, 15)
if not loc_sal.empty:
    fig_loc = box_plot(loc_sal, "primary_location", "average_salary_lpa",
                       "Salary Distribution by City", height=460)
    fig_loc.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_loc, use_container_width=True)

    loc_mean = mean_salary_by(fdf, "primary_location").head(15)
    fig_loc2 = hbar(
        loc_mean.rename(columns={"avg_salary_lpa": "avg_sal"}),
        "avg_sal", "primary_location", "",
        color=SECONDARY, height=420,
        x_label="Avg Salary (LPA)", y_label="City",
    )
    st.plotly_chart(fig_loc2, use_container_width=True)
else:
    st.info("No salary data for current filters.")

divider()

# ── Section 4: Salary by Experience ───────────────────────────────────────
section("📈 How does advertised salary grow with experience?")

exp_sal = salary_by_experience(fdf)
if not exp_sal.empty:
    exp_order = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    exp_sal["exp_order"] = exp_sal["experience_group"].apply(
        lambda x: exp_order.index(x) if x in exp_order else 99
    )
    exp_sal = exp_sal.sort_values("exp_order")

    c3, c4 = st.columns(2)
    with c3:
        fig_exp = box_plot(exp_sal, "experience_group", "average_salary_lpa",
                           "Salary by Experience Level", height=420)
        # Enforce categorical order
        fig_exp.update_xaxes(categoryorder="array", categoryarray=exp_order)
        st.plotly_chart(fig_exp, use_container_width=True)

    with c4:
        exp_agg = (
            exp_sal.groupby("experience_group")["average_salary_lpa"]
            .agg(["mean", "median", "count"])
            .reset_index()
            .rename(columns={"mean": "Avg LPA", "median": "Median LPA", "count": "N"})
            .round(2)
        )
        exp_agg["exp_order"] = exp_agg["experience_group"].apply(
            lambda x: exp_order.index(x) if x in exp_order else 99
        )
        exp_agg = exp_agg.sort_values("exp_order").drop(columns="exp_order")
        st.dataframe(exp_agg, hide_index=True, use_container_width=True)
else:
    st.info("No salary-vs-experience data available.")

divider()

# ── Section 5: Salary by Skill ────────────────────────────────────────────
section("🛠️ Which skills are associated with higher-advertised salaries?")

_sal_src = fdf.dropna(subset=["average_salary_lpa", "skills_list"])
skill_sal_rows = []
for _, row in _sal_src[["skills_list", "average_salary_lpa"]].iterrows():
    if isinstance(row["skills_list"], list):
        for skill in row["skills_list"]:
            skill_sal_rows.append({"skill": skill, "average_salary_lpa": row["average_salary_lpa"]})

if skill_sal_rows:
    skill_sal_df = pd.DataFrame(skill_sal_rows)
    top_skills = get_top_skills(fdf, 20)["skill"].tolist()
    skill_sal_df = skill_sal_df[skill_sal_df["skill"].isin(top_skills)]

    skill_agg = (
        skill_sal_df.groupby("skill")["average_salary_lpa"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "Avg LPA", "median": "Median LPA", "count": "N"})
        .sort_values("Avg LPA", ascending=False)
        .round(2)
    )
    c5, c6 = st.columns([2, 1])
    with c5:
        fig_skill = hbar(
            skill_agg.rename(columns={"Avg LPA": "avg_sal"}),
            "avg_sal", "skill", "",
            color=ACCENT_GREEN, height=480,
            x_label="Average Salary (LPA)", y_label="Skill",
        )
        st.plotly_chart(fig_skill, use_container_width=True)
    with c6:
        st.dataframe(skill_agg, hide_index=True, use_container_width=True)
else:
    st.info("Not enough skill-salary data for current filters.")

divider()

# ── Download ───────────────────────────────────────────────────────────────
export_cols = ["title", "companyName", "primary_location", "experience_group",
               "minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa", "tagsAndSkills"]
download_csv_button(
    fdf_sal[[c for c in export_cols if c in fdf_sal.columns]],
    key="salary_dl"
)
