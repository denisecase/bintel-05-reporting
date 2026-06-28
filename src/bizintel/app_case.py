"""app_case.py - example.

An example of a supervised regression case.
This app is used to verify project workflow.

Author: Denise Case
Date: 2026-06

Process:
    - Load a CSV dataset.
    - Train a supervised regression model.
    - Evaluate model performance.
    - Predict one new case.
    - Create useful charts.

Data Source:
- data/raw/hours_scores_case.csv

Terminal command to run this file from the root project folder:

uv run python -m bizintel.app_case

OBS:
  Don't edit this file - it should remain a working example.
  It is used in each module to test the installation and workflow.
  You never need to do anything with it, but if would like,
  you can copy it, rename it, and modify your copy.
  If you do, include your command to run it in the docstring above and in README.md.
"""

# === Section 1a. DECLARE IMPORTS (BRING IN FREE CODE) ===

import logging
from typing import Final

from datafun_toolkit.logger import get_logger, log_header
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# === Section 1b. CONFIGURE LOGGER ONCE PER MODULE ===

LOG: logging.Logger = get_logger("ML", level="DEBUG")
log_header(LOG, "ML")

# === Section 1c. Global Constants and Configuration ===

DATASET_NAME: Final[str] = "hours_scores_case"

# Important: Inspect your dataset to identify feature and target column names.
# Raw data is typically in data/raw.
# You can assume this data has already been cleaned and preprocessed for modeling,
# but you should still inspect it to understand the column names and data types.

# STEP 1. Pick the target variable we want to predict.

TARGET_COL: Final[str] = "score"

# STEP 2. Define the column names (features) that may help predict the target variable.

FEATURE_COLS: Final[list[str]] = [
    "hours_studied",
    "practice_quizzes",
    "attendance_pct",
    "sleep_hours",
    "prior_score",
]

# STEP 3. Define the test size and random state for reproducibility.

# For a small dataset, use a larger test size (e.g., 0.30 or 0.40)
# to get a more reliable estimate of model performance.

# 0.30 means: hold back 30% of the records for testing, and train the model on the other 70%.
# So for every 10 records:
# 7 records -> training
# 3 records -> testing

# The model learns from the training records,
# then we check how well it predicts the test records it did not train on.

TEST_SIZE: Final[float] = 0.30
RANDOM_STATE: Final[int] = 42

# RANDOM_STATE controls the random split.
# Without it, every run might choose a different 70/30 split.
# With it, we get the same split every time, so results always match.
# The value 42 is arbitrary and conventional. We can choose any integer.

# === Section 1d. Pandas Configuration for Display ===

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 120)


# === Section 2. Load the Data ===


