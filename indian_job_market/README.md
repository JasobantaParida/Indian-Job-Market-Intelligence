# 🇮🇳 Indian Job Market Intelligence & Career Analytics Platform

> A comprehensive Data Analyst portfolio project — interactive analytics dashboard, SQL analytics, statistical analysis, machine learning, and career skill gap analysis for the **Indian Job Market 2025** dataset (97K+ job postings from Naukri.com).

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Project Overview

This project transforms raw job posting data into a fully interactive analytics platform. It demonstrates end-to-end data analyst skills: data cleaning, feature engineering, exploratory data analysis, SQL querying, statistical analysis, machine learning, and business storytelling through interactive dashboards.

**Every chart answers a real business or career question.** No decorative visualizations.

---

## 🎯 Problem Statement

Job seekers and data professionals in India struggle with:
- **Where are the jobs?** — Which cities and companies are hiring the most?
- **What skills do I need?** — Which skills are actually in demand vs. what I read in blogs?
- **What salary should I expect?** — Salary transparency is low; how do I benchmark?
- **How ready am I?** — How do my current skills compare to what employers want?

This platform answers all of these questions using real job posting data.

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| **Source** | https://www.kaggle.com/datasets/shivamshrivastava21/indian-job-market-dataset-2025-2026?utm_source=chatgpt.com |
| **Raw Rows** | 97,929 |
| **Duplicate Rows Removed** | 247 |
| **Clean Rows** | 97,682 |
| **Columns** | 17 |
| **Salary Disclosed** | ~33,553 rows (~34%) |
| **Companies** | 18,624 unique employers |
| **Locations** | 1,498 unique cities |

### Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| `title` | text | Job title / role name |
| `companyName` | text | Employer name |
| `location` | text | Raw multi-city location string |
| `tagsAndSkills` | text | Comma-separated skills and tags |
| `experience` | text | Experience range string (e.g. "2–4 Yrs") |
| `minimumExperience` | int | Minimum years required |
| `maximumExperience` | int | Maximum years required |
| `salary` | text | Salary string (e.g. "3–5 Lacs PA") |
| `minimumSalary` | int | Minimum salary in INR |
| `maximumSalary` | int | Maximum salary in INR |
| `currency` | text | INR or USD |
| `jobUploaded` | text | Relative posting time (e.g. "4 Days Ago") |
| `AggregateRating` | float | Company rating (1–5) |
| `ReviewsCount` | float | Number of company reviews |

---

## 🎯 Objectives

1. Understand job demand patterns across roles, cities, and experience levels
2. Identify the most in-demand skills and skill combinations
3. Analyze salary distributions and what drives compensation
4. Build a machine learning model to estimate salary from job profile features
5. Help job seekers identify skill gaps for their target role
6. Provide an interactive job search tool for filtering 97K+ postings
7. Demonstrate SQL analytics against a structured dataset
8. Apply statistical methods including descriptive statistics, correlation, and ANOVA

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.10+ |
| **Web Framework** | Streamlit |
| **Data Manipulation** | Pandas, NumPy |
| **Visualization** | Plotly Express & Graph Objects |
| **SQL** | SQLite (in-memory, via Python stdlib) |
| **Statistics** | SciPy (ANOVA, descriptive stats) |
| **Machine Learning** | Scikit-learn (LinearRegression, RandomForest, GradientBoosting) |

---

## 🧹 Data Cleaning

The following cleaning steps are applied in [`src/data_cleaning.py`](src/data_cleaning.py):

| Step | Description |
|------|-------------|
| **Deduplication** | 247 exact duplicate rows removed |
| **Salary: zero → NaN** | `minimumSalary = 0` treated as "not disclosed" |
| **USD → INR** | USD salaries multiplied by ₹83 fixed conversion rate |
| **Salary outlier cap** | 99th percentile cap applied to `average_salary` |
| **Swap check** | Rows where min > max salary are corrected |
| **Experience 0–0 → NaN** | Both experience fields = 0 treated as undisclosed |
| **Location parsing** | Multi-city strings parsed to a single `primary_location` |
| **Relative date parsing** | `"4 Days Ago"` → `days_ago = 4` (integer) |
| **Company name normalisation** | Strips whitespace; fills blank/nan with "Unknown" |
| **Title normalisation** | Collapses multiple spaces, strips whitespace |

---

## ⚙️ Feature Engineering

Implemented in [`src/feature_engineering.py`](src/feature_engineering.py):

| Feature | Description |
|---------|-------------|
| `experience_group` | Bucketed from `minimumExperience`: Fresher / 0–2 / 2–5 / 5–8 / 8+ Yrs |
| `average_salary_lpa` | `(minimumSalary + maximumSalary) / 2 / 100,000` — in Lakhs Per Annum |
| `minimumSalary_lpa` | Minimum salary in LPA |
| `maximumSalary_lpa` | Maximum salary in LPA |
| `is_fresher` | Boolean: `minimumExperience == 0` |
| `skills_list` | Parsed list of canonical skills from `tagsAndSkills` |

