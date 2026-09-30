"""
10_Statistical_Insights.py — Page 10: Statistical Insights
Descriptive statistics, salary distributions, correlations, and ANOVA.
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui_helpers import (
    inject_css, render_sidebar, page_header, section, kpi_row, divider,
    apply_chart_style, download_csv_button,
    QUAL_COLORS, PRIMARY, SECONDARY,
)
from statistics_analysis import (
    numeric_summary, outlier_summary, salary_stats_by_group,
    correlation_matrix, anova_salary_by_experience, salary_percentiles,
)

st.set_page_config(page_title="Statistical Insights", page_icon="📐", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "📐", "Statistical Insights",
    "Statistical summary of salary and experience patterns — distributions, percentiles, correlations & ANOVA.",
)
divider()

# ── Salary Descriptive Stats ───────────────────────────────────────────────
section("📊 Salary (LPA) \u2014 Descriptive Statistics")
st.caption("Full statistical summary of the average_salary_lpa column (salary-disclosed rows only).")

sal_stats = numeric_summary(df, "average_salary_lpa")
sal_outliers = outlier_summary(df, "average_salary_lpa")
sal_data = df["average_salary_lpa"].dropna()

c1, c2 = st.columns([1, 2])
with c1:
    st.dataframe(sal_stats, hide_index=True, use_container_width=True)
    if sal_outliers:
        st.markdown("**IQR Outlier Summary**")
        st.dataframe(pd.DataFrame([sal_outliers]), hide_index=True, use_container_width=True)

with c2:
    fig_hist = px.histogram(
        sal_data, x=sal_data, nbins=50,
        labels={"x": "Average Salary (LPA)"},
        color_discrete_sequence=[PRIMARY],
        title="Salary Distribution",
    )
    fig_hist.add_vline(
        x=float(sal_data.mean()), line_dash="dash", line_color="#ef4444",
        annotation_text=f"\u20b9{sal_data.mean():.1f} Mean",
        annotation_font_color="#ef4444",
    )
    fig_hist.add_vline(
        x=float(sal_data.median()), line_dash="dot", line_color="#22c55e",
        annotation_text=f"\u20b9{sal_data.median():.1f} Median",
        annotation_font_color="#22c55e",
    )
    st.plotly_chart(apply_chart_style(fig_hist, 380), use_container_width=True)

divider()

# ── Salary Percentiles ────────────────────────────────────────────────────
section("📐 Salary Percentile Table")
st.caption("At what LPA does X% of salary-disclosed postings fall below?")

pct_df = salary_percentiles(df)
c3, c4 = st.columns([1, 2])
with c3:
    st.dataframe(pct_df, hide_index=True, use_container_width=True)
with c4:
    fig_pct = px.line(
        pct_df,
        x="Percentile", y="Salary (LPA)",
        markers=True,
        color_discrete_sequence=[PRIMARY],
        title="Salary Percentile Curve",
    )
    fig_pct.update_traces(line_width=2.5, marker_size=7)
    st.plotly_chart(apply_chart_style(fig_pct, 360), use_container_width=True)

divider()

# ── Salary by Experience ───────────────────────────────────────────────────
section("📊 Salary Statistics by Experience Group")
st.caption("How do mean, median, and spread differ across experience brackets?")

exp_order = ["Fresher (0 Yrs)", "0\u20132 Yrs", "2\u20135 Yrs", "5\u20138 Yrs", "8+ Yrs"]
exp_stats = salary_stats_by_group(df, "experience_group", min_n=20)
exp_stats = exp_stats[exp_stats["Group"].isin(exp_order)].copy()
exp_stats["sort"] = exp_stats["Group"].apply(lambda x: exp_order.index(x) if x in exp_order else 99)
exp_stats = exp_stats.sort_values("sort").drop(columns="sort")

if not exp_stats.empty:
    c5, c6 = st.columns([3, 2])
    with c5:
        fig_exp = go.Figure()
        for col, clr, name in [("Mean", PRIMARY, "Mean"), ("Median", SECONDARY, "Median")]:
            fig_exp.add_trace(go.Bar(
                x=exp_stats["Group"], y=exp_stats[col],
                name=name, marker_color=clr,
            ))
        fig_exp.update_layout(barmode="group", xaxis_tickangle=-20,
                               legend=dict(orientation="h", y=1.05))
        st.plotly_chart(apply_chart_style(fig_exp, 380), use_container_width=True)
    with c6:
        st.dataframe(exp_stats.rename(columns={"Group": "Experience Level"}),
                     hide_index=True, use_container_width=True)
else:
    st.info("Insufficient data for experience group comparison.")

divider()

# ── Salary by Top Job Categories ──────────────────────────────────────────
section("🏆 Salary Statistics by Job Role (Top 15)")
st.caption("How does salary vary across the highest-demand roles?")

role_stats = salary_stats_by_group(df, "title", min_n=15).head(15)
if not role_stats.empty:
    st.dataframe(role_stats.rename(columns={"Group": "Job Role"}),
                 hide_index=True, use_container_width=True)
    fig_role = px.bar(
        role_stats.sort_values("Mean"),
        x="Mean", y="Group",
        orientation="h",
        color="Mean",
        color_continuous_scale="Blues",
        labels={"Mean": "Mean Salary (LPA)", "Group": "Job Role"},
        title="Average Salary by Role",
    )
    fig_role.update_layout(coloraxis_showscale=False)
    st.plotly_chart(apply_chart_style(fig_role, 440), use_container_width=True)

divider()

# ── Correlation Matrix ────────────────────────────────────────────────────
section("🔗 Correlation Matrix (Numeric Variables)")
st.caption("Pearson correlation between key numeric features. Values near \u00b11 indicate strong linear relationships.")

corr = correlation_matrix(df)
if not corr.empty:
    fig_corr = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="Pearson Correlation Matrix",
    )
    fig_corr.update_layout(height=420)
    st.plotly_chart(apply_chart_style(fig_corr, 420), use_container_width=True)

    st.caption(
        "Note: Correlation measures linear association only. "
        "High correlation does not imply causation."
    )

divider()

# ── ANOVA ─────────────────────────────────────────────────────────────────
section("🔬 One-Way ANOVA: Salary by Experience Group")
st.caption("Does average salary differ significantly across experience levels?")

anova = anova_salary_by_experience(df)
if "error" in anova:
    st.info(anova["error"])
else:
    c7, c8 = st.columns(2)
    c7.metric("F-statistic", f"{anova['f_statistic']:,.3f}")
    c8.metric(
        "p-value", f"{anova['p_value']:.2e}",
        delta="Significant" if anova["significant"] else "Not Significant",
        delta_color="normal",
    )
    if anova["significant"]:
        st.success("The test suggests salary differences across experience groups are statistically significant.")
    else:
        st.info("No statistically significant salary difference detected across experience groups.")
    st.warning(f"\u26a0\ufe0f Interpretation caveat: {anova['caveat']}")

divider()

# ── Experience Stats ───────────────────────────────────────────────────────
section("📐 Experience \u2014 Descriptive Statistics")
st.caption("Statistical summary of minimum years of experience required.")

exp_stats_raw = numeric_summary(df, "minimumExperience")
c9, c10 = st.columns([1, 2])
with c9:
    st.dataframe(exp_stats_raw, hide_index=True, use_container_width=True)
with c10:
    exp_data = df["minimumExperience"].dropna()
    fig_exp2 = px.histogram(
        exp_data, x=exp_data, nbins=20,
        labels={"x": "Min Experience Required (Yrs)"},
        color_discrete_sequence=[SECONDARY],
        title="Distribution of Minimum Experience Required",
    )
    st.plotly_chart(apply_chart_style(fig_exp2, 360), use_container_width=True)
