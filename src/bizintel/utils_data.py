"""utils_data.py - reusable data loading and inspection functions.

These functions work on any pandas DataFrame.
"""

# === IMPORTS ===

from pathlib import Path

import pandas as pd

from bizintel.utils_logger import LOG

# === PANDAS DISPLAY CONFIGURATION ===

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 120)


# === FUNCTIONS ===


def load_data(filepath: Path, name: str) -> pd.DataFrame:
    """Load one CSV file into a pandas DataFrame.

    WHY: Reading from CSV into a DataFrame is the first step
    in almost every BI pipeline.


    Args:
        filepath: Path to the CSV file.
        name: A short name for logging.

    Returns:
        A pandas DataFrame with the file contents.
    """
    LOG.info(f"Loading {name} from {filepath}")
    df: pd.DataFrame = pd.read_csv(filepath)
    LOG.info(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def inspect_basic(df: pd.DataFrame, name: str) -> None:
    """Log basic structure of a DataFrame.

    WHY: Before analysis, we need to understand what columns
    exist, what types they are, and what the first few rows look like.

    Args:
        df: The DataFrame to inspect.
        name: A short name for logging.

    Returns:
        None
    """
    LOG.info(f"Inspecting {name}")
    LOG.info(f"  Columns: {list(df.columns)}")
    LOG.info(f"  Shape:   {df.shape[0]} rows x {df.shape[1]} columns")
    LOG.debug(f"\n{df.head()}\n")


def check_quality(df: pd.DataFrame, name: str) -> None:
    """Check for missing values and duplicate rows.

    WHY: Real-world data is messy. Knowing what problems exist
    helps us decide how to handle them in the cleaning step.

    Args:
        df: The DataFrame to check.
        name: A short name for logging.

    Returns:
        None
    """
    LOG.info(f"Quality check: {name}")

    missing: pd.Series = df.isna().sum()
    total_missing: int = int(missing.sum())
    LOG.info(f"  Total missing values: {total_missing}")

    if total_missing > 0:
        LOG.warning(f"  Missing by column:\n{missing[missing > 0]}")

    duplicate_count: int = int(df.duplicated().sum())
    LOG.info(f"  Duplicate rows: {duplicate_count}")

    if duplicate_count > 0:
        LOG.warning(
            f"  {duplicate_count} duplicate row(s) found - "
            "review before loading to warehouse"
        )


def summarize_numeric(df: pd.DataFrame, name: str) -> None:
    """Log basic descriptive statistics for numeric columns.

    WHY: Summary statistics give a quick sense of the range
    and distribution of numeric data.
    Unexpected values often signal data quality issues.

    Args:
        df: The DataFrame to summarize.
        name: A short name for logging.

    Returns:
        None
    """
    numeric_cols = df.select_dtypes(include="number")
    if numeric_cols.empty:
        LOG.info(f"  No numeric columns in {name}")
        return

    LOG.info(f"Numeric summary: {name}")
    LOG.info(f"\n{numeric_cols.describe().round(2)}")