---

## 🔍 Exploratory Data Analysis

Pages 1–7 provide full EDA covering:
- Market overview KPIs (total jobs, companies, locations, salary)
- Top roles, companies, and cities by posting frequency
- Job posting recency (days ago distribution)
- Demand heatmaps (role × city)
- Salary distributions with histograms and box plots
- Experience level breakdowns
- Company ratings analysis

---

## 🛠️ Skill Intelligence

[`src/skill_extraction.py`](src/skill_extraction.py) maps 100+ raw skill strings to canonical technology names using pattern matching:

- **100+ canonical skills** including Python, SQL, Java, AWS, Azure, Power BI, Tableau, Machine Learning, and more
- **Top skills by frequency** — overall and filtered by role/location/experience
- **Skill co-occurrence matrix** — which skills appear together most often
- **Skill × role heatmap** — what each role specifically demands
- **Skill × experience heatmap** — how requirements evolve with seniority

**Top skills found (from actual data):** SAP (7,036), Java (7,008), SQL (6,252), Python (5,936), Project Management (5,742)

---

## 💰 Salary Intelligence

Key findings (based on disclosed salary data, ~34% of postings):
- **Mean salary:** ₹7.05 LPA
- **Median salary:** ₹4.20 LPA (right-skewed distribution)
- **Fresher average:** ₹3.54 LPA

Analysis includes salary by role, location, experience level, and skill using box plots and bar charts.

---

## 🗄️ SQL Analytics

[`src/sql_analysis.py`](src/sql_analysis.py) loads the cleaned DataFrame into an **in-memory SQLite database** and runs 12 pre-built queries demonstrating:

- `GROUP BY` + `HAVING` for aggregated filtering
- CTEs (`WITH` clause) for readability
- `CASE WHEN` logic in query patterns
- String matching with `LIKE`
- Multi-table window-function style aggregation

No external database server required — runs entirely in memory.

---

## 📈 Statistical Analysis

[`src/statistics_analysis.py`](src/statistics_analysis.py) provides:

- Full descriptive statistics (mean, median, mode, std, variance, IQR, skewness, kurtosis)
- IQR-based outlier detection and bounds
- Salary percentile table (P5 through P99)
- Group comparison statistics (salary by experience, by role)
- Pearson correlation matrix across all numeric features
- One-way ANOVA: salary differences across experience groups (F=5,354.5, p<0.001)

> **Note:** With ~100K records, almost any real difference will be statistically significant. ANOVA results are presented as descriptive evidence, not causal proof.

---

## 🤖 Machine Learning — Salary Prediction

[`src/ml_salary_prediction.py`](src/ml_salary_prediction.py) trains three models on disclosed salary data:

| Model | MAE (LPA) | RMSE (LPA) | R² |
|-------|-----------|------------|-----|
| Linear Regression | 3.31 | 5.64 | 0.399 |
| Random Forest | 2.95 | 5.26 | **0.477** |
| Gradient Boosting | 2.97 | 5.25 | **0.477** |

**Features used:** `minimumExperience`, `maximumExperience`, `title` (top-50), `primary_location` (top-50)

**Pipeline:** `ColumnTransformer` (median imputation + ordinal encoding) → model

> **Limitation:** Only ~34% of postings disclosed salary, so the model trains on a biased subset. Predictions are directional estimates only.

---

## 🎯 Career Skill Gap Analysis

[`src/career_analysis.py`](src/career_analysis.py) supports 17 target roles including:

- Data Analyst, Business Analyst, Data Scientist
- Machine Learning Engineer, Data Engineer
- Software Developer, Python Developer, Java Developer
- Full Stack, Backend, Frontend Developer
- DevOps Engineer, Financial Analyst, Project Manager

For each role: shows demand frequency per skill, compares against user's self-reported skills, displays skill gaps ranked by posting frequency, and shows common skill co-occurrence pairs.

---

## 🔎 Interactive Job Explorer

[`pages/13_Job_Explorer.py`](pages/13_Job_Explorer.py) provides:
- Full-text search on job title, company, and skills
- Filters: location, experience level, salary range, minimum rating
- Sort by salary (high/low), rating, title, or company
- Pagination with configurable rows per page (25–200)
- CSV export of all filtered results

Optimized for ~100K rows using Pandas vectorized filtering.

---

## 📁 Dashboard Pages

