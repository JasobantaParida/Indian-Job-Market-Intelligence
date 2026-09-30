"""
7_Company_Location.py — Page 7: Company & Location Analysis
Answers: Which companies dominate hiring? Which cities pay the most?
How do employers rate and what roles are concentrated in which cities?
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider, hbar,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY, ACCENT_GREEN,
)
from analysis import (
    top_companies, top_locations, avg_salary_by_location, company_ratings,
    mean_salary_by,
)

st.set_page_config(page_title="Company & Location Analysis", page_icon="🏢", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🏢", "Company & Location Analysis",
    "Which companies and cities dominate the Indian job market? — Top employers, cities, salaries & ratings.",
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔧 Filters</div>",
        unsafe_allow_html=True,
    )
    search_company = st.text_input("Search Company", placeholder="e.g. Infosys")
    all_locs = sorted(df["primary_location"].dropna().unique().tolist())
    sel_locs = st.multiselect("Location", all_locs, placeholder="All locations")
    all_exp = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")
    top_n = st.slider("Top N to show", 10, 30, 20)
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

fdf = df.copy()
if search_company:
    fdf = fdf[fdf["companyName"].str.contains(search_company, case=False, na=False)]
if sel_locs:
    fdf = fdf[fdf["primary_location"].isin(sel_locs)]
if sel_exp:
    fdf = fdf[fdf["experience_group"].isin(sel_exp)]

st.info(
    f"**{len(fdf):,}** postings · **{fdf['companyName'].nunique():,}** companies · "
    f"**{fdf['primary_location'].nunique():,}** cities",
    icon="🏢",
)

# ── Top Companies ─────────────────────────────────────────────────────────
section("🏆 Which employers are the most active in the Indian job market?")

top_cos = top_companies(fdf, top_n)
c1, c2 = st.columns([3, 2])
with c1:
    fig1 = hbar(top_cos, "count", "companyName", "",
                color=PRIMARY, height=max(380, top_n * 26),
                x_label="Number of Postings", y_label="Company")
    st.plotly_chart(fig1, use_container_width=True)
with c2:
    st.dataframe(
        top_cos.rename(columns={"companyName": "Company", "count": "Postings"})
               .assign(Rank=range(1, len(top_cos)+1))
               .set_index("Rank"),
        use_container_width=True,
    )

divider()

# ── Top Locations ─────────────────────────────────────────────────────────
section("📍 Which cities have the highest concentration of jobs?")

top_locs = top_locations(fdf, top_n)
c3, c4 = st.columns([3, 2])
with c3:
    fig2 = hbar(top_locs, "count", "primary_location", "",
                color=SECONDARY, height=max(380, top_n * 26),
                x_label="Number of Postings", y_label="City")
    st.plotly_chart(fig2, use_container_width=True)
with c4:
    st.dataframe(
        top_locs.rename(columns={"primary_location": "City", "count": "Postings"})
                .assign(Rank=range(1, len(top_locs)+1))
                .set_index("Rank"),
        use_container_width=True,
    )

divider()

# ── Salary by Location ─────────────────────────────────────────────────────
section("💰 Which cities offer the highest-advertised salaries?")

sal_loc = avg_salary_by_location(fdf)
if not sal_loc.empty:
    sal_loc_plot = sal_loc.copy().rename(columns={"avg_salary_lpa": "avg_sal"})
    fig3 = hbar(
        sal_loc_plot, "avg_sal", "primary_location", "",
        color=ACCENT_GREEN, height=440,
        x_label="Average Salary (LPA)", y_label="City",
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(
        sal_loc[["primary_location", "avg_salary_lpa", "median_salary_lpa", "n"]]
        .rename(columns={
            "primary_location": "City",
            "avg_salary_lpa": "Avg LPA",
            "median_salary_lpa": "Median LPA",
            "n": "Postings w/ Salary",
        })
        .round(2),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No salary data available for current filters.")

divider()

# ── Job Roles by Location ─────────────────────────────────────────────────
section("🌐 What roles dominate which cities?")

top_role_list = df["title"].value_counts().head(10).index.tolist()
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
    st.plotly_chart(apply_chart_style(fig4, 460), use_container_width=True)
else:
    st.info("Not enough data to build heatmap for current filters.")

divider()

# ── Company Ratings ────────────────────────────────────────────────────────
section("⭐ Which companies have the highest employee ratings?")

ratings = company_ratings(fdf, min_reviews=5)
if not ratings.empty:
    c5, c6 = st.columns([2, 1])
    with c5:
        fig5 = hbar(
            ratings.head(20).rename(columns={"avg_rating": "avg_rat"}),
            "avg_rat", "companyName", "",
            color="#f59e0b", height=480,
            x_label="Average Rating (out of 5)", y_label="Company",
        )
        fig5.update_xaxes(range=[0, 5])
        st.plotly_chart(fig5, use_container_width=True)
    with c6:
        st.dataframe(
            ratings[["companyName", "avg_rating", "total_reviews", "job_postings"]]
            .rename(columns={
                "companyName": "Company",
                "avg_rating": "Rating",
                "total_reviews": "Reviews",
                "job_postings": "Postings",
            })
            .round(2),
            hide_index=True,
            use_container_width=True,
        )
else:
    st.info("Insufficient review data for the current filters (need \u2265 5 reviews per company).")

divider()

# ── Company Diversity: Roles per Company ──────────────────────────────────
section("🔍 Which companies hire across the widest range of roles?")

role_diversity = (
    fdf.groupby("companyName")["title"]
    .nunique()
    .reset_index()
    .rename(columns={"title": "unique_roles"})
    .sort_values("unique_roles", ascending=False)
    .head(15)
)

fig6 = hbar(
    role_diversity.rename(columns={"unique_roles": "count"}),
    "count", "companyName", "",
    color="#8b5cf6", height=420,
    x_label="Unique Job Roles Posted", y_label="Company",
)
st.plotly_chart(fig6, use_container_width=True)

divider()

# ── Download ───────────────────────────────────────────────────────────────
export_cols = ["title", "companyName", "primary_location", "experience_group",
               "average_salary_lpa", "AggregateRating", "ReviewsCount"]
download_csv_button(
    fdf[[c for c in export_cols if c in fdf.columns]],
    label="Download Company & Location Data as CSV",
    key="company_dl"
)
