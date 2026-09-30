"""
ui_helpers.py — Shared Streamlit UI components for the dark-theme dashboard.
No Streamlit cache decorators here — those live in app.py and pages/.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── Palette ────────────────────────────────────────────────────────────────
PRIMARY        = "#38bdf8"   # accent cyan
SECONDARY      = "#60a5fa"   # secondary blue
ACCENT         = "#38bdf8"   # alias for compat
ACCENT_GREEN   = "#34d399"
ACCENT_AMBER   = "#fbbf24"
ACCENT_RED     = "#f87171"
MUTED          = "#94a3b8"
TEXT           = "#f8fafc"
BG             = "#0b1220"
SURFACE        = "#111827"
SURFACE2       = "#1e293b"
BORDER         = "#26354d"

QUAL_COLORS = [
    "#4f8ef7", "#22c55e", "#f59e0b", "#ef4444",
    "#7c5cd8", "#06b6d4", "#ec4899", "#10b981",
    "#f97316", "#8b5cf6",
]

# ── IJMI SVG Logo ─────────────────────────────────────────────────────────
# Original mark: an India-inspired geometric frame around a rising data signal.
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="42" height="42" viewBox="0 0 42 42" role="img" aria-label="IJMI">
    <rect width="42" height="42" rx="10" fill="#17243a"/>
    <path d="M21 6.5 32.5 12v10.5c0 7.2-4.9 11.3-11.5 14-6.6-2.7-11.5-6.8-11.5-14V12L21 6.5Z" fill="none" stroke="#38bdf8" stroke-width="1.6" opacity=".9"/>
    <path d="M14 27v-6h4v6m3 0v-10h4v10m3 0v-14h4v14" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round"/>
    <path d="m13.5 18.5 6.2-4.2 4 2.8 6-6" fill="none" stroke="#34d399" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

LOGO_SVG_LARGE = """
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 42 42" role="img" aria-label="IJMI">
    <rect width="42" height="42" rx="10" fill="#17243a"/>
    <path d="M21 6.5 32.5 12v10.5c0 7.2-4.9 11.3-11.5 14-6.6-2.7-11.5-6.8-11.5-14V12L21 6.5Z" fill="none" stroke="#38bdf8" stroke-width="1.6" opacity=".9"/>
    <path d="M14 27v-6h4v6m3 0v-10h4v10m3 0v-14h4v14" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round"/>
    <path d="m13.5 18.5 6.2-4.2 4 2.8 6-6" fill="none" stroke="#34d399" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

