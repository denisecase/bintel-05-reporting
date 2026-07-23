"""olap_spark_case.py - example.

An example of OLAP reporting with Apache Spark.

Spark is a distributed data processing engine.
It is not a replacement for Power BI.

This example uses Spark to perform the same basic OLAP operations
used in the DuckDB reporting example:

    - Slice: focus on one value from one dimension.
    - Dice: focus on selected values from multiple dimensions.
    - Rollup: summarize detailed data at a higher level.
    - Drilldown: move from a summary to more detailed data.

Run olap_case.py first to create the reporting-ready CSV file.

Author: Denise Case
Date: 2026-06

Process:
    - Start a local Spark session.
    - Load the reporting-ready CSV file.
    - Slice sales by one region.
    - Dice sales by region and category.
    - Roll up sales into annual totals.
    - Drill down from annual totals to monthly totals.
    - Visualize the small reporting results.
    - Log a summary of findings.

Data Source:
- data/reporting/sales_reporting_case.csv

Terminal command to run this file from the root project folder:

uv run python -m bizintel.olap_spark_case

OBS:
  Don't edit this file - it should remain a working example.
  Copy it, rename it with your alias, and modify your copy.
  If you do, include your command to run it in the docstring above and in README.md.
"""

# === Section 1. Import dependencies and set up constants ===

# === DECLARE IMPORTS (bring in free code from elsewhere) ===

from pathlib import Path
from typing import Final

from datafun_toolkit.logger import log_path
import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from bizintel.utils_logger import LOG, log_header
from bizintel.utils_viz import plot_bar, plot_line

# === DECLARE GLOBAL CONSTANTS AND CONFIGURATION ===

# Folder containing reporting-ready data.
DATA_REPORTING: Final[Path] = Path("data/reporting")

# Reporting-ready CSV file created by olap_case.py.
REPORTING_FILE: Final[Path] = DATA_REPORTING / "sales_reporting_case.csv"

# Region used in the slice example.
SLICE_REGION: Final[str] = "East"

# Values used in the dice example.
DICE_REGIONS: Final[list[str]] = ["East", "West"]
DICE_CATEGORIES: Final[list[str]] = ["Clothing", "Electronics"]


# === Section 2. Define Reusable Functions ===

# === Section 2.1 DEFINE A CREATE SPARK SESSION FUNCTION ===


def create_spark_session() -> SparkSession:
    """Create a local Spark session.

    WHY: SparkSession is the starting point for working with Spark.
    It allows us to load data and create Spark DataFrames.

    Returns:
        Active SparkSession.
    """
    LOG.info("Creating Spark session")

    spark: SparkSession = (
        SparkSession.builder.appName("SmartSalesOLAP").master("local[*]").getOrCreate()
    )

    # Reduce routine Spark messages in the terminal.
    spark.sparkContext.setLogLevel("WARN")

    LOG.info("  Spark session created")
    return spark


# === Section 2.2 DEFINE A LOAD REPORTING DATA FUNCTION ===


def load_reporting_data(
    spark: SparkSession,
    file_path: Path,
) -> DataFrame:
    """Load reporting data into a Spark DataFrame.

    WHY: The reporting file already contains the sales facts
    joined with customer and product information.

    Args:
        spark: Active SparkSession.
        file_path: Path to the reporting CSV file.

    Returns:
        Spark DataFrame containing reporting data.
    """
    LOG.info("Loading reporting data")

    # header=True uses the first row as column names.
    # inferSchema=True asks Spark to detect data types.
    df_reporting: DataFrame = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(str(file_path))
    )

    LOG.info(f"  Loaded {df_reporting.count()} rows")
    return df_reporting


# === Section 2.3 DEFINE A SLICE FUNCTION ===

# Slice: filter one dimension to one selected value.
#
# We answer:
# What are total sales by category in one selected region?
#
# Use a slice when you want to focus on one business segment.


def slice_by_region(
    df_reporting: DataFrame,
    selected_region: str,
) -> DataFrame:
    """Slice sales by one selected region.

    Args:
        df_reporting: Complete reporting DataFrame.
        selected_region: Region to include.

    Returns:
        Spark DataFrame with Region, Category, and TotalSales.
    """
    LOG.info(f"Spark OLAP slice: {selected_region}")

    # filter() keeps only rows for the selected region.
    df_selected: DataFrame = df_reporting.filter(F.col("Region") == selected_region)

    # groupBy() creates one group for each category.
    # sum() calculates total sales for each group.
    df_slice: DataFrame = (
        df_selected.groupBy("Region", "Category")
        .agg(
            F.round(
                F.sum("SaleAmount"),
                2,
            ).alias("TotalSales")
        )
        .orderBy(F.desc("TotalSales"))
    )

    return df_slice


# === Section 2.4 DEFINE A DICE FUNCTION ===

# Dice: filter two or more dimensions.
#
# We answer:
# Which selected region and category combinations
# produce the highest sales?
#
# Use a dice when you want to examine a specific
# multidimensional subset of the data.


