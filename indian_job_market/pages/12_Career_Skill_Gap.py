"""
12_Career_Skill_Gap.py — Page 12: Career Skill Gap Analyzer
Select a target role, see what skills are in demand, compare with your own.
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, hbar,
    apply_chart_style, PRIMARY, SECONDARY, QUAL_COLORS,
)
from career_analysis import (
    ROLE_KEYWORDS, ALL_CANONICAL_SKILLS,
    filter_by_role, get_role_skill_demand, skill_gap_analysis, get_common_skill_combos,
)

st.set_page_config(page_title="Career Skill Gap Analyzer", page_icon="🎯", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🎯", "Career Skill Gap Analyzer",
    "Understand which skills employers frequently seek for your target role \u2014 and identify your gaps.",
)

st.info(
    "\U0001f4cc Skills shown are **frequently mentioned** in job postings for the selected role \u2014 "
    "not guaranteed requirements. Based on patterns in this dataset only.",
)
divider()

# ── Sidebar: role selection & user skills ─────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🎯 Your Profile</div>",
        unsafe_allow_html=True,
    )
    target_role = st.selectbox(
        "Target Role",
        options=list(ROLE_KEYWORDS.keys()),
        help="Choose the role you want to work towards",
    )
    st.markdown("**Your Current Skills**")
    user_skills = st.multiselect(
        "Select skills you already have",
        options=ALL_CANONICAL_SKILLS,
        default=[],
        help="Choose from canonical skill names used in this dataset",
    )
    top_n = st.slider("Top N skills to analyse", 10, 30, 20)

    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()

# ── Filter data for role ───────────────────────────────────────────────────
role_df = filter_by_role(df, target_role)

if len(role_df) < 5:
    st.warning(
        f"Fewer than 5 job postings found for **{target_role}** in the dataset. "
        "Try a broader role or check the dataset coverage."
    )
    st.stop()

st.success(f"Found **{len(role_df):,}** job postings for **{target_role}** in the dataset.", icon="\u2705")
divider()

# ── Skill gap analysis ────────────────────────────────────────────────────
gap = skill_gap_analysis(role_df, user_skills, top_n=top_n)
demand_df = gap["demand"]
covered   = gap["covered"]
gaps      = gap["gaps"]
coverage  = gap["coverage"]

# ── KPIs ──────────────────────────────────────────────────────────────────
section("📌 Skill Coverage Summary")
kpi_row([
    ("Target Role Postings",  f"{len(role_df):,}", "in the dataset"),
    ("Top Skills Analysed",   str(top_n),          "by posting frequency"),
    ("Your Skills Covered",   f"{len(covered)}",   f"of top {top_n} demanded"),
    ("Skills to Develop",     f"{len(gaps)}",      "not in your current set"),
    ("Coverage Rate",         f"{coverage}%",      "of top demand met"),
])

divider()

# ── Demand chart ──────────────────────────────────────────────────────────
section(f"📊 Top {top_n} Skills Demanded for {target_role}")
st.caption(
    "Skill frequency = number of postings for this role that mention the skill. "
    "Not all postings have skill data \u2014 treat % as a directional indicator."
)

if demand_df.empty:
    st.info("No skill data found for this role with current filters.")
else:
    # Colour-code covered vs gap skills
    demand_df = demand_df.copy()
    demand_df["status"] = demand_df["skill"].apply(
        lambda s: "\u2705 Have it" if s in covered else "\U0001f4da Need it"
    )
    color_map = {"\u2705 Have it": "#22c55e", "\U0001f4da Need it": PRIMARY}

    fig = px.bar(
        demand_df.sort_values("count"),
        x="count",
        y="skill",
        color="status",
        orientation="h",
        color_discrete_map=color_map,
        labels={"count": "Job Postings Mentioning Skill", "skill": "Skill", "status": ""},
        title=f"Skill Frequency for {target_role} Roles",
        text="pct_of_postings",
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Postings: %{x:,}<br>%{text:.1f}% of role postings<extra></extra>",
    )
    fig.update_layout(legend=dict(orientation="h", y=1.05))
    st.plotly_chart(apply_chart_style(fig, max(400, top_n * 28)), use_container_width=True)

divider()

# ── Coverage breakdown ────────────────────────────────────────────────────
section("\u2705 Skills You Already Have (Covered)")
if covered:
    covered_df = demand_df[demand_df["skill"].isin(covered)][["skill", "count", "pct_of_postings"]]
    covered_df.columns = ["Skill", "Postings Mentioning", "% of Role Postings"]
    st.dataframe(covered_df, hide_index=True, use_container_width=True)
else:
    st.info("None of your selected skills appear in the top-demand list for this role (or no skills selected).")

divider()

section("\U0001f4da Skills Frequently Requested \u2014 Not in Your Current Set")
st.caption("These are the highest-frequency skills for this role that you haven\u2019t listed yet.")
if gaps:
    gaps_df = demand_df[demand_df["skill"].isin(gaps)][["skill", "count", "pct_of_postings"]]
    gaps_df.columns = ["Skill to Develop", "Postings Mentioning", "% of Role Postings"]
    st.dataframe(gaps_df, hide_index=True, use_container_width=True)
    st.caption(
        "\U0001f4a1 Tip: Focus on skills with the highest % of postings \u2014 those appear most consistently "
        "in job requirements for this role."
    )
else:
    st.success("You\u2019ve covered all the top-demanded skills for this role! \U0001f389")

divider()

# ── Common skill combos ────────────────────────────────────────────────────
section("🔗 Common Skill Combinations for This Role")
st.caption("Skill pairs that frequently appear together in the same job posting.")

combos = get_common_skill_combos(role_df, top_n_skills=top_n, top_combos=12)
if not combos.empty:
    combos["pair"] = combos["Skill A"] + " \u2194 " + combos["Skill B"]
    fig_combo = hbar(
        combos.rename(columns={"Co-occurrences": "count", "pair": "pair"}),
        x_col="count", y_col="pair", title="",
        color=SECONDARY, height=380,
        x_label="Co-occurrence Count", y_label="Skill Pair",
    )
    st.plotly_chart(fig_combo, use_container_width=True)
    st.dataframe(
        combos[["Skill A", "Skill B", "Co-occurrences"]],
        hide_index=True, use_container_width=True,
    )
else:
    st.info("Not enough skill co-occurrence data for this role.")

divider()

# ── Salary insight for role ────────────────────────────────────────────────
section("💰 Salary Insight for This Role")
sal_data = role_df.dropna(subset=["average_salary_lpa"])
if len(sal_data) >= 5:
    kpi_row([
        ("Postings with Salary", f"{len(sal_data):,}", f"{len(sal_data)/len(role_df)*100:.0f}% disclosed"),
        ("Mean Salary",   f"\u20b9{sal_data['average_salary_lpa'].mean():.1f} LPA", ""),
        ("Median Salary", f"\u20b9{sal_data['average_salary_lpa'].median():.1f} LPA", ""),
        ("Salary Range",  f"\u20b9{sal_data['average_salary_lpa'].min():.1f}\u2013{sal_data['average_salary_lpa'].max():.1f} LPA", "disclosed range"),
    ])
    fig_sal = px.histogram(
        sal_data["average_salary_lpa"], nbins=25,
        labels={"value": "Avg Salary (LPA)"},
        color_discrete_sequence=[PRIMARY],
        title=f"Salary Distribution \u2014 {target_role}",
    )
    st.plotly_chart(apply_chart_style(fig_sal, 320), use_container_width=True)
else:
    st.info("Insufficient salary data for this role to show distributions.")
