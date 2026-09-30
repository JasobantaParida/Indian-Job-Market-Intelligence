"""
5_Experience_Analysis.py — Page 5: Experience Analysis
Answers: How are job requirements distributed across experience levels?
How do salaries and required skills vary with seniority?
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, hbar, vbar,
    box_plot, apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY,
)
from analysis import demand_by_experience, roles_by_experience, salary_by_experience
from skill_extraction import get_skill_by_column

st.set_page_config(page_title="Experience Analysis", page_icon="📈", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

EXP_ORDER = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]

page_header(
    "📈", "Experience Analysis",
    "How do employers structure experience requirements? — Jobs, salaries & skills by seniority level.",
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
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if search_role:
    fdf = fdf[fdf["title"].str.contains(search_role, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]

# ── KPIs per experience level ─────────────────────────────────────────────
section("📌 Jobs by Experience Level")

exp_df = demand_by_experience(fdf)
exp_known = exp_df[exp_df["experience_group"].isin(EXP_ORDER)]

if not exp_known.empty:
    kpi_row([
        (row["experience_group"], f"{row['count']:,}", "postings")
        for _, row in exp_known.iterrows()
    ])

divider()

# ── Bar chart: jobs by experience ─────────────────────────────────────────
section("📊 How many postings are in each experience bracket?")
c1, c2 = st.columns([2, 1])
with c1:
    exp_plot = exp_known.copy()
    exp_plot["sort"] = exp_plot["experience_group"].apply(
        lambda x: EXP_ORDER.index(x) if x in EXP_ORDER else 99
    )
    exp_plot = exp_plot.sort_values("sort")
    fig1 = px.bar(
        exp_plot,
        x="experience_group",
        y="count",
        color="experience_group",
        color_discrete_sequence=QUAL_COLORS,
        labels={"experience_group": "Experience Level", "count": "Number of Postings"},
        category_orders={"experience_group": EXP_ORDER},
    )
    fig1.update_traces(marker_line_width=0, showlegend=False)
    st.plotly_chart(apply_chart_style(fig1, 380), use_container_width=True)

with c2:
    st.dataframe(
        exp_plot[["experience_group", "count"]]
        .rename(columns={"experience_group": "Level", "count": "Postings"})
        .assign(Share=lambda d: (d["Postings"] / d["Postings"].sum() * 100).round(1)),
        hide_index=True,
        use_container_width=True,
    )

divider()

# ── Salary by Experience ───────────────────────────────────────────────────
section("💰 How does salary grow with seniority?")

exp_sal = salary_by_experience(fdf)
if not exp_sal.empty:
    exp_sal["sort"] = exp_sal["experience_group"].apply(
        lambda x: EXP_ORDER.index(x) if x in EXP_ORDER else 99
    )
    exp_sal = exp_sal.sort_values("sort")

    exp_agg = (
        exp_sal.groupby("experience_group")["average_salary_lpa"]
        .agg(["mean", "median"])
        .reset_index()
        .rename(columns={"mean": "Mean LPA", "median": "Median LPA"})
    )
    exp_agg["_sort"] = exp_agg["experience_group"].apply(
        lambda x: EXP_ORDER.index(x) if x in EXP_ORDER else 99
    )
    exp_agg = exp_agg.sort_values("_sort").drop(columns="_sort")

    c3, c4 = st.columns([3, 2])
    with c3:
        fig_sal = px.bar(
            exp_agg.melt(id_vars="experience_group", value_vars=["Mean LPA", "Median LPA"]),
            x="experience_group",
            y="value",
            color="variable",
            barmode="group",
            color_discrete_sequence=[PRIMARY, SECONDARY],
            labels={"experience_group": "Level", "value": "Salary (LPA)", "variable": ""},
            category_orders={"experience_group": EXP_ORDER},
        )
        fig_sal.update_traces(marker_line_width=0)
        st.plotly_chart(apply_chart_style(fig_sal, 380), use_container_width=True)

    with c4:
        c4_box = box_plot(exp_sal, "experience_group", "average_salary_lpa",
                          "Salary Distribution", height=380)
        c4_box.update_xaxes(categoryorder="array", categoryarray=EXP_ORDER, tickangle=-30)
        st.plotly_chart(c4_box, use_container_width=True)
else:
    st.info("No salary data available for current filters.")

divider()

# ── Top Roles by Experience ────────────────────────────────────────────────
section("🎯 Which roles dominate each experience bracket?")

for exp_level in EXP_ORDER:
    sub = fdf[fdf["experience_group"] == exp_level]
    if len(sub) < 5:
        continue
    with st.expander(f"**{exp_level}** — {len(sub):,} postings", expanded=(exp_level == "0\u20132 Yrs")):
        top = sub["title"].value_counts().head(10).reset_index()
        top.columns = ["title", "count"]
        fig = hbar(top, "count", "title", "",
                   color=QUAL_COLORS[EXP_ORDER.index(exp_level)], height=320,
                   x_label="Postings", y_label="Role")
        st.plotly_chart(fig, use_container_width=True)

divider()

# ── Skills by Experience ───────────────────────────────────────────────────
section("🛠️ What skills must you demonstrate at each career stage?")

exp_skill = get_skill_by_column(
    fdf[fdf["experience_group"].isin(EXP_ORDER)], "experience_group", n_skills=15
)

if not exp_skill.empty:
    exp_skill["sort"] = exp_skill["category"].apply(
        lambda x: EXP_ORDER.index(x) if x in EXP_ORDER else 99
    )
    exp_skill = exp_skill.sort_values("sort")

    fig_sk = px.bar(
        exp_skill,
        x="count",
        y="skill",
        color="category",
        barmode="group",
        orientation="h",
        labels={"count": "Job Postings", "skill": "Skill", "category": "Experience Level"},
        color_discrete_sequence=QUAL_COLORS,
        category_orders={"category": EXP_ORDER},
    )
    fig_sk.update_layout(legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(apply_chart_style(fig_sk, 520), use_container_width=True)
else:
    st.info("Not enough skill data for current filters.")

divider()

# ── Experience Range Distribution ─────────────────────────────────────────
section("📐 What min/max experience range do employers typically ask for?")

exp_range = fdf.dropna(subset=["minimumExperience", "maximumExperience"]).copy()
exp_range["exp_spread"] = exp_range["maximumExperience"] - exp_range["minimumExperience"]

c5, c6 = st.columns(2)
with c5:
    fig_min = px.histogram(
        exp_range, x="minimumExperience", nbins=15,
        labels={"minimumExperience": "Minimum Experience Required (Yrs)"},
        color_discrete_sequence=[PRIMARY],
    )
    fig_min.update_layout(title="Min Experience Distribution")
    st.plotly_chart(apply_chart_style(fig_min, 350), use_container_width=True)

with c6:
    fig_spread = px.histogram(
        exp_range, x="exp_spread", nbins=15,
        labels={"exp_spread": "Experience Range Width (Max \u2212 Min Years)"},
        color_discrete_sequence=[SECONDARY],
    )
    fig_spread.update_layout(title="Experience Range Width")
    st.plotly_chart(apply_chart_style(fig_spread, 350), use_container_width=True)

divider()

# ── Download ───────────────────────────────────────────────────────────────
export_cols = ["title", "companyName", "primary_location", "experience_group",
               "minimumExperience", "maximumExperience", "average_salary_lpa"]
download_csv_button(
    fdf[[c for c in export_cols if c in fdf.columns]],
    key="exp_dl"
)
