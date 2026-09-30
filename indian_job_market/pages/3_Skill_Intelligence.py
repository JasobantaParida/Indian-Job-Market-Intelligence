"""
3_Skill_Intelligence.py — Page 3: Skill Intelligence
Answers: Which skills are most in demand? How do requirements vary by role or experience?
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, divider, hbar, insight_card,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY,
)
from skill_extraction import (
    get_top_skills, get_skill_by_column, get_skill_cooccurrence,
)

st.set_page_config(page_title="Skill Intelligence", page_icon="🛠️", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🛠️", "Skill Intelligence",
    "Which skills appear most frequently in job postings? — Demand patterns, role gaps & co-occurrence.",
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔧 Filters</div>",
        unsafe_allow_html=True,
    )
    search_role = st.text_input("Search Job Role", placeholder="e.g. Data Analyst")
    all_locs = sorted(df["primary_location"].dropna().unique().tolist())
    sel_locs = st.multiselect("Location", all_locs, placeholder="All locations")
    all_exp = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")
    top_n_skills = st.slider("Number of top skills to show", 10, 30, 20)

    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if search_role:
    fdf = fdf[fdf["title"].str.contains(search_role, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]
if sel_exp:
    fdf = fdf[fdf["experience_group"].isin(sel_exp)]

st.info(f"Analysing skills across **{len(fdf):,}** job postings.", icon="🛠️")

# ── Section 1: Top Skills ─────────────────────────────────────────────────
section(f"🥇 Top {top_n_skills} Most In-Demand Skills")

top_skills_df = get_top_skills(fdf, top_n_skills)
if top_skills_df.empty:
    st.warning("No skills detected for the current filters.")
else:
    fig1 = hbar(
        top_skills_df, "count", "skill", "",
        color=PRIMARY, height=max(380, top_n_skills * 26),
        x_label="Number of Postings", y_label="Skill",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Insight card below top skills
    top_skill_name = top_skills_df.iloc[-1]["skill"]  # sorted ascending, last = highest
    top_skill_count = int(top_skills_df.iloc[-1]["count"])
    insight_card(
        f"<b>{top_skill_name}</b> is the most frequently listed skill, appearing in "
        f"<b>{top_skill_count:,}</b> job postings in the current filter. "
        f"Consider building depth in this skill to maximise your employability."
    )

divider()

# ── Section 2: Skills by Job Role ─────────────────────────────────────────
section("🎯 Which skills are requested for each role?")

# Pick top 8 roles for readability
top_roles = fdf["title"].value_counts().head(8).index.tolist()
role_skill = get_skill_by_column(
    fdf[fdf["title"].isin(top_roles)], "title", n_skills=12
)

if not role_skill.empty:
    pivot = (
        role_skill.pivot(index="skill", columns="category", values="count")
        .fillna(0)
    )
    fig2 = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        labels=dict(x="Job Role", y="Skill", color="Count"),
        aspect="auto",
        title="",
    )
    fig2.update_xaxes(tickangle=-30)
    st.plotly_chart(apply_chart_style(fig2, 480), use_container_width=True)
else:
    st.info("Not enough data for a skills-by-role heatmap with current filters.")

divider()

# ── Section 3: Skills by Experience Level ─────────────────────────────────
section("📈 How do skill requirements evolve with seniority?")

exp_order = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
exp_skill = get_skill_by_column(
    fdf[fdf["experience_group"].isin(exp_order)], "experience_group", n_skills=12
)

if not exp_skill.empty:
    # Normalise counts within each experience group for fair comparison
    totals = exp_skill.groupby("category")["count"].transform("sum")
    exp_skill = exp_skill.copy()
    exp_skill["pct"] = (exp_skill["count"] / totals * 100).round(1)

    exp_skill["cat_order"] = exp_skill["category"].apply(
        lambda x: exp_order.index(x) if x in exp_order else 99
    )
    exp_skill = exp_skill.sort_values("cat_order")

    fig3 = px.bar(
        exp_skill,
        x="pct",
        y="skill",
        color="category",
        barmode="group",
        orientation="h",
        labels={"pct": "% of Postings in Category", "skill": "Skill", "category": "Experience"},
        color_discrete_sequence=QUAL_COLORS,
    )
    fig3.update_layout(legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(apply_chart_style(fig3, 500), use_container_width=True)
else:
    st.info("Not enough data for skills-by-experience chart with current filters.")

divider()

# ── Section 4: Skill Co-occurrence ────────────────────────────────────────
section("🔗 Which skills are most commonly listed together?")

co_df = get_skill_cooccurrence(fdf, top_n=top_n_skills)
if not co_df.empty:
    top_co = co_df.head(15).copy()
    top_co["pair"] = top_co["skill_a"] + " ↔ " + top_co["skill_b"]
    fig4 = hbar(
        top_co, "count", "pair", "",
        color=SECONDARY, height=420,
        x_label="Co-occurrence Count", y_label="Skill Pair",
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.caption("Top co-occurrence pairs (detailed view):")
    st.dataframe(
        top_co[["skill_a", "skill_b", "count"]]
        .rename(columns={"skill_a": "Skill A", "skill_b": "Skill B", "count": "Co-occurrences"}),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Not enough skill co-occurrence data for current filters.")

divider()

# ── Download ───────────────────────────────────────────────────────────────
section("⬇️ Export Data")
skill_export = fdf[["title", "companyName", "primary_location",
                     "experience_group", "tagsAndSkills"]].copy()
download_csv_button(skill_export, key="skill_dl")