# ── CSS ────────────────────────────────────────────────────────────────────
PAGE_CSS = """
<style>
/* ═══════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: "Aptos", "Segoe UI", system-ui, sans-serif !important;
    background-color: #0b1220;
    color: #f8fafc;
}

/* ═══════════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b1220; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

/* ═══════════════════════════════════════════════════════
   HIDE STREAMLIT CHROME
═══════════════════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stAppDeployButton"] { display: none !important; }

/* ═══════════════════════════════════════════════════════
   APP BACKGROUND
═══════════════════════════════════════════════════════ */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #0f1117 !important;
}
[data-testid="stHeader"] { background-color: transparent !important; }

/* ═══════════════════════════════════════════════════════
   BLOCK CONTAINER
═══════════════════════════════════════════════════════ */
.block-container {
    padding-top: 1.6rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1180px;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — SHELL
═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #131720 !important;
    border-right: 1px solid #2d3348 !important;
    min-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
[data-testid="stSidebarContent"] {
    padding: 0 12px 16px 12px !important;
    background: #131720 !important;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — HIDE STREAMLIT AUTO-NAV (pages/ folder list)
═══════════════════════════════════════════════════════ */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — st.page_link() ITEMS
   Streamlit 1.28+ wraps page_link in [data-testid="stPageLink"]
═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:visited {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    color: #cbd5e1 !important;
    font-size: 0.855rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    padding: 6px 10px !important;
    border-radius: 7px !important;
    transition: background 0.15s, color 0.15s !important;
    line-height: 1.35 !important;
    margin: 1px 0 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: #1e293b !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-selected="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-left: 3px solid #7dd3fc !important;
    padding-left: 7px !important;
}

/* Fallback — target the inner span/p text in page_link */
[data-testid="stSidebar"] [data-testid="stPageLink"] span,
[data-testid="stSidebar"] [data-testid="stPageLink"] p {
    color: inherit !important;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — MARKDOWN TEXT (group labels, captions)
═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown div {
    color: #94a3b8 !important;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — WIDGETS (inputs, sliders, etc.)
═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label,
    background: #111827 !important;
    border-color: #26354d !important;
    color: #f8fafc !important;
    font-size: 0.8rem !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    background: #111827 !important;
    border-color: #26354d !important;
    color: #f8fafc !important;
/* ═══════════════════════════════════════════════════════
   PAGE TITLE / SUBTITLE
═══════════════════════════════════════════════════════ */
    background: #111827 !important;
    border-color: #26354d !important;
    color: #f8fafc !important;
    color: #f8fafc;
    margin-bottom: 0.2rem;
    line-height: 1.2;
    background: #111827 !important;
    border: 1px solid #26354d !important;
    font-size: 0.9rem;
    color: #94a3b8;
    color: #f8fafc !important;
    max-width: 700px;
}
    background: #111827;
    border: 1px solid #26354d;
    font-size: 0.68rem;
    font-weight: 700;
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #f8fafc !important; }
    text-transform: uppercase;
}
    background: #111827 !important;
    border: 1px solid #38bdf8 !important;
    color: #7dd3fc !important;
    margin-right: 0.35rem;
}

    background: #2563eb !important;
   SECTION HEADERS
═══════════════════════════════════════════════════════ */
.section-header {
    background: #2563eb !important;
    font-weight: 600;
    color: #f8fafc;
    border-color: #2563eb !important;
    border-left: 3px solid #4f8ef7;
    background: #1d4ed8 !important;
    background: rgba(56,189,248,0.06);
    border-radius: 0 4px 4px 0;
    color: #94a3b8 !important;
}

/* ═══════════════════════════════════════════════════════
    color: #7dd3fc !important;
    border-bottom: 2px solid #38bdf8 !important;
.kpi-card {
    background: #111827;
pre { background: #111827 !important; border: 1px solid #26354d !important; border-radius: 6px !important; }
code { color: #7dd3fc !important; }
    padding: 1.1rem 1.2rem;
[data-testid="stSpinner"] { color: #38bdf8 !important; }
    transition: border-color 0.2s;
    border-top: 1px solid #26354d;
.kpi-card:hover { border-color: #38bdf8; }
    color: #94a3b8;
    font-size: 0.7rem;
    color: #94a3b8;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 4px;
}

/* ═══════════════════════════════════════════════════════
   INSIGHT CARD
═══════════════════════════════════════════════════════ */
.insight-card {
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.28);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #f8fafc;
    font-size: 0.87rem;
    line-height: 1.55;
    margin-bottom: 0.55rem;
}

/* ═══════════════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════════════ */
hr.dark-divider {
    border: none;
    border-top: 1px solid #26354d;
    margin: 1rem 0;
}

/* ═══════════════════════════════════════════════════════
   PLOTLY MODEBAR
═══════════════════════════════════════════════════════ */
.js-plotly-plot .plotly .modebar {
    background: transparent !important;
}
.js-plotly-plot .plotly .modebar-btn path {
    fill: #8b92a8 !important;
}

/* ═══════════════════════════════════════════════════════
   DATAFRAME / TABLE
═══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #26354d;
    border-radius: 8px;
    overflow: hidden;
}
[data-testid="stDataFrame"] table,
.dataframe {
    background: #111827 !important;
    color: #f8fafc !important;
}
[data-testid="stDataFrame"] th, .dataframe th {
    background: #1e293b !important;
    color: #cbd5e1 !important;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid #26354d !important;
    padding: 8px 12px !important;
}
[data-testid="stDataFrame"] td, .dataframe td {
    border-bottom: 1px solid #1e2335 !important;
    font-size: 0.85rem;
    padding: 6px 12px !important;
}

/* ═══════════════════════════════════════════════════════
   ALERT BOXES
═══════════════════════════════════════════════════════ */
[data-testid="stInfo"] {
    background: rgba(56,189,248,0.08) !important;
    border-left: 4px solid #38bdf8 !important;
    color: #f8fafc !important;
    border-radius: 0 6px 6px 0 !important;
}
[data-testid="stWarning"] {
    background: rgba(251,191,36,0.08) !important;
    border-left: 4px solid #fbbf24 !important;
    color: #f8fafc !important;
    border-radius: 0 6px 6px 0 !important;
}
[data-testid="stError"] {
    background: rgba(248,113,113,0.08) !important;
    border-left: 4px solid #f87171 !important;
    color: #f8fafc !important;
    border-radius: 0 6px 6px 0 !important;
}
[data-testid="stSuccess"] {
    background: rgba(52,211,153,0.08) !important;
    border-left: 4px solid #34d399 !important;
    color: #f8fafc !important;
    border-radius: 0 6px 6px 0 !important;
}

/* ═══════════════════════════════════════════════════════
   FORM INPUTS
═══════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #1a1f2e !important;
    border-color: #2d3348 !important;
    color: #e8eaf0 !important;
}
.stTextInput > div > div > input,
.stTextArea textarea {
    background: #1a1f2e !important;
    border-color: #2d3348 !important;
    color: #e8eaf0 !important;
}
[data-testid="stNumberInput"] input {
    background: #1a1f2e !important;
    border-color: #2d3348 !important;
    color: #e8eaf0 !important;
}
/* Slider track */
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #8b92a8 !important;
}

/* ═══════════════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: #1a1f2e !important;
    border: 1px solid #2d3348 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #e8eaf0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* ═══════════════════════════════════════════════════════
   ST.METRIC
═══════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: #1a1f2e;
    border: 1px solid #2d3348;
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricLabel"] { color: #8b92a8 !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #e8eaf0 !important; }

/* ═══════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════ */
.stDownloadButton > button, .stButton > button {
    background: #1a1f2e !important;
    border: 1px solid #4f8ef7 !important;
    color: #4f8ef7 !important;
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    transition: background 0.15s, color 0.15s !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background: #4f8ef7 !important;
    color: #ffffff !important;
}

/* Primary form submit */
.stButton > button[kind="primary"] {
    background: #4f8ef7 !important;
    color: #ffffff !important;
    border-color: #4f8ef7 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3a7de3 !important;
}

/* ═══════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════ */
[data-testid="stTabs"] [role="tab"] {
    color: #8b92a8 !important;
    font-size: 0.87rem !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #4f8ef7 !important;
    border-bottom: 2px solid #4f8ef7 !important;
}

/* ═══════════════════════════════════════════════════════
   CODE BLOCKS
═══════════════════════════════════════════════════════ */
pre { background: #1a1f2e !important; border: 1px solid #2d3348 !important; border-radius: 6px !important; }
code { color: #4f8ef7 !important; }

/* ═══════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════ */
[data-testid="stSpinner"] { color: #4f8ef7 !important; }

/* ═══════════════════════════════════════════════════════
   FOOTER
═══════════════════════════════════════════════════════ */
.dash-footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #2d3348;
    text-align: center;
    color: #94a3b8;
    font-size: 0.74rem;
    line-height: 1.8;
}

/* ═══════════════════════════════════════════════════════
   RESPONSIVE — narrow screens
═══════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
    .kpi-value { font-size: 1.5rem !important; }
}
</style>
"""

