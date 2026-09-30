"""
data_loader.py — Responsible for reading the CSV from disk and returning
a raw DataFrame. Keeps I/O separate from cleaning logic.

NOTE: No Streamlit imports here. Caching (@st.cache_data) is applied
by callers (app.py, pages) that run inside the Streamlit runtime.
"""

import os
import pandas as pd

# Default path relative to the project root
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "indian_job_market.csv")


def load_raw_data(filepath: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the raw CSV dataset and return as a DataFrame.
    Raises FileNotFoundError with a friendly message if the file is missing.
    Pure function — no Streamlit dependency.
    """
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at: {filepath}\n"
            "Please place 'indian_job_market.csv' inside the 'data/' folder."
        )
    df = pd.read_csv(filepath, low_memory=False)
    return df


def get_dataset_info(df: pd.DataFrame) -> dict:
    """Return a summary dict about the raw dataset for display purposes."""
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "null_counts": df.isnull().sum().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "duplicates": df.duplicated().sum(),
    }