def dice_by_region_and_category(
    df_reporting: DataFrame,
    selected_regions: list[str],
    selected_categories: list[str],
) -> DataFrame:
    """Dice sales by selected regions and categories.

    Args:
        df_reporting: Complete reporting DataFrame.
        selected_regions: Regions to include.
        selected_categories: Categories to include.

    Returns:
        Spark DataFrame with Region, Category, and TotalSales.
    """
    LOG.info("Spark OLAP dice: region and category")

    # isin() keeps rows whose values appear in the selected lists.
    df_selected: DataFrame = df_reporting.filter(
        F.col("Region").isin(selected_regions)
        & F.col("Category").isin(selected_categories)
    )

    df_dice: DataFrame = (
        df_selected.groupBy("Region", "Category")
        .agg(
            F.round(
                F.sum("SaleAmount"),
                2,
            ).alias("TotalSales")
        )
        .orderBy(F.desc("TotalSales"))
    )

    return df_dice


# === Section 2.5 DEFINE A ROLLUP FUNCTION ===

# Rollup: move from detailed data to a higher-level summary.
#
# We answer:
# What are total sales for each year?
#
# Use a rollup when managers need a broader summary
# instead of detailed monthly or transaction-level data.


def rollup_yearly_sales(
    df_reporting: DataFrame,
) -> DataFrame:
    """Roll up sales into yearly totals.

    Args:
        df_reporting: Complete reporting DataFrame.

    Returns:
        Spark DataFrame with SalesYear and TotalSales.
    """
    LOG.info("Spark OLAP rollup: yearly sales")

    df_yearly: DataFrame = (
        df_reporting.groupBy("SalesYear")
        .agg(
            F.round(
                F.sum("SaleAmount"),
                2,
            ).alias("TotalSales")
        )
        .orderBy("SalesYear")
    )

    return df_yearly


# === Section 2.6 DEFINE A DRILLDOWN FUNCTION ===

# Drilldown: move from a summary to more detail.
#
# We answer:
# What do monthly sales look like inside one selected year?
#
# Use drilldown when a summary raises more questions.
# A yearly total may hide strong and weak months.


def drilldown_monthly_sales(
    df_reporting: DataFrame,
    selected_year: int,
) -> DataFrame:
    """Drill down from yearly sales to monthly sales.

    Args:
        df_reporting: Complete reporting DataFrame.
        selected_year: Year to investigate.

    Returns:
        Spark DataFrame with YearMonth and TotalSales.
    """
    LOG.info(f"Spark OLAP drilldown: monthly sales for {selected_year}")

    # First, filter to one selected year.
    df_selected_year: DataFrame = df_reporting.filter(
        F.col("SalesYear") == selected_year
    )

    # Then group the selected year by month.
    df_monthly: DataFrame = (
        df_selected_year.groupBy("YearMonth")
        .agg(
            F.round(
                F.sum("SaleAmount"),
                2,
            ).alias("TotalSales")
        )
        .orderBy("YearMonth")
    )

    return df_monthly


# === Section 2.7 DEFINE A SUMMARIZE FUNCTION ===


def summarize(
    df_slice: pd.DataFrame,
    df_dice: pd.DataFrame,
    df_yearly: pd.DataFrame,
    df_monthly: pd.DataFrame,
    selected_region: str,
    selected_year: int,
) -> None:
    """Log a brief summary of Spark OLAP findings.

    Args:
        df_slice: Slice result converted to pandas.
        df_dice: Dice result converted to pandas.
        df_yearly: Rollup result converted to pandas.
        df_monthly: Drilldown result converted to pandas.
        selected_region: Region used in the slice.
        selected_year: Year used in the drilldown.

    Returns:
        None
    """
    LOG.info("========================")
    LOG.info("SPARK SUMMARY")
    LOG.info("========================")

    # First row contains the largest value
    # because the slice was sorted descending.
    top_category: str = str(df_slice.iloc[0]["Category"])
    top_category_sales: float = float(df_slice.iloc[0]["TotalSales"])

    LOG.info(
        f"Slice: In {selected_region}, the leading category is "
        f"{top_category} (${top_category_sales:,.2f})"
    )

    top_region: str = str(df_dice.iloc[0]["Region"])
    top_dice_category: str = str(df_dice.iloc[0]["Category"])
    top_dice_sales: float = float(df_dice.iloc[0]["TotalSales"])

    LOG.info(
        "Dice: The strongest selected combination is "
        f"{top_region} / {top_dice_category} "
        f"(${top_dice_sales:,.2f})"
    )

    best_year: int = int(
        df_yearly.loc[
            df_yearly["TotalSales"].idxmax(),
            "SalesYear",
        ]
    )

    best_year_sales: float = float(df_yearly["TotalSales"].max())

    LOG.info(f"Rollup: The strongest year is {best_year} (${best_year_sales:,.2f})")

    best_month: str = str(
        df_monthly.loc[
            df_monthly["TotalSales"].idxmax(),
            "YearMonth",
        ]
    )

    best_month_sales: float = float(df_monthly["TotalSales"].max())

    LOG.info(
        f"Drilldown: The strongest month in {selected_year} is "
        f"{best_month} (${best_month_sales:,.2f})"
    )

    LOG.info("========================")
    LOG.info("ANALYST NOTES:")
    LOG.info("Slice focuses on one dimension value.")
    LOG.info("Dice filters multiple dimensions.")
    LOG.info("Rollup creates a higher-level summary.")
    LOG.info("Drilldown reveals more detailed results.")
    LOG.info("========================")