# Final shared shell styles. Keeping this block centralized makes every page
# use the same contrast, spacing, navigation, and responsive behavior.
PAGE_CSS = """
<style>
:root {
    --ijmi-bg: #0b1220;
    --ijmi-sidebar: #0f172a;
    --ijmi-surface: #111827;
    --ijmi-surface-2: #1e293b;
    --ijmi-border: #26354d;
    --ijmi-text: #f8fafc;
    --ijmi-muted: #94a3b8;
    --ijmi-blue: #2563eb;
    --ijmi-cyan: #38bdf8;
}
html, body, [class*="css"] {
    font-family: "Aptos", "Segoe UI", system-ui, sans-serif !important;
}
.stApp, [data-testid="stAppViewContainer"] { background: var(--ijmi-bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stAppDeployButton"] { display: none !important; }
.block-container { max-width: 1180px; padding-top: 1.4rem !important; padding-bottom: 2.5rem !important; }
[data-testid="stSidebar"] {
    background: var(--ijmi-sidebar) !important;
    border-right: 1px solid var(--ijmi-border) !important;
    min-width: 236px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarContent"] { background: var(--ijmi-sidebar) !important; padding: 0 12px 16px !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:visited {
    align-items: center !important;
    border-left: 3px solid transparent !important;
    border-radius: 7px !important;
    color: #cbd5e1 !important;
    display: flex !important;
    font-size: .855rem !important;
    font-weight: 550 !important;
    gap: 8px !important;
    line-height: 1.35 !important;
    margin: 1px 0 !important;
    padding: 7px 10px !important;
    text-decoration: none !important;
    transition: background .15s ease, color .15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: #1e293b !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-selected="true"] {
    background: var(--ijmi-blue) !important;
    border-left-color: #7dd3fc !important;
    color: #ffffff !important;
    font-weight: 650 !important;
    padding-left: 7px !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] span,
[data-testid="stSidebar"] [data-testid="stPageLink"] p { color: inherit !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown div { color: var(--ijmi-muted) !important; }
[data-testid="stSidebar"] label { color: #cbd5e1 !important; font-size: .8rem !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--ijmi-muted) !important; }
.ijmi-brand svg { flex: 0 0 auto; }
.sidebar-footer { border-top: 1px solid var(--ijmi-border); color: #cbd5e1; font-size: .72rem; line-height: 1.7; margin-top: 14px; padding: 12px 4px 0; }
.sidebar-footer span { color: var(--ijmi-muted); }
.page-kicker { color: var(--ijmi-cyan); font-size: .68rem; font-weight: 700; letter-spacing: .14em; margin-bottom: .45rem; text-transform: uppercase; }
.page-title { color: var(--ijmi-text); font-size: 1.8rem; font-weight: 750; line-height: 1.2; margin-bottom: .2rem; }
.page-mark { color: #7dd3fc; font-size: 1.1rem; margin-right: .35rem; }
.page-subtitle { color: var(--ijmi-muted); font-size: .9rem; line-height: 1.55; margin-bottom: 1.4rem; max-width: 700px; }
.section-header { background: rgba(56,189,248,.06); border-left: 3px solid var(--ijmi-cyan); border-radius: 0 4px 4px 0; color: var(--ijmi-text); font-size: .93rem; font-weight: 650; letter-spacing: .01em; margin: 1.4rem 0 .85rem; padding: .45rem 0 .45rem .8rem; }
.kpi-card { background: var(--ijmi-surface); border: 1px solid var(--ijmi-border); border-radius: 8px; min-height: 96px; padding: 1.1rem 1.2rem; text-align: center; transition: border-color .2s ease; }
.kpi-card:hover { border-color: var(--ijmi-cyan); }
.kpi-label { color: var(--ijmi-muted); font-size: .7rem; letter-spacing: .07em; margin-bottom: 6px; text-transform: uppercase; }
.kpi-value { color: var(--ijmi-text); font-size: 1.9rem; font-weight: 700; line-height: 1.1; }
.kpi-sub { color: var(--ijmi-muted); font-size: .7rem; margin-top: 4px; }
.insight-card { background: rgba(52,211,153,.07); border: 1px solid rgba(52,211,153,.28); border-radius: 8px; color: var(--ijmi-text); font-size: .87rem; line-height: 1.55; margin-bottom: .55rem; padding: .8rem 1rem; }
hr.dark-divider { border: 0; border-top: 1px solid var(--ijmi-border); margin: 1rem 0; }
[data-testid="stDataFrame"] { border: 1px solid var(--ijmi-border); border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrame"] th { background: var(--ijmi-surface-2) !important; color: #cbd5e1 !important; }
[data-testid="stDataFrame"] td { border-bottom-color: #1e293b !important; }
[data-testid="stSelectbox"] > div > div, [data-testid="stMultiSelect"] > div > div,
.stTextInput > div > div > input, .stTextArea textarea, [data-testid="stNumberInput"] input { background: var(--ijmi-surface) !important; border-color: var(--ijmi-border) !important; color: var(--ijmi-text) !important; }
[data-testid="stExpander"], [data-testid="stMetric"] { background: var(--ijmi-surface) !important; border-color: var(--ijmi-border) !important; }
[data-testid="stExpander"] summary, [data-testid="stMetricValue"] { color: var(--ijmi-text) !important; }
[data-testid="stMetricLabel"] { color: var(--ijmi-muted) !important; }
.stDownloadButton > button, .stButton > button { background: var(--ijmi-surface) !important; border: 1px solid var(--ijmi-cyan) !important; color: #7dd3fc !important; }
.stDownloadButton > button:hover, .stButton > button:hover { background: var(--ijmi-blue) !important; color: #ffffff !important; }
.stButton > button[kind="primary"] { background: var(--ijmi-blue) !important; border-color: var(--ijmi-blue) !important; color: #ffffff !important; }
.dash-footer { border-top-color: var(--ijmi-border); color: var(--ijmi-muted); }
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 220px !important; }
    .block-container { padding-left: .8rem !important; padding-right: .8rem !important; }
    .page-title { font-size: 1.55rem; }
    .kpi-value { font-size: 1.5rem !important; }
}
</style>
"""