| # | Page | Key Questions Answered |
|---|------|------------------------|
| 1 | 📊 Job Market Overview | Total market size, top roles, companies, cities, time trends |
| 2 | 🔍 Job Demand Analysis | Which roles/cities/experience levels are hottest? |
| 3 | 🛠️ Skill Intelligence | What skills are in demand? What skills co-occur? |
| 4 | 💰 Salary Intelligence | Salary distributions, benchmarks by role/city/skill |
| 5 | 📈 Experience Analysis | How do jobs and salaries differ by seniority? |
| 6 | 🌱 Fresher Opportunities | Entry-level jobs, companies, cities, skills for new grads |
| 7 | 🏢 Company & Location | Top employers, city rankings, company ratings |
| 8 | 📁 Dataset & Data Quality | Data cleaning report, missing values, quality metrics |
| 9 | 🗄️ SQL Analytics | 12 pre-built SQL queries + custom SQL editor |
| 10 | 📈 Statistical Insights | Descriptive stats, correlations, ANOVA |
| 11 | 🤖 Salary Prediction | ML model training, evaluation, interactive predictor |
| 12 | 🎯 Career Skill Gap | Select role, input skills, see gap analysis |
| 13 | 🔎 Job Explorer | Interactive search across 97K+ postings |

---

## 🏗️ Project Architecture

```
indian_job_market/
├── app.py                              # Main entry point + home page
├── pages/
│   ├── 1_Job_Market_Overview.py        # Market snapshot & KPIs
│   ├── 2_Job_Demand.py                 # Demand analysis
│   ├── 3_Skill_Intelligence.py         # Skill analysis
│   ├── 4_Salary_Intelligence.py        # Salary analysis
│   ├── 5_Experience_Analysis.py        # Experience analysis
│   ├── 6_Fresher_Jobs.py               # Entry-level analysis
│   ├── 7_Company_Location.py           # Company & location analysis
│   ├── 8_Dataset_Quality.py            # Data quality report
│   ├── 9_SQL_Analytics.py              # SQL analytics
│   ├── 10_Statistical_Insights.py      # Statistical analysis
│   ├── 11_Salary_Prediction.py         # ML salary prediction
│   ├── 12_Career_Skill_Gap.py          # Career skill gap analyzer
│   └── 13_Job_Explorer.py              # Interactive job explorer
├── src/
│   ├── __init__.py
│   ├── data_loader.py                  # CSV loading & caching
│   ├── data_cleaning.py                # Preprocessing & cleaning
│   ├── feature_engineering.py          # Derived columns
│   ├── analysis.py                     # Aggregation helpers
│   ├── skill_extraction.py             # Skill parsing & mapping
│   ├── sql_analysis.py                 # SQLite integration & queries
│   ├── statistics_analysis.py          # Statistical functions
│   ├── ml_salary_prediction.py         # ML training & inference
│   ├── career_analysis.py              # Skill gap analysis
│   └── ui_helpers.py                   # Shared UI components
├── data/
│   └── indian_job_market.csv           # Dataset (97K+ rows)
├── .streamlit/
│   └── config.toml                     # Theme configuration
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd indian_job_market
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Place the dataset

Ensure the dataset is at:
```
data/indian_job_market.csv
```

### 4. Run the application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## ⚠️ Limitations

| Limitation | Details |
|-----------|---------|
| **Salary coverage** | Only ~34% of postings disclosed salary. All salary insights reflect a non-random subset. |
| **Salary not actual pay** | Disclosed values are employer-posted ranges, not actual paid salaries. |
| **Dataset coverage** | Data is from Naukri.com only. Other job portals (LinkedIn, Indeed, etc.) are not included. |
| **Relative dates** | `jobUploaded` values like "4 Days Ago" cannot be mapped to calendar dates, making true time-series analysis impossible. |
| **Currency conversion** | USD→INR uses a fixed rate of ₹83. |
| **Duplicate postings** | Some companies repost the same role multiple times. 247 exact duplicates were removed, but near-duplicates may remain. |
| **Skill extraction** | Skills are extracted via keyword matching, not NLP. Synonyms or unusual phrasings may be missed. |
| **ML model** | R²≈0.47 means ~47% of salary variance is explained by the features used. Many external factors (company size, negotiation, actual role level) are not captured. |
| **Disclaimer** | Insights describe patterns within this dataset and should not be interpreted as a complete representation of the entire Indian job market. |

---

## 🔮 Future Improvements

| Area | Improvement |
|------|------------|
| **NLP** | Use transformer models (BERT/spaCy) for job description analysis |
| **Skill extraction** | Semantic skill extraction beyond keyword matching |
| **Recommendation** | "Jobs similar to your profile" recommendation engine |
| **Live data** | Integration with job APIs for real-time data |
| **Career paths** | Role transition analysis (which roles lead to which?) |
| **Industry segmentation** | Classify jobs into industry sectors (IT, Finance, Healthcare, etc.) |
| **Salary negotiation** | Confidence intervals and negotiation range recommendations |
| **Geo visualization** | Map-based location visualizations using India state shapefiles |

---

## 👤 Author

Built as a **Data Analyst Portfolio Project** demonstrating:
- End-to-end data pipeline (load → clean → feature engineer → analyze)
- SQL analytics using in-memory SQLite
- Statistical analysis including ANOVA
- Machine learning with scikit-learn
- Interactive dashboard development with Streamlit & Plotly
- Career analytics and skill gap analysis

---

*Data Source: Naukri.com · Indian Job Market Dataset 2025 · 97,929 raw rows · 97,682 clean rows*
