"""
11_Salary_Prediction.py — Page 11: ML Salary Prediction
Train regression models and predict salary for a given job profile.
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
    inject_css, render_sidebar, page_header, section, kpi_row, divider,
    apply_chart_style, PRIMARY, SECONDARY, QUAL_COLORS,
)
from ml_salary_prediction import (
    train_models, predict_salary, get_top_roles, get_top_locations,
)

st.set_page_config(page_title="Salary Prediction", page_icon="🤖", layout="wide")
inject_css()
render_sidebar()

if "df" not in st.session_state:
    st.error("Dataset not loaded. Please return to the **Home** page first.")
    st.stop()

df = st.session_state["df"]

page_header(
    "🤖", "Salary Prediction",
    "Estimate salary based on job profile features \u2014 ML models trained on real posting patterns.",
)

st.warning(
    "\u26a0\ufe0f **Important:** Salary estimates are based on patterns in job postings, not actual paid salaries. "
    "Only ~34% of postings disclosed salary data. Treat predictions as directional guidance, not guarantees.",
)
divider()

# ── Cached training wrapper ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _cached_train(_df, df_hash: int) -> dict:
    """Cache key is df_hash; _df prefixed so Streamlit skips hashing the DataFrame."""
    return train_models(_df)


# ── Train models ───────────────────────────────────────────────────────────
section("\U0001f3cb\ufe0f Model Training")
st.caption("Three models are compared: Linear Regression (baseline), Random Forest, and Gradient Boosting.")

df_hash = hash(len(df))
with st.spinner("Training models\u2026 (this runs once and is cached)"):
    results = _cached_train(df, df_hash)

if "error" in results:
    st.error(f"Model training failed: {results['error']}")
    st.stop()

# ── Model comparison table ─────────────────────────────────────────────────
metrics_rows = []
for model_name, res in results.items():
    metrics_rows.append({
        "Model": model_name,
        "MAE (LPA)": res["mae"],
        "RMSE (LPA)": res["rmse"],
        "R\u00b2 Score": res["r2"],
    })
metrics_df = pd.DataFrame(metrics_rows).sort_values("R\u00b2 Score", ascending=False)

c1, c2 = st.columns([2, 1])
with c1:
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)
with c2:
    best_model_name = metrics_df.iloc[0]["Model"]
    best_r2   = metrics_df.iloc[0]["R\u00b2 Score"]
    best_mae  = metrics_df.iloc[0]["MAE (LPA)"]
    best_rmse = metrics_df.iloc[0]["RMSE (LPA)"]
    st.markdown(f"**Best Model: {best_model_name}**")
    kpi_row([
        ("R\u00b2 Score",  f"{best_r2:.3f}",       "explained variance"),
        ("MAE",            f"\u20b9{best_mae:.2f} LPA", "mean absolute error"),
        ("RMSE",           f"\u20b9{best_rmse:.2f} LPA", "root mean square error"),
    ])

divider()

# ── Actual vs Predicted ────────────────────────────────────────────────────
section("📊 Actual vs Predicted (Best Model)")
st.caption(f"Scatter plot of actual salary vs predicted salary on the 20% test set \u2014 {best_model_name}.")

best_res   = results[best_model_name]
y_test     = best_res["y_test"]
y_pred     = best_res["y_pred"]
n_sample   = min(2000, len(y_test))
idx_sample = np.random.default_rng(42).choice(len(y_test), n_sample, replace=False)

scatter_df = pd.DataFrame({
    "Actual (LPA)":    y_test[idx_sample],
    "Predicted (LPA)": y_pred[idx_sample],
})
scatter_df["Error"] = (scatter_df["Predicted (LPA)"] - scatter_df["Actual (LPA)"]).abs()

max_val = max(scatter_df["Actual (LPA)"].max(), scatter_df["Predicted (LPA)"].max())
fig_scatter = px.scatter(
    scatter_df,
    x="Actual (LPA)",
    y="Predicted (LPA)",
    color="Error",
    color_continuous_scale="Reds",
    opacity=0.6,
    labels={"Actual (LPA)": "Actual Salary (LPA)", "Predicted (LPA)": "Predicted Salary (LPA)"},
    title=f"Actual vs Predicted \u2014 {best_model_name} (n={n_sample:,})",
)
fig_scatter.add_trace(go.Scatter(
    x=[0, max_val], y=[0, max_val],
    mode="lines", name="Perfect Prediction",
    line=dict(color="#ef4444", dash="dash", width=1.5),
))
fig_scatter.update_layout(coloraxis_showscale=False)
st.plotly_chart(apply_chart_style(fig_scatter, 460), use_container_width=True)

divider()

# ── Model metrics bar chart ────────────────────────────────────────────────
section("📋 Model Comparison")

c3, c4 = st.columns(2)
with c3:
    fig_mae = px.bar(
        metrics_df.sort_values("MAE (LPA)"),
        x="MAE (LPA)", y="Model", orientation="h",
        color_discrete_sequence=[PRIMARY],
        title="MAE by Model (lower is better)",
    )
    st.plotly_chart(apply_chart_style(fig_mae, 280), use_container_width=True)
with c4:
    fig_r2 = px.bar(
        metrics_df.sort_values("R\u00b2 Score"),
        x="R\u00b2 Score", y="Model", orientation="h",
        color_discrete_sequence=[SECONDARY],
        title="R\u00b2 Score by Model (higher is better)",
    )
    st.plotly_chart(apply_chart_style(fig_r2, 280), use_container_width=True)

divider()

# ── Interactive predictor ──────────────────────────────────────────────────
section("🎯 Predict Salary for a Job Profile")
st.caption("Enter job details to get a salary estimate from the best-performing model.")

top_roles = get_top_roles(df)
top_locs  = get_top_locations(df)

with st.form("predict_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        sel_role = st.selectbox("Job Role", top_roles, help="Select the most similar role")
        sel_loc  = st.selectbox("Location (City)", top_locs)
    with col_b:
        min_exp  = st.number_input("Minimum Experience (Years)", 0, 30, 2, step=1)
        max_exp  = st.number_input("Maximum Experience (Years)", 0, 35, 5, step=1)

    submitted = st.form_submit_button("\U0001f4a1 Predict Salary", type="primary")

if submitted:
    if max_exp < min_exp:
        st.warning("Maximum experience should be \u2265 minimum experience.")
    else:
        try:
            best_pipe = best_res["pipeline"]
            pred_val  = predict_salary(best_pipe, sel_role, sel_loc, min_exp, max_exp)
            pred_val  = max(0.0, pred_val)

            st.success(
                f"### \U0001f916 Estimated Salary: \u20b9 {pred_val:.2f} LPA\n\n"
                f"*Model: {best_model_name} \u00b7 Role: {sel_role} \u00b7 City: {sel_loc} \u00b7 "
                f"Experience: {min_exp}\u2013{max_exp} yrs*\n\n"
                f"**This is a model estimate based on patterns in {len(df):,} job postings. "
                "It is NOT a guaranteed salary and may not reflect actual market conditions.**"
            )

            # Confidence range \u2248 \u00b1MAE
            lo = max(0, pred_val - best_mae)
            hi = pred_val + best_mae
            st.caption(
                f"Approximate range (\u00b1MAE): \u20b9{lo:.1f} \u2013 \u20b9{hi:.1f} LPA"
            )
        except Exception as e:
            st.error(f"Prediction failed: {e}")

divider()

# ── Feature importance (RF only) ──────────────────────────────────────────
section("🔍 Feature Importance (Random Forest)")
st.caption("Which features contribute most to the model's predictions?")

rf_key = "Random Forest"
if rf_key in results:
    try:
        rf_pipe = results[rf_key]["pipeline"]
        feat_names = ["minimumExperience", "maximumExperience", "title", "primary_location"]
        importances = rf_pipe.named_steps["model"].feature_importances_
        fi_df = pd.DataFrame({"Feature": feat_names, "Importance": importances}).sort_values("Importance")
        fig_fi = px.bar(
            fi_df, x="Importance", y="Feature", orientation="h",
            color_discrete_sequence=["#22c55e"],
            title="Random Forest Feature Importance",
        )
        st.plotly_chart(apply_chart_style(fig_fi, 280), use_container_width=True)
    except Exception:
        st.info("Feature importance not available.")