# ── Sidebar HTML block ─────────────────────────────────────────────────────
SIDEBAR_BRAND_HTML = f"""
<div class="ijmi-brand" style="display:flex;align-items:center;gap:10px;padding:16px 4px 14px 4px;">
  {LOGO_SVG}
  <div>
        <div style="font-size:0.88rem;font-weight:750;color:#f8fafc;line-height:1.2;">
      Indian Job Market
    </div>
        <div style="font-size:0.7rem;color:#cbd5e1;margin-top:2px;">
            Intelligence
        </div>
        <div style="font-size:0.62rem;color:#94a3b8;margin-top:2px;letter-spacing:0.04em;">
            Analytics Platform
    </div>
  </div>
</div>
<div style="height:1px;background:#26354d;margin:0 0 8px 0;"></div>
"""

NAV_GROUP_HTML = (
    "<div style='font-size:0.68rem;font-weight:700;color:#94a3b8;"
    "text-transform:uppercase;letter-spacing:0.1em;"
    "padding:12px 4px 4px 4px;'>{label}</div>"
)

NAV_ITEMS = (
    ("MARKET", (
        ("pages/1_Job_Market_Overview.py", ":material/dashboard:  Overview"),
        ("pages/2_Job_Demand.py", ":material/query_stats:  Job Demand"),
        ("pages/3_Skill_Intelligence.py", ":material/psychology:  Skill Intelligence"),
        ("pages/4_Salary_Intelligence.py", ":material/payments:  Salary Intelligence"),
        ("pages/5_Experience_Analysis.py", ":material/trending_up:  Experience Analysis"),
        ("pages/6_Fresher_Jobs.py", ":material/school:  Fresher Opportunities"),
        ("pages/7_Company_Location.py", ":material/business:  Company & Location"),
    )),
    ("CAREER", (
        ("pages/13_Job_Explorer.py", ":material/search:  Job Explorer"),
        ("pages/12_Career_Skill_Gap.py", ":material/target:  Career Skill Gap"),
    )),
    ("ADVANCED ANALYTICS", (
        ("pages/9_SQL_Analytics.py", ":material/database:  SQL Analytics"),
        ("pages/10_Statistical_Insights.py", ":material/insights:  Statistical Insights"),
        ("pages/11_Salary_Prediction.py", ":material/model_training:  Salary Prediction"),
    )),
    ("DATA", (
        ("pages/8_Dataset_Quality.py", ":material/fact_check:  Dataset & Quality"),
    )),
)


