"""
6_Fresher_Jobs.py — Page 6: Fresher Job Opportunities
Answers: Where can freshers find jobs? Which companies, cities, and roles welcome entry-level candidates?
"""

import os
import sys
import streamlit as st
import plotly.express as px

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, hbar,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY, ACCENT_GREEN,
)
from analysis import fresher_kpis
from skill_extraction import get_top_skills

st.set_page_config(page_title="Fresher Job Opportunities", page_icon="🌱", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]
fresher_df = df[df["is_fresher"]].copy()

page_header(
    "🌱", "Entry-Level Opportunities",
    "Explore job postings suitable for fresh graduates and entry-level candidates in this dataset.",
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔧 Filters</div>",
        unsafe_allow_html=True,
    )
    search_role = st.text_input("Search Role", placeholder="e.g. Data Analyst")
    all_locs = sorted(fresher_df["primary_location"].dropna().unique().tolist())
    sel_locs = st.multiselect("City", all_locs, placeholder="All cities")
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = fresher_df.copy()
if search_role:
    fdf = fdf[fdf["title"].str.contains(search_role, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]

# ── KPIs ───────────────────────────────────────────────────────────────────
section("📌 Fresher Opportunity Summary")
kpis = fresher_kpis(fdf)

sal_str = f"₹{float(kpis['avg_salary_lpa']):.1f} LPA" if kpis["avg_salary_lpa"] is not None else "Not disclosed"
kpi_row([
    ("Fresher Job Postings",   f"{kpis['total_fresher_jobs']:,}", "0 yrs min experience"),
    ("% of All Postings",      f"{kpis['total_fresher_jobs']/len(df)*100:.1f}%", "market share"),
    ("Avg Fresher Salary",     sal_str, "where disclosed"),
    ("Top City",               kpis["top_cities"].iloc[0]["city"] if len(kpis["top_cities"]) > 0 else "–", "most openings"),
    ("Top Company",            kpis["top_companies"].iloc[0]["company"] if len(kpis["top_companies"]) > 0 else "–", "most fresher roles"),
])

divider()

# ── Top Roles ──────────────────────────────────────────────────────────────
section("🏆 Which roles are most accessible to new graduates?")

c1, c2 = st.columns(2)
with c1:
    fig1 = hbar(
        kpis["top_roles"].rename(columns={"role": "title", "count": "count"}),
        "count", "title", "",
        color=PRIMARY, height=380,
        x_label="Number of Postings", y_label="Job Role",
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("**Top Fresher Roles (Detailed)**")
    st.dataframe(
        kpis["top_roles"]
        .rename(columns={"role": "Role", "count": "Postings"})
        .assign(Share=lambda d: (d["Postings"] / d["Postings"].sum() * 100).round(1)),
        hide_index=True,
        use_container_width=True,
        height=380,
    )

divider()

# ── Top Skills for Freshers ────────────────────────────────────────────────
section("🛠️ Which skills should freshers build for maximum employability?")

top_fresher_skills = get_top_skills(fdf, 20)
if not top_fresher_skills.empty:
    fig2 = hbar(
        top_fresher_skills, "count", "skill", "",
        color=SECONDARY, height=520,
        x_label="Frequency in Fresher Job Postings", y_label="Skill",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No skill data available for current filters.")

divider()

# ── Top Cities ─────────────────────────────────────────────────────────────
section("📍 Which cities offer the most entry-level opportunities?")

c3, c4 = st.columns([2, 1])
with c3:
    fig3 = hbar(
        kpis["top_cities"].rename(columns={"city": "primary_location", "count": "count"}),
        "count", "primary_location", "",
        color=ACCENT_GREEN, height=360,
        x_label="Fresher Postings", y_label="City",
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.dataframe(
        kpis["top_cities"].rename(columns={"city": "City", "count": "Postings"}),
        hide_index=True,
        use_container_width=True,
    )

divider()

# ── Top Companies ──────────────────────────────────────────────────────────
section("🏢 Which employers are most active in hiring entry-level talent?")

c5, c6 = st.columns([2, 1])
with c5:
    fig4 = hbar(
        kpis["top_companies"].rename(columns={"company": "companyName", "count": "count"}),
        "count", "companyName", "",
        color="#f59e0b", height=360,
        x_label="Fresher Postings", y_label="Company",
    )
    st.plotly_chart(fig4, use_container_width=True)
with c6:
    st.dataframe(
        kpis["top_companies"].rename(columns={"company": "Company", "count": "Postings"}),
        hide_index=True,
        use_container_width=True,
    )

divider()

# ── Fresher Salary ─────────────────────────────────────────────────────────
section("💰 What salary range can freshers realistically expect?")

sal_fr = fdf.dropna(subset=["average_salary_lpa"])
if len(sal_fr) > 10:
    fig5 = px.histogram(
        sal_fr,
        x="average_salary_lpa",
        nbins=30,
        labels={"average_salary_lpa": "Average Salary (LPA)"},
        color_discrete_sequence=[PRIMARY],
    )
    fig5.add_vline(
        x=sal_fr["average_salary_lpa"].mean(),
        line_dash="dash", line_color="#ef4444",
        annotation_text=f"Mean: ₹{sal_fr['average_salary_lpa'].mean():.1f} LPA",
        annotation_font_color="#ef4444",
    )
    st.plotly_chart(apply_chart_style(fig5, 360), use_container_width=True)
else:
    st.info("Limited salary data for freshers in the current filters.")

divider()

# ── Role × City Demand ────────────────────────────────────────────────────
section("🌐 Where are the best cities for each fresher role?")

top_role_list = fdf["title"].value_counts().head(8).index.tolist()
top_loc_list  = fdf["primary_location"].value_counts().head(10).index.tolist()

heat_df = (
    fdf[fdf["title"].isin(top_role_list) & fdf["primary_location"].isin(top_loc_list)]
    .groupby(["primary_location", "title"])
    .size()
    .reset_index(name="count")
    .pivot(index="primary_location", columns="title", values="count")
    .fillna(0)
)

if not heat_df.empty:
    fig6 = px.imshow(
        heat_df,
        color_continuous_scale="Blues",
        labels=dict(x="Job Role", y="City", color="Postings"),
        aspect="auto",
    )
    fig6.update_xaxes(tickangle=-35)
    st.plotly_chart(apply_chart_style(fig6, 440), use_container_width=True)
else:
    st.info("Not enough data to build heatmap for current filters.")

divider()

# ── Download ───────────────────────────────────────────────────────────────
export_cols = ["title", "companyName", "primary_location",
               "minimumSalary_lpa", "maximumSalary_lpa", "average_salary_lpa",
               "tagsAndSkills", "AggregateRating"]
download_csv_button(
    fdf[[c for c in export_cols if c in fdf.columns]],
    label="Download Fresher Jobs CSV",
    key="fresher_dl"
)
