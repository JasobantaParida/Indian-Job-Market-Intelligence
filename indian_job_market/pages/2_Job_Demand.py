"""
2_Job_Demand.py — Page 2: Job Demand Analysis
Answers: Which roles, cities, and experience levels have the highest demand?
"""

import os
import sys
import streamlit as st
import plotly.express as px

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, divider, hbar, vbar,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY,
)
from analysis import demand_by_role, demand_by_location, demand_by_experience

st.set_page_config(page_title="Job Demand Analysis", page_icon="🔍", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🔍", "Job Demand Analysis",
    "What drives job demand in India's market? — Roles, cities, and experience levels ranked by posting volume.",
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

    top_n = st.slider("Top N roles / locations", 5, 30, 15)

    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if search_role:
    fdf = fdf[fdf["title"].str.contains(search_role, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]
if sel_exp:
    fdf = fdf[fdf["experience_group"].isin(sel_exp)]

st.info(f"Showing **{len(fdf):,}** job postings matching the current filters.", icon="📋")

# ── Section 1: Most demanded roles ────────────────────────────────────────
section("🏆 Which roles are employers posting for the most?")

top_roles = demand_by_role(fdf, top_n)
fig = hbar(top_roles, "count", "title", "",
           color=PRIMARY, height=max(350, top_n * 28),
           x_label="Number of Postings", y_label="Job Role")
st.plotly_chart(fig, use_container_width=True)

divider()

# ── Section 2: Job demand by location ─────────────────────────────────────
section("📍 Which cities are the hottest job markets?")

top_locs = demand_by_location(fdf, top_n)
c1, c2 = st.columns([3, 2])
with c1:
    fig2 = hbar(top_locs, "count", "primary_location", "",
                color=SECONDARY, height=max(350, top_n * 28),
                x_label="Number of Postings", y_label="City")
    st.plotly_chart(fig2, use_container_width=True)
with c2:
    st.dataframe(
        top_locs.rename(columns={"primary_location": "City", "count": "Postings"})
                .assign(Rank=lambda d: range(1, len(d)+1))
                .set_index("Rank"),
        use_container_width=True,
    )

divider()

# ── Section 3: Demand by experience ───────────────────────────────────────
section("🎓 How many postings target each experience bracket?")

exp_df = demand_by_experience(fdf)
c3, c4 = st.columns([2, 1])
with c3:
    exp_known_plot = exp_df[exp_df["experience_group"] != "Unknown"].copy()
    exp_colors = [PRIMARY, "#5ba4e8", SECONDARY, "#22c55e", "#f59e0b"]
    bar_colors  = exp_colors[:len(exp_known_plot)]
    fig3 = vbar(
        exp_known_plot,
        "experience_group", "count", "",
        color=PRIMARY, height=380,
        x_label="Experience Level", y_label="Number of Postings",
    )
    if bar_colors:
        fig3.update_traces(marker_color=bar_colors, marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)
with c4:
    st.dataframe(
        exp_df.rename(columns={"experience_group": "Level", "count": "Postings"})
              .assign(Share=lambda d: (d["Postings"] / d["Postings"].sum() * 100).round(1)),
        hide_index=True,
        use_container_width=True,
    )

divider()

# ── Section 4: Role × Location heatmap ─────────────────────────────────────
section("🌐 Role × Location Demand Heatmap")
st.caption("Which roles are concentrated in which cities?")

top_role_list = df["title"].value_counts().head(12).index.tolist()
top_loc_list  = df["primary_location"].value_counts().head(12).index.tolist()

heat_df = (
    fdf[fdf["title"].isin(top_role_list) & fdf["primary_location"].isin(top_loc_list)]
    .groupby(["primary_location", "title"])
    .size()
    .reset_index(name="count")
    .pivot(index="primary_location", columns="title", values="count")
    .fillna(0)
)

if not heat_df.empty:
    fig4 = px.imshow(
        heat_df,
        color_continuous_scale="Blues",
        labels=dict(x="Job Role", y="City", color="Postings"),
        aspect="auto",
    )
    fig4.update_xaxes(tickangle=-35)
    fig4.update_layout(coloraxis_showscale=True)
    st.plotly_chart(apply_chart_style(fig4, 460), use_container_width=True)
else:
    st.info("No data for current filters to build heatmap.")

divider()

# ── Download ───────────────────────────────────────────────────────────────
cols_export = ["title", "companyName", "primary_location", "experience_group",
               "average_salary_lpa", "tagsAndSkills"]
download_csv_button(fdf[[c for c in cols_export if c in fdf.columns]], key="demand_dl")