def inject_css():
    """Inject the global dark-theme CSS. Call once at the top of every page."""
    st.markdown(PAGE_CSS, unsafe_allow_html=True)


def sidebar_brand():
    """Render the logo + brand block at the top of the sidebar."""
    st.markdown(SIDEBAR_BRAND_HTML, unsafe_allow_html=True)


def nav_group(label: str):
    """Render a navigation group label in the sidebar."""
    st.markdown(NAV_GROUP_HTML.format(label=label), unsafe_allow_html=True)


def render_sidebar(dataset_path: str | None = None):
    """Render the shared IJMI sidebar and optionally return the dataset path."""
    with st.sidebar:
        sidebar_brand()
        for group, links in NAV_ITEMS:
            nav_group(group)
            for page_path, label in links:
                st.page_link(page_path, label=label)

        st.markdown(
            "<div class='sidebar-footer'><strong>Indian Job Market Intelligence</strong>"
            "<br><span>Python · SQL · Power BI · ML</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border-color:#26354d;margin:12px 0;'>", unsafe_allow_html=True)
        if dataset_path is not None:
            dataset_path = st.text_input(
                "Dataset path",
                value=dataset_path,
                help="Absolute or relative path to indian_job_market.csv",
                label_visibility="collapsed",
            )
            st.caption("97K+ postings · Naukri.com · 2025")
    return dataset_path


def page_header(icon: str, title: str, subtitle: str):
    """Render the page title + subtitle block."""
    category = "Advanced analytics"
    if title in {"Job Market Overview", "Job Demand Analysis", "Skill Intelligence",
                 "Salary Intelligence", "Experience Analysis", "Entry-Level Opportunities",
                 "Company & Location Analysis"}:
        category = "Market intelligence"
    elif title in {"Job Explorer", "Career Skill Gap Analyzer"}:
        category = "Career intelligence"
    elif title == "Dataset & Data Quality":
        category = "Data foundation"
    st.markdown(
        f"""<div class="page-kicker">{category}</div>
            <div class="page-title"><span class="page-mark">{icon}</span>{title}</div>
            <div class="page-subtitle">{subtitle}</div>""",
        unsafe_allow_html=True,
    )