def load_data() -> pd.DataFrame:
    """Load the case dataset from the data/raw folder."""
    LOG.info(f"Loading dataset: {DATASET_NAME}")

    df: pd.DataFrame = pd.read_csv(f"data/raw/{DATASET_NAME}.csv")

    LOG.info(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    LOG.debug(f"\n{df.head()}")

    return df


# === Section 3. Inspect Data Shape and Structure ===


def inspect_basic(df: pd.DataFrame) -> None:
    """Inspect basic dataset structure."""
    LOG.info("Column names")
    LOG.debug(f"{list(df.columns)}")

    LOG.info("DataFrame info")
    df.info()

    LOG.info(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")


# === Section 4. Check Data Quality ===


def check_quality(df: pd.DataFrame) -> None:
    """Check missing values and duplicate rows."""
    LOG.info("Missing values by column")
    LOG.debug(f"\n{df.isna().sum()}")

    duplicate_count: int = df.duplicated().sum()
    LOG.info(f"Duplicate row count: {duplicate_count}")


# === Section 5. Create a Clean View ===


def make_clean_view(df: pd.DataFrame) -> pd.DataFrame:
    """Create a cleaned view for modeling."""
    LOG.info("Creating clean modeling view")

    selected_cols: list[str] = FEATURE_COLS + [TARGET_COL]

    # Select only the columns we need.
    df_selected: pd.DataFrame = df[selected_cols]  # type: ignore[assignment]

    # Drop rows with any missing values.
    df_no_missing: pd.DataFrame = df_selected.dropna()

    # Assign a copy of the no-missing DataFrame to df_clean to avoid SettingWithCopyWarning.
    df_clean: pd.DataFrame = df_no_missing.copy()

    LOG.info(f"Clean view: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
    return df_clean


# === Section 6. Train Supervised Model ===


def train_model(df_clean: pd.DataFrame) -> LinearRegression:
    """Train a supervised regression model."""
    LOG.info("Training LinearRegression model")

    x = df_clean[FEATURE_COLS]
    y = df_clean[TARGET_COL]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    model = LinearRegression()
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    mae: float = mean_absolute_error(y_test, y_pred)
    r2: float = r2_score(y_test, y_pred)

    LOG.info(f"Mean absolute error: {mae:.2f}")
    LOG.info(f"R-squared: {r2:.2f}")

    return model


# === Section 7. Predict One New Case ===


def predict_example(model: LinearRegression) -> None:
    """Use the trained model to predict one new student score."""
    LOG.info("Predicting one new case")

    new_case = pd.DataFrame(
        [
            {
                "hours_studied": 6.5,
                "practice_quizzes": 4,
                "attendance_pct": 92,
                "sleep_hours": 7.0,
                "prior_score": 72,
            }
        ]
    )

    predicted_score: float = model.predict(new_case)[0]

    LOG.info(f"New case:\n{new_case}")
    LOG.info(f"Predicted score: {predicted_score:.1f}")


# === Section 8. Create Visualizations ===


def make_plots(df_clean: pd.DataFrame, model: LinearRegression) -> None:
    """Create charts for the supervised regression case."""
    LOG.info("Creating chart: hours studied vs score")

    fig, ax = plt.subplots(figsize=(9, 5))

    scatter_plt: Axes = sns.scatterplot(
        data=df_clean,
        x="hours_studied",
        y=TARGET_COL,
        ax=ax,
    )

    scatter_plt.set_title("Hours Studied vs Score (CLOSE chart to continue)")
    scatter_plt.set_xlabel("Hours Studied")
    scatter_plt.set_ylabel("Score")

    LOG.info("Creating chart: model coefficients")

    fig, ax = plt.subplots(figsize=(9, 5))

    LOG.info(f"Got a figure {fig} and axes {ax} from plt.subplots().")

    coefficient_df = pd.DataFrame(
        {
            "feature": FEATURE_COLS,
            "coefficient": model.coef_,
        }
    ).sort_values("coefficient", ascending=False)

    bar_plt: Axes = sns.barplot(
        data=coefficient_df,
        x="coefficient",
        y="feature",
        ax=ax,
    )

    bar_plt.set_title("Model Coefficients (CLOSE chart to continue)")
    bar_plt.set_xlabel("Coefficient")
    bar_plt.set_ylabel("Feature")


# === Section 9. Summary and Next Steps ===


def summarize(df: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    """Log a brief summary."""
    LOG.info("========================")
    LOG.info("SUMMARY")
    LOG.info("========================")
    LOG.info(f"Dataset: {DATASET_NAME}")
    LOG.info(f"Original rows: {df.shape[0]}")
    LOG.info(f"Clean rows: {df_clean.shape[0]}")
    LOG.info(f"Features: {FEATURE_COLS}")
    LOG.info(f"Target: {TARGET_COL}")


# === DEFINE THE MAIN FUNCTION THAT CALLS OTHER FUNCTIONS ===


def main() -> None:
    """Main function to run the supervised ML workflow."""
    log_header(LOG, "ML")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    LOG.info("Load dataset..............")
    df = load_data()

    LOG.info("Inspect dataset...........")
    inspect_basic(df)

    LOG.info("Check data quality........")
    check_quality(df)

    LOG.info("Create clean view.........")
    df_clean = make_clean_view(df)

    LOG.info("Train supervised model....")
    model = train_model(df_clean)

    LOG.info("Predict one case..........")
    predict_example(model)

    LOG.info("Create charts.............")
    make_plots(df_clean, model)

    LOG.info("Summarize workflow........")
    summarize(df, df_clean)

    LOG.info(
        "----- in a script, call plt.show() once at the end to display all charts -----"
    )
    LOG.info(
        "----- in a script, CLOSE the chart windows with the close button to CONTINUE -----"
    )

    plt.show()

    LOG.info("Workflow complete")
    LOG.info("IMPORTANT: This script creates chart windows.")
    LOG.info("Close chart windows and terminate this process with CTRL+c as needed.")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

# WHY: Only call main() when running this file directly as a script.
# This is standard Python boilerplate.

if __name__ == "__main__":
    main()
