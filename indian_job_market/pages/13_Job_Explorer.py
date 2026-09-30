"""
13_Job_Explorer.py — Page 13: Interactive Job Explorer
Filter and search across 97K+ job postings with sorting, pagination, and CSV export.
"""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider,
    download_csv_button, PRIMARY,
)

st.set_page_config(page_title="Job Explorer", page_icon="🔎", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🔎", "Job Explorer",
    "Search and explore 97K+ job postings \u2014 filter by role, company, skill, location & salary.",
)
divider()

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#8b92a8;text-transform:uppercase;"
        "letter-spacing:0.06em;margin-bottom:0.4rem;'>🔍 Search & Filters</div>",
        unsafe_allow_html=True,
    )

    title_search   = st.text_input("Job Title / Role",  placeholder="e.g. Data Analyst")
    company_search = st.text_input("Company",            placeholder="e.g. Infosys")
    skill_search   = st.text_input("Skill / Keyword",   placeholder="e.g. Python")

    all_locs = ["All"] + sorted(df["primary_location"].dropna().unique().tolist())
    sel_loc = st.selectbox("Location", all_locs)

    all_exp = ["All", "Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
    sel_exp = st.selectbox("Experience Level", all_exp)

    max_sal = float(df["average_salary_lpa"].dropna().max()) if df["average_salary_lpa"].notna().any() else 50.0
    sal_range = st.slider(
        "Salary Range (LPA, 0 = any)",
        0.0, min(max_sal, 100.0), (0.0, min(max_sal, 100.0)), step=0.5
    )

    min_rating = st.slider(
        "Minimum Company Rating (0 = any)",
        0.0, 5.0, 0.0, step=0.1,
    )

    sort_col = st.selectbox(
        "Sort By",
        ["average_salary_lpa (High\u2192Low)", "average_salary_lpa (Low\u2192High)",
         "AggregateRating (High\u2192Low)", "title (A\u2192Z)", "companyName (A\u2192Z)"],
    )

    rows_per_page = st.select_slider("Rows per page", [25, 50, 100, 200], value=50)

    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()

# ── Apply filters ──────────────────────────────────────────────────────────
fdf = df.copy()

if title_search:
    fdf = fdf[fdf["title"].str.contains(title_search, case=False, na=False)]
if company_search:
    fdf = fdf[fdf["companyName"].str.contains(company_search, case=False, na=False)]
if skill_search:
    fdf = fdf[fdf["tagsAndSkills"].str.contains(skill_search, case=False, na=False)]
if sel_loc != "All":
    fdf = fdf[fdf["primary_location"] == sel_loc]
if sel_exp != "All":
    fdf = fdf[fdf["experience_group"] == sel_exp]
if sal_range[0] > 0 or sal_range[1] < min(max_sal, 100.0):
    fdf = fdf[
        fdf["average_salary_lpa"].notna() &
        (fdf["average_salary_lpa"] >= sal_range[0]) &
        (fdf["average_salary_lpa"] <= sal_range[1])
    ]
if min_rating > 0:
    fdf = fdf[fdf["AggregateRating"].notna() & (fdf["AggregateRating"] >= min_rating)]

# ── Apply sorting ──────────────────────────────────────────────────────────
sort_map = {
    "average_salary_lpa (High\u2192Low)": ("average_salary_lpa", False),
    "average_salary_lpa (Low\u2192High)": ("average_salary_lpa", True),
    "AggregateRating (High\u2192Low)":    ("AggregateRating", False),
    "title (A\u2192Z)":                   ("title", True),
    "companyName (A\u2192Z)":             ("companyName", True),
}
sort_field, sort_asc = sort_map[sort_col]
fdf = fdf.sort_values(sort_field, ascending=sort_asc, na_position="last")

# ── Results summary ────────────────────────────────────────────────────────
# Result count badge
st.markdown(
    f"<div style='display:inline-block;background:#1a1f2e;border:1px solid #2d3348;"
    f"border-radius:20px;padding:4px 14px;font-size:0.82rem;color:#4f8ef7;font-weight:600;"
    f"margin-bottom:0.8rem;'>\U0001f4cb {len(fdf):,} matching jobs</div>",
    unsafe_allow_html=True,
)

if len(fdf) == 0:
    st.warning("No jobs match the current filters. Try broadening your search criteria.")
    st.stop()

sal_match = fdf["average_salary_lpa"].notna().sum()
kpi_row([
    ("Matching Jobs",     f"{len(fdf):,}",    f"{len(fdf)/len(df)*100:.1f}% of total"),
    ("With Salary",       f"{sal_match:,}",   f"{sal_match/max(1,len(fdf))*100:.0f}% disclosed"),
    ("Avg Salary",        f"\u20b9{fdf['average_salary_lpa'].mean():.1f} LPA" if sal_match > 0 else "N/A", "filtered"),
    ("Unique Companies",  f"{fdf['companyName'].nunique():,}", ""),
    ("Unique Locations",  f"{fdf['primary_location'].nunique():,}", ""),
])

divider()

# ── Pagination ─────────────────────────────────────────────────────────────
total_pages = max(1, (len(fdf) - 1) // rows_per_page + 1)
page_num = st.number_input(
    f"Page (1 \u2013 {total_pages})", min_value=1, max_value=total_pages, value=1, step=1, key="page_num"
)

start = (page_num - 1) * rows_per_page
end   = start + rows_per_page
page_df = fdf.iloc[start:end]

# ── Display columns ────────────────────────────────────────────────────────
DISPLAY_COLS = {
    "title":              "Job Role",
    "companyName":        "Company",
    "primary_location":   "City",
    "experience_group":   "Experience",
    "average_salary_lpa": "Avg Salary (LPA)",
    "AggregateRating":    "Rating",
    "tagsAndSkills":      "Skills / Tags",
}
available_display = {k: v for k, v in DISPLAY_COLS.items() if k in page_df.columns}
display_df = page_df[list(available_display.keys())].rename(columns=available_display).copy()
if "Avg Salary (LPA)" in display_df.columns:
    display_df["Avg Salary (LPA)"] = display_df["Avg Salary (LPA)"].apply(
        lambda x: f"\u20b9{x:.1f}" if pd.notna(x) else "\u2013"
    )
if "Rating" in display_df.columns:
    display_df["Rating"] = display_df["Rating"].apply(
        lambda x: f"\u2b50 {x:.1f}" if pd.notna(x) else "\u2013"
    )

st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)

st.caption(
    f"Showing rows {start+1}\u2013{min(end, len(fdf))} of {len(fdf):,}  |  "
    f"Page {page_num} of {total_pages}"
)

divider()

# ── Download ───────────────────────────────────────────────────────────────
section("\u2b07\ufe0f Export")
export_cols = ["title", "companyName", "primary_location", "experience_group",
               "minimumExperience", "maximumExperience",
               "average_salary_lpa", "AggregateRating", "tagsAndSkills"]
download_csv_button(
    fdf[[c for c in export_cols if c in fdf.columns]].rename(columns={
        "title":              "Job Role",
        "companyName":        "Company",
        "primary_location":   "City",
        "experience_group":   "Experience Group",
        "minimumExperience":  "Min Exp (Yrs)",
        "maximumExperience":  "Max Exp (Yrs)",
        "average_salary_lpa": "Avg Salary (LPA)",
        "AggregateRating":    "Company Rating",
        "tagsAndSkills":      "Skills",
    }),
    label=f"Download {len(fdf):,} matching jobs as CSV",
    key="explorer_dl",
)