# === DEFINE THE MAIN FUNCTION (WHERE THE MAGIC HAPPENS) ===


def main() -> None:
    """Main function to run the Spark OLAP logic.

    This is where the main logic starts
    when this script is run.
    """

    # First, log the header for the BI module.
    log_header(LOG, "BI")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "Reporting data:", REPORTING_FILE)

    LOG.info("CALL a function to create a Spark session........")
    spark: SparkSession = create_spark_session()

    LOG.info("CALL a function to load reporting data........")
    df_reporting: DataFrame = load_reporting_data(
        spark,
        REPORTING_FILE,
    )

    LOG.info("CALL a function to slice sales by region........")
    df_slice_spark: DataFrame = slice_by_region(
        df_reporting,
        SLICE_REGION,
    )

    LOG.info("SHOW the slice result........")
    df_slice_spark.show()

    # The OLAP result is small after aggregation,
    # so it is safe to convert it to pandas for plotting.
    df_slice: pd.DataFrame = df_slice_spark.toPandas()

    LOG.info("CALL a function to plot the slice result........")
    plot_bar(
        df=df_slice,
        x="Category",
        y="TotalSales",
        title=f"Sales by Category in {SLICE_REGION}",
        xlabel="Category",
        ylabel="Total Sales ($)",
        palette="Blues_d",
    )

    LOG.info("CALL a function to dice sales by region and category........")
    df_dice_spark: DataFrame = dice_by_region_and_category(
        df_reporting,
        DICE_REGIONS,
        DICE_CATEGORIES,
    )

    LOG.info("SHOW the dice result........")
    df_dice_spark.show()

    df_dice: pd.DataFrame = df_dice_spark.toPandas()

    # Create one readable label for each combination.
    df_dice["RegionCategory"] = (
        df_dice["Region"].astype(str) + " / " + df_dice["Category"].astype(str)
    )

    LOG.info("CALL a function to plot the dice result........")
    plot_bar(
        df=df_dice,
        x="RegionCategory",
        y="TotalSales",
        title="Selected Region and Category Sales",
        xlabel="Region / Category",
        ylabel="Total Sales ($)",
        palette="Greens_d",
    )

    LOG.info("CALL a function to roll up yearly sales........")
    df_yearly_spark: DataFrame = rollup_yearly_sales(df_reporting)

    LOG.info("SHOW the rollup result........")
    df_yearly_spark.show()

    df_yearly: pd.DataFrame = df_yearly_spark.toPandas()

    LOG.info("CALL a function to plot yearly sales........")
    plot_bar(
        df=df_yearly,
        x="SalesYear",
        y="TotalSales",
        title="Yearly Sales Rollup",
        xlabel="Year",
        ylabel="Total Sales ($)",
        palette="Blues_d",
    )

    # Use the most recent year for the drilldown example.
    selected_year_row = df_reporting.agg(F.max("SalesYear").alias("LatestYear")).first()

    selected_year: int = int(selected_year_row["LatestYear"])

    LOG.info("CALL a function to drill down to monthly sales........")
    df_monthly_spark: DataFrame = drilldown_monthly_sales(
        df_reporting,
        selected_year,
    )

    LOG.info("SHOW the drilldown result........")
    df_monthly_spark.show()

    df_monthly: pd.DataFrame = df_monthly_spark.toPandas()

    LOG.info("CALL a function to plot monthly sales........")
    plot_line(
        df=df_monthly,
        x="YearMonth",
        y="TotalSales",
        title=f"Monthly Sales Drilldown for {selected_year}",
        xlabel="Month",
        ylabel="Total Sales ($)",
    )

    LOG.info("CALL a function to summarize findings........")
    summarize(
        df_slice,
        df_dice,
        df_yearly,
        df_monthly,
        SLICE_REGION,
        selected_year,
    )

    LOG.info("CALL a function to show charts........")
    plt.show()

    # Stop Spark when the work is complete.
    spark.stop()

    LOG.info("Spark workflow complete")
    LOG.info("CLOSE chart windows to continue.")
    LOG.info("Terminate this process with CTRL+c as needed.")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    # This conditional ensures that the main() function is only executed
    # when this script is run directly, not when it is imported as a module.
    main()
