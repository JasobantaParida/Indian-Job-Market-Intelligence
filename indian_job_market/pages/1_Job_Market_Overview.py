"""
1_Job_Market_Overview.py — Page 1: Job Market Overview
Answers: What is the overall state of the Indian job market in 2025?
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, insight_card,
    hbar, vbar, apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY, ACCENT_GREEN,
)
from analysis import (
    overview_kpis, demand_by_role, demand_by_location, jobs_over_time,
    top_n_by_count,
)

st.set_page_config(page_title="Job Market Overview", page_icon="📊", layout="wide")
inject_css()
render_sidebar()

# ── Load data ──────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

# ── Header ─────────────────────────────────────────────────────────────────
page_header(
    "📊", "Job Market Overview",
    "What is the overall state of the Indian job market? — Postings, companies, locations & salary at a glance.",
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔧 Filters</div>",
        unsafe_allow_html=True,
    )
    all_locs = sorted(df["primary_location"].dropna().unique().tolist())
    sel_locs = st.multiselect("Location", all_locs, placeholder="All locations")

    all_exp = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")

    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]
if sel_exp:
    fdf = fdf[fdf["experience_group"].isin(sel_exp)]

# ── KPIs ───────────────────────────────────────────────────────────────────
section("📌 Key Metrics")
kpis = overview_kpis(fdf)
avg_sal_str    = f"₹{float(kpis['avg_salary_lpa']):.1f} LPA"    if kpis["avg_salary_lpa"] is not None else "N/A"
median_sal_str = f"₹{float(kpis['median_salary_lpa']):.1f} LPA" if kpis["median_salary_lpa"] is not None else "N/A"
kpi_row([
    ("Total Job Postings", f"{kpis['total_jobs']:,}",      f"across {kpis['total_locations']:,} cities"),
    ("Companies Hiring",   f"{kpis['total_companies']:,}", "unique employers"),
    ("Locations",          f"{kpis['total_locations']:,}", "cities & metro areas"),
    ("Avg Salary",         avg_sal_str,                    "where disclosed"),
    ("Median Salary",      median_sal_str,                 "where disclosed"),
])

divider()

# ── Row 1: Top Job Roles + Top Locations ───────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    section("🏆 Which roles have the most postings?")
    top_roles = demand_by_role(fdf, 10)
    fig = hbar(top_roles, "count", "title", "",
               color=PRIMARY, height=380,
               x_label="Number of Postings", y_label="Job Role")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section("📍 Where are jobs most concentrated?")
    top_locs = demand_by_location(fdf, 10)
    fig2 = hbar(top_locs, "count", "primary_location", "",
                color=SECONDARY, height=380,
                x_label="Number of Postings", y_label="City")
    st.plotly_chart(fig2, use_container_width=True)

divider()

# ── Row 2: Top Companies + Time Trend ──────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    section("🏢 Which companies are hiring the most?")
    top_cos = top_n_by_count(fdf, "companyName", 10)
    fig3 = hbar(top_cos, "count", "companyName", "",
                color=ACCENT_GREEN, height=380,
                x_label="Number of Postings", y_label="Company")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    section("📅 How fresh are the job postings?")
    time_df = jobs_over_time(fdf)
    if len(time_df) > 1:
        fig4 = px.area(
            time_df,
            x="days_ago",
            y="job_count",
            labels={"days_ago": "Days Ago (0 = Today)", "job_count": "Number of Jobs"},
            color_discrete_sequence=[PRIMARY],
        )
        fig4.update_traces(
            line_color=PRIMARY,
            fillcolor="rgba(79,142,247,0.15)",
            hovertemplate="<b>%{x} days ago</b><br>Jobs: %{y:,}<extra></extra>",
        )
        fig4.update_xaxes(autorange="reversed")
        st.plotly_chart(apply_chart_style(fig4, 380), use_container_width=True)
    else:
        st.info("Not enough date variance to plot a trend for the current filter.")

divider()

# ── Experience mix ─────────────────────────────────────────────────────────
section("🎯 How are jobs distributed by experience level?")
exp_order = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs", "Unknown"]
exp_counts = (
    fdf["experience_group"]
    .value_counts()
    .reindex(exp_order, fill_value=0)
    .reset_index()
    .rename(columns={"experience_group": "Experience Level", "count": "count"})
)
c5, c6 = st.columns([1, 2])
with c5:
    fig5 = px.pie(
        exp_counts[exp_counts["count"] > 0],
        names="Experience Level",
        values="count",
        color_discrete_sequence=QUAL_COLORS,
        hole=0.45,
    )
    fig5.update_traces(
        textinfo="percent+label",
        textfont_color="#e8eaf0",
        marker=dict(line=dict(color="#0f1117", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value:,} jobs<extra></extra>",
    )
    st.plotly_chart(apply_chart_style(fig5, 350), use_container_width=True)
with c6:
    st.dataframe(
        exp_counts.assign(pct=lambda d: (d["count"] / d["count"].sum() * 100).round(1))
        .rename(columns={"count": "Postings", "pct": "% Share"}),
        hide_index=True,
        use_container_width=True,
    )

# ── Insight ────────────────────────────────────────────────────────────────
if not exp_counts.empty and exp_counts["count"].sum() > 0:
    top_exp = exp_counts.sort_values("count", ascending=False).iloc[0]
    pct_val = round(top_exp["count"] / exp_counts["count"].sum() * 100, 1)
    insight_card(
        f"<b>{top_exp['Experience Level']}</b> is the most common experience bracket with "
        f"<b>{int(top_exp['count']):,}</b> postings — {pct_val}% of the filtered dataset."
    )

divider()

# ── Download ───────────────────────────────────────────────────────────────
section("⬇️ Export Data")
st.caption(f"Exporting **{len(fdf):,}** filtered rows.")
download_csv_button(
    fdf[["title", "companyName", "primary_location", "experience_group",
         "average_salary_lpa", "tagsAndSkills", "jobUploaded", "AggregateRating"]],
    key="overview_dl"
)