def section(label: str):
    """Render a section divider with accent left border."""
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)


def kpi_row(metrics: list):
    """
    Render a row of KPI cards.
    metrics: list of (label, value, sub_label) tuples.
    """
    cols = st.columns(len(metrics))
    for col, (label, value, sub) in zip(cols, metrics):
        col.markdown(
            f"""<div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{value}</div>
                  <div class="kpi-sub">{sub}</div>
                </div>""",
            unsafe_allow_html=True,
        )


def divider():
    """Subtle dark horizontal rule."""
    st.markdown("<hr class='dark-divider'>", unsafe_allow_html=True)


def insight_card(text: str, icon: str = "\U0001f4a1"):
    """Green-bordered insight box for data-derived observations."""
    st.markdown(
        f'<div class="insight-card">{icon}&nbsp; {text}</div>',
        unsafe_allow_html=True,
    )


def metric_delta(label: str, value, delta=None, delta_label: str = ""):
    """Wrapper around st.metric with optional delta."""
    st.metric(label=label, value=value, delta=delta, help=delta_label or None)


def filter_bar(*args):
    """
    Returns st.columns ready for filter widgets.
    Optionally pass label strings; they are rendered as small uppercase labels above the columns.
    """
    if args:
        cols = st.columns(len(args))
        for col, label in zip(cols, args):
            col.markdown(
                f"<div style='font-size:0.73rem;color:#8b92a8;text-transform:uppercase;"
                f"letter-spacing:0.06em;margin-bottom:4px;'>{label}</div>",
                unsafe_allow_html=True,
            )
        return cols
    return st.columns(1)


# ── Plotly theme ───────────────────────────────────────────────────────────

def apply_chart_style(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply the dark theme to any Plotly figure."""
    fig.update_layout(
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(
            family='"Inter",-apple-system,"Segoe UI",system-ui,sans-serif',
            size=12,
            color=TEXT,
        ),
        margin=dict(l=10, r=10, t=44, b=10),
        title_font=dict(size=13, color=TEXT, family='"Inter",sans-serif'),
        legend=dict(
            bgcolor="#242938",
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(size=11, color=TEXT),
        ),
        xaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            tickfont=dict(size=11, color=MUTED),
            title_font=dict(size=11, color=MUTED),
            zerolinecolor=BORDER,
        ),
        yaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            tickfont=dict(size=11, color=MUTED),
            title_font=dict(size=11, color=MUTED),
            zerolinecolor=BORDER,
        ),
    )
    return fig


def hbar(data, x_col: str, y_col: str, title: str, color: str = PRIMARY,
         height: int = 400, x_label: str = "", y_label: str = "") -> go.Figure:
    """Horizontal bar chart — x_col is the numeric axis, y_col is the category axis."""
    fig = px.bar(
        data.sort_values(x_col),
        x=x_col,
        y=y_col,
        orientation="h",
        title=title,
        color_discrete_sequence=[color],
        labels={x_col: x_label or x_col, y_col: y_label or y_col},
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate=f"<b>%{{y}}</b><br>{x_label or x_col}: %{{x:,}}<extra></extra>",
    )
    return apply_chart_style(fig, height)


def vbar(data, x_col: str, y_col: str, title: str, color: str = PRIMARY,
         height: int = 380, x_label: str = "", y_label: str = "") -> go.Figure:
    """Vertical bar chart."""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color],
        labels={x_col: x_label or x_col, y_col: y_label or y_col},
    )
    fig.update_traces(marker_line_width=0)
    return apply_chart_style(fig, height)


def box_plot(data, x_col: str, y_col: str, title: str, height: int = 450) -> go.Figure:
    """Box plot with dark theme."""
    fig = px.box(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color=x_col,
        color_discrete_sequence=QUAL_COLORS,
        labels={x_col: x_col, y_col: "Salary (LPA)"},
        points=False,
    )
    fig.update_layout(showlegend=False)
    return apply_chart_style(fig, height)


def download_csv_button(df, label: str = "Download Filtered Data as CSV", key: str = "dl"):
    """Styled CSV download button."""
    st.download_button(
        label=f"\u2b07\ufe0f  {label}",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_jobs.csv",
        mime="text/csv",
        key=key,
    )
