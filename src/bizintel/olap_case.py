"""olap_case.py - example.

An example of OLAP reporting on a data warehouse.

OLAP stands for Online Analytical Processing.
OLAP techniques help us examine business measures
across different dimensions and levels of detail.

Author: Denise Case
Date: 2026-07

Process:
- Connect to the DuckDB data warehouse.
- Create a reporting view that joins facts and dimensions.
- Export a reporting-ready dataset for Power BI or Spark.
- Slice sales by selecting one region.
- Dice sales by selecting multiple regions and categories.
- Roll up monthly sales into quarterly and annual summaries.
- Drill down from annual sales to quarterly and monthly detail.
- Visualize OLAP results with business charts.
- Log a summary of findings.

Data Source:
- artifacts/smart_sales.duckdb

Output:
- data/reporting/sales_reporting_case.csv

Terminal command to run this file from the root project folder:

uv run python -m bizintel.olap_case

OBS:
  Don't edit this file - it should remain a working example.
  Copy it, rename it with your alias, and modify your copy.
  If you do, include your command to run it in the docstring above and in README.md.
"""

# === Section 1. Import dependencies and set up constants ===

# === IMPORTS ===

from pathlib import Path
from typing import Final

from datafun_toolkit.logger import log_path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

from bizintel.utils_logger import LOG, log_header
from bizintel.utils_viz import plot_bar, plot_line

# === DECLARE CONSTANTS ===

# Path to the DuckDB data warehouse.
DW_FILE: Final[Path] = Path("artifacts/smart_sales.duckdb")

# Folder for reporting-ready data.
DATA_REPORTING: Final[Path] = Path("data/reporting")

# Reporting-ready CSV file used by Power BI or Spark.
REPORTING_FILE: Final[Path] = DATA_REPORTING / "sales_reporting_case.csv"

# A slice selects one value from one dimension.
# Change this value in your copied file to investigate another region.
SLICE_REGION: Final[str] = "East"

# A dice selects values from two or more dimensions.
# Change these values in your copied file to investigate another data subset.
DICE_REGIONS: Final[tuple[str, ...]] = ("East", "West")
DICE_CATEGORIES: Final[tuple[str, ...]] = ("Clothing", "Electronics")


# === Section 2. Define Reusable Functions ===

# === Section 2.1 DEFINE A VERIFY WAREHOUSE FUNCTION ===


def verify_warehouse(conn: duckdb.DuckDBPyConnection) -> None:
    """Verify that the required warehouse tables exist.

    WHY: Connecting to a missing DuckDB file creates a new empty database.
    We verify the file and required tables before running reporting queries
    so students receive a useful message instead of a confusing SQL error.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None

    Raises:
        RuntimeError: If a required warehouse table is missing.
    """
    LOG.info("Verifying required warehouse tables")

    # SHOW TABLES returns one tuple for every table in the database.
    table_rows = conn.execute("SHOW TABLES").fetchall()

    # The first value in each tuple is the table name.
    existing_tables: set[str] = {str(row[0]) for row in table_rows}

    # These tables were created and populated in Module 4.
    required_tables: set[str] = {
        "dim_customers",
        "dim_products",
        "fact_sales",
    }

    # Set subtraction finds any required tables that are not present.
    missing_tables: set[str] = required_tables - existing_tables

    if missing_tables:
        missing_text = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            "The data warehouse is missing required tables: "
            f"{missing_text}. Create and populate the Module 4 warehouse first."
        )

    LOG.info("  PASS: All required warehouse tables are available")


# === Section 2.2 DEFINE A CREATE REPORTING VIEW FUNCTION ===


def create_reporting_view(conn: duckdb.DuckDBPyConnection) -> None:
    """Create a reporting view that joins facts and dimensions.

    WHY: The fact table stores measurable business events.
    Dimension tables store descriptive context such as region,
    product name, and category.

    A reporting view joins these tables so analysts can work with
    one reporting-ready result without repeating the joins in every query.

    A view stores the SQL query, not another copy of the data.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("Creating the sales_reporting view")

    # Join the sales fact table to the customer and product dimensions.
    # Add year, quarter, and month values for time-based OLAP operations.
    sql = """
        CREATE OR REPLACE VIEW sales_reporting AS
        SELECT
            s.TransactionID,
            s.SaleDate,
            CAST(EXTRACT(YEAR FROM s.SaleDate) AS INTEGER) AS SalesYear,
            CAST(EXTRACT(QUARTER FROM s.SaleDate) AS INTEGER) AS SalesQuarter,
            STRFTIME(s.SaleDate, '%Y-%m') AS YearMonth,
            s.CustomerID,
            c.Name AS CustomerName,
            c.Region,
            s.ProductID,
            p.ProductName,
            p.Category,
            s.StoreID,
            s.CampaignID,
            s.SaleAmount
        FROM fact_sales s
        JOIN dim_customers c
            ON s.CustomerID = c.CustomerID
        JOIN dim_products p
            ON s.ProductID = p.ProductID
    """

    conn.execute(sql)

    LOG.info("  sales_reporting view created")


# === Section 2.3 DEFINE AN EXPORT REPORTING DATASET FUNCTION ===


def export_reporting_dataset(
    conn: duckdb.DuckDBPyConnection,
) -> pd.DataFrame:
    """Export the reporting view to a CSV file.

    WHY: Power BI and Spark can both read CSV files.
    Exporting one reporting-ready dataset gives both tool paths
    the same rows, columns, dimensions, and business measures.

    Args:
        conn: Open DuckDB connection.

    Returns:
        Reporting-ready pandas DataFrame.
    """
    LOG.info("Exporting the reporting-ready dataset")

    # Create the output folder if it does not already exist.
    DATA_REPORTING.mkdir(parents=True, exist_ok=True)

    # Query the view and return the result as a pandas DataFrame.
    sql = """
        SELECT *
        FROM sales_reporting
        ORDER BY SaleDate, TransactionID
    """

    df_reporting: pd.DataFrame = conn.execute(sql).df()

    # Write the reporting DataFrame to CSV without a pandas index column.
    df_reporting.to_csv(REPORTING_FILE, index=False)

    LOG.info(f"  Exported {df_reporting.shape[0]} reporting rows")
    log_path(LOG, "Reporting data:", REPORTING_FILE)

    return df_reporting


# === Section 2.4 DEFINE A SLICE FUNCTION ===

# Slice: select one value from one dimension.
#
# We select one Region value.
# After fixing the Region dimension, we compare sales by Category.
#
# Use a slice when an analyst wants to focus on one business segment,
# such as one region, one year, one store, or one product category.


def slice_sales_by_region(
    conn: duckdb.DuckDBPyConnection,
    selected_region: str,
) -> pd.DataFrame:
    """Slice sales by one selected region.

    WHY: A slice fixes one dimension at one selected value.
    Here, the Region dimension is fixed to one region.
    We then compare product-category sales inside that region.

    Args:
        conn: Open DuckDB connection.
        selected_region: Region value to include in the slice.

    Returns:
        DataFrame with Region, Category, and TotalSales columns.

    Raises:
        ValueError: If the selected region has no matching rows.
    """
    LOG.info(f"OLAP slice: sales for Region = {selected_region!r}")

    # The WHERE clause performs the slice.
    # It keeps rows for one selected member of the Region dimension.
    #
    # After slicing, GROUP BY summarizes sales by product category
    # within the selected region.
    sql = """
        SELECT
            Region,
            Category,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM sales_reporting
        WHERE Region = ?
        GROUP BY Region, Category
        ORDER BY TotalSales DESC
    """

    # The question-mark placeholder is filled with selected_region.
    # Parameterized queries are safer than constructing SQL with f-strings.
    df_slice: pd.DataFrame = conn.execute(sql, [selected_region]).df()

    if df_slice.empty:
        raise ValueError(
            f"No sales were found for region {selected_region!r}. "
            "Update SLICE_REGION to a region present in the data."
        )

    LOG.info(f"  Categories in the slice: {df_slice.shape[0]}")
    return df_slice


# === Section 2.5 DEFINE A DICE FUNCTION ===

# Dice: select values from two or more dimensions.
#
# We select multiple Region values and multiple Category values.
# The resulting subset is smaller than the complete reporting dataset.
#
# Use a dice when an analyst wants to compare a targeted combination,
# such as two regions, selected categories, and a limited time period.


def dice_sales_by_dimensions(
    conn: duckdb.DuckDBPyConnection,
    selected_regions: tuple[str, ...],
    selected_categories: tuple[str, ...],
) -> pd.DataFrame:
    """Dice sales by selected regions and product categories.

    WHY: A dice filters across two or more dimensions.
    Here, we select members from both the Region dimension
    and the Category dimension.

    Args:
        conn: Open DuckDB connection.
        selected_regions: Region values to include.
        selected_categories: Category values to include.

    Returns:
        DataFrame with Region, Category, and TotalSales columns.

    Raises:
        ValueError: If the selected dice has no matching rows.
    """
    LOG.info(
        f"OLAP dice: Regions = {selected_regions}; Categories = {selected_categories}"
    )

    # Each IN condition selects multiple members from one dimension.
    # Combining both conditions creates a multidimensional subset.
    sql = """
        SELECT
            Region,
            Category,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM sales_reporting
        WHERE Region IN (?, ?)
          AND Category IN (?, ?)
        GROUP BY Region, Category
        ORDER BY TotalSales DESC
    """

    # The parameter order must match the question-mark placeholders.
    parameters: list[str] = [
        *selected_regions,
        *selected_categories,
    ]

    df_dice: pd.DataFrame = conn.execute(sql, parameters).df()

    if df_dice.empty:
        raise ValueError(
            "The selected OLAP dice returned no rows. "
            "Update DICE_REGIONS and DICE_CATEGORIES "
            "to values present in the reporting data."
        )

    LOG.info(f"  Region-category combinations: {df_dice.shape[0]}")
    return df_dice


# === Section 2.6 DEFINE A ROLL-UP FUNCTION ===

# Roll-up: move from detailed values to broader summaries.
#
# Our time hierarchy is:
#
# Month -> Quarter -> Year -> All Years
#
# Use a roll-up when managers need increasingly summarized results,
# such as moving from monthly operational detail to annual totals.


def rollup_sales_by_time(
    conn: duckdb.DuckDBPyConnection,
) -> pd.DataFrame:
    """Roll up sales through the time hierarchy.

    WHY: Roll-up summarizes a measure at broader hierarchy levels.
    Here, detailed monthly sales are summarized into quarters,
    years, and a grand total.

    DuckDB's ROLLUP operation creates each subtotal level
    in one analytical query.

    Args:
        conn: Open DuckDB connection.

    Returns:
        DataFrame containing monthly, quarterly, yearly,
        and all-years sales totals.
    """
    LOG.info("OLAP roll-up: Month -> Quarter -> Year -> All Years")

    # ROLLUP creates these grouping levels:
    #
    # SalesYear, SalesQuarter, YearMonth  = monthly totals
    # SalesYear, SalesQuarter             = quarterly totals
    # SalesYear                           = yearly totals
    # no grouping columns                 = grand total
    #
    # Columns become NULL when that level has been rolled up.
    sql = """
        SELECT
            CASE
                WHEN SalesYear IS NULL THEN 'All Years'
                WHEN SalesQuarter IS NULL THEN 'Year'
                WHEN YearMonth IS NULL THEN 'Quarter'
                ELSE 'Month'
            END AS SummaryLevel,
            SalesYear,
            SalesQuarter,
            YearMonth,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM sales_reporting
        GROUP BY ROLLUP (
            SalesYear,
            SalesQuarter,
            YearMonth
        )
        ORDER BY
            SalesYear NULLS LAST,
            SalesQuarter NULLS LAST,
            YearMonth NULLS LAST
    """

    df_rollup: pd.DataFrame = conn.execute(sql).df()

    LOG.info(f"  Roll-up rows returned: {df_rollup.shape[0]}")
    return df_rollup


# === Section 2.7 DEFINE A GET LATEST SALES YEAR FUNCTION ===


def get_latest_sales_year(
    conn: duckdb.DuckDBPyConnection,
) -> int:
    """Get the latest year represented in the reporting data.

    WHY: Drill-down begins with a selected summary value.
    In an interactive BI tool, a user might click a particular year.
    In this example, we automatically select the latest available year.

    Args:
        conn: Open DuckDB connection.

    Returns:
        Latest sales year as an integer.

    Raises:
        ValueError: If the reporting data contains no sales year.
    """
    LOG.info("Finding the latest sales year for drill-down")

    result = conn.execute("""
        SELECT MAX(SalesYear)
        FROM sales_reporting
    """).fetchone()

    if result is None or result[0] is None:
        raise ValueError("No sales year was found in the reporting data.")

    latest_year: int = int(result[0])
    LOG.info(f"  Selected drill-down year: {latest_year}")
    return latest_year


# === Section 2.8 DEFINE A DRILL-DOWN FUNCTION ===

# Drill-down: move from a summary to increasing levels of detail.
#
# Our time hierarchy is:
#
# Year -> Quarter -> Month
#
# Use a drill-down when a summary result raises another question.
# For example, a manager may see an annual total and then ask:
#
# - Which quarter produced that total?
# - Which months explain the strongest or weakest quarter?


def drilldown_sales_by_time(
    conn: duckdb.DuckDBPyConnection,
    selected_year: int,
) -> pd.DataFrame:
    """Drill down from one year to quarters and months.

    WHY: Drill-down reveals the details behind a summary value.
    This query begins with one selected year and then shows
    the quarter and month levels inside that year.

    Args:
        conn: Open DuckDB connection.
        selected_year: Year to investigate.

    Returns:
        DataFrame with year, quarter, and month detail levels.

    Raises:
        ValueError: If the selected year has no matching rows.
    """
    LOG.info(f"OLAP drill-down: Year {selected_year} -> Quarter -> Month")

    # Each SELECT creates one hierarchy level.
    #
    # UNION ALL combines the year, quarter, and month results
    # into one DataFrame without removing any rows.
    sql = """
        WITH selected_sales AS (
            SELECT
                SalesYear,
                SalesQuarter,
                YearMonth,
                SaleAmount
            FROM sales_reporting
            WHERE SalesYear = ?
        )

        SELECT
            1 AS SortLevel,
            'Year' AS DetailLevel,
            CAST(SalesYear AS VARCHAR) AS PeriodLabel,
            CAST(NULL AS INTEGER) AS SalesQuarter,
            CAST(NULL AS VARCHAR) AS YearMonth,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM selected_sales
        GROUP BY SalesYear

        UNION ALL

        SELECT
            2 AS SortLevel,
            'Quarter' AS DetailLevel,
            CAST(SalesYear AS VARCHAR)
                || '-Q'
                || CAST(SalesQuarter AS VARCHAR) AS PeriodLabel,
            SalesQuarter,
            CAST(NULL AS VARCHAR) AS YearMonth,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM selected_sales
        GROUP BY SalesYear, SalesQuarter

        UNION ALL

        SELECT
            3 AS SortLevel,
            'Month' AS DetailLevel,
            YearMonth AS PeriodLabel,
            SalesQuarter,
            YearMonth,
            ROUND(SUM(SaleAmount), 2) AS TotalSales
        FROM selected_sales
        GROUP BY SalesQuarter, YearMonth

        ORDER BY
            SortLevel,
            SalesQuarter NULLS FIRST,
            YearMonth NULLS FIRST
    """

    df_drilldown: pd.DataFrame = conn.execute(
        sql,
        [selected_year],
    ).df()

    if df_drilldown.empty:
        raise ValueError(f"No sales were found for year {selected_year}.")

    LOG.info(f"  Drill-down rows returned: {df_drilldown.shape[0]}")
    return df_drilldown


# === Section 2.9 DEFINE A SUMMARIZE FUNCTION ===


def summarize(
    df_slice: pd.DataFrame,
    df_dice: pd.DataFrame,
    df_rollup: pd.DataFrame,
    df_drilldown: pd.DataFrame,
    selected_region: str,
    selected_year: int,
) -> None:
    """Log a brief summary of the OLAP findings.

    Args:
        df_slice: Slice results for one selected region.
        df_dice: Dice results for selected regions and categories.
        df_rollup: Time roll-up results.
        df_drilldown: Time drill-down results.
        selected_region: Region used in the slice.
        selected_year: Year used in the drill-down.

    Returns:
        None
    """
    LOG.info("========================")
    LOG.info("SUMMARY")
    LOG.info("========================")

    # The slice is sorted by TotalSales descending.
    # The first row therefore contains the leading category
    # inside the selected region.
    top_slice_category: str = str(df_slice.iloc[0]["Category"])
    top_slice_sales: float = float(df_slice.iloc[0]["TotalSales"])

    LOG.info(
        f"Slice: In {selected_region}, the leading category is "
        f"{top_slice_category} (${top_slice_sales:,.2f})"
    )

    # The dice is also sorted by TotalSales descending.
    # The first row contains the strongest selected combination.
    top_dice_region: str = str(df_dice.iloc[0]["Region"])
    top_dice_category: str = str(df_dice.iloc[0]["Category"])
    top_dice_sales: float = float(df_dice.iloc[0]["TotalSales"])

    LOG.info(
        "Dice: The strongest selected combination is "
        f"{top_dice_region} / {top_dice_category} "
        f"(${top_dice_sales:,.2f})"
    )

    # Select the all-years row from the roll-up result.
    df_all_years = df_rollup.loc[df_rollup["SummaryLevel"] == "All Years"]
    all_years_sales: float = float(df_all_years.iloc[0]["TotalSales"])

    LOG.info(f"Roll-up: Total sales across all years are ${all_years_sales:,.2f}")

    # Select only month-level rows from the drill-down result.
    df_months = df_drilldown.loc[df_drilldown["DetailLevel"] == "Month"]

    best_month_index = df_months["TotalSales"].idxmax()
    best_month: str = str(df_months.loc[best_month_index, "PeriodLabel"])
    best_month_sales: float = float(df_months.loc[best_month_index, "TotalSales"])

    LOG.info(
        f"Drill-down: The strongest month in {selected_year} is "
        f"{best_month} (${best_month_sales:,.2f})"
    )

    LOG.info("========================")
    LOG.info("ANALYST NOTES:")
    LOG.info("Use slice to focus on one dimension value.")
    LOG.info("Use dice to investigate a selected multidimensional subset.")
    LOG.info("Use roll-up to move from detail to broader summaries.")
    LOG.info("Use drill-down to investigate the detail behind a summary.")
    LOG.info("========================")


# === MAIN FUNCTION ===


def main() -> None:
    """Main function to run the DuckDB OLAP reporting logic."""

    log_header(LOG, "BI")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "Data warehouse:", DW_FILE)
    log_path(LOG, "Reporting data:", REPORTING_FILE)

    # DuckDB creates an empty database when the requested file is missing.
    # Check first so we do not accidentally connect to a new empty warehouse.
    if not DW_FILE.exists():
        raise FileNotFoundError(
            f"Data warehouse not found: {DW_FILE}. "
            "Create and populate the Module 4 warehouse first."
        )

    LOG.info("Connecting to DuckDB data warehouse........")
    conn: duckdb.DuckDBPyConnection = duckdb.connect(str(DW_FILE))

    try:
        LOG.info("CALL a function to verify the warehouse........")
        verify_warehouse(conn)

        LOG.info("CALL a function to create the reporting view........")
        create_reporting_view(conn)

        LOG.info("CALL a function to export reporting data........")
        export_reporting_dataset(conn)

        LOG.info("CALL a function to slice sales by region........")
        df_slice = slice_sales_by_region(
            conn,
            SLICE_REGION,
        )

        LOG.info("CALL a function to plot the slice result........")
        plot_bar(
            df=df_slice,
            x="Category",
            y="TotalSales",
            title=f"Sales by Category in {SLICE_REGION}",
            xlabel="Product Category",
            ylabel="Total Sales ($)",
            palette="Blues_d",
        )

        LOG.info("CALL a function to dice sales by dimensions........")
        df_dice = dice_sales_by_dimensions(
            conn,
            DICE_REGIONS,
            DICE_CATEGORIES,
        )

        # Create one readable label for each region-category combination.
        df_dice_chart = df_dice.copy()
        df_dice_chart["RegionCategory"] = (
            df_dice_chart["Region"] + " / " + df_dice_chart["Category"]
        )

        LOG.info("CALL a function to plot the dice result........")
        plot_bar(
            df=df_dice_chart,
            x="RegionCategory",
            y="TotalSales",
            title="Sales for Selected Regions and Categories",
            xlabel="Region / Category",
            ylabel="Total Sales ($)",
            palette="Greens_d",
        )

        LOG.info("CALL a function to roll up sales by time........")
        df_rollup = rollup_sales_by_time(conn)

        # Select the quarterly subtotal rows for a readable chart.
        df_quarterly = df_rollup.loc[df_rollup["SummaryLevel"] == "Quarter"].copy()

        # Build labels such as 2025-Q1.
        df_quarterly["YearQuarter"] = (
            df_quarterly["SalesYear"].astype(int).astype(str)
            + "-Q"
            + df_quarterly["SalesQuarter"].astype(int).astype(str)
        )

        LOG.info("CALL a function to plot quarterly roll-up results........")
        plot_line(
            df=df_quarterly,
            x="YearQuarter",
            y="TotalSales",
            title="Quarterly Sales Roll-Up",
            xlabel="Quarter",
            ylabel="Total Sales ($)",
        )

        LOG.info("CALL a function to select a drill-down year........")
        selected_year = get_latest_sales_year(conn)

        LOG.info("CALL a function to drill down by time........")
        df_drilldown = drilldown_sales_by_time(
            conn,
            selected_year,
        )

        # Select the month-level rows for the detailed trend chart.
        df_monthly = df_drilldown.loc[df_drilldown["DetailLevel"] == "Month"].copy()

        LOG.info("CALL a function to plot monthly drill-down results........")
        plot_line(
            df=df_monthly,
            x="PeriodLabel",
            y="TotalSales",
            title=f"Monthly Sales Drill-Down for {selected_year}",
            xlabel="Month",
            ylabel="Total Sales ($)",
        )

        LOG.info("CALL a function to summarize OLAP findings........")
        summarize(
            df_slice,
            df_dice,
            df_rollup,
            df_drilldown,
            SLICE_REGION,
            selected_year,
        )

        LOG.info("CALL a function to show charts........")
        plt.show()

    finally:
        # Always close the database connection,
        # even if an error occurs while running a query.
        conn.close()
        LOG.info("Closed DuckDB connection")

    LOG.info("Workflow complete")
    LOG.info("CLOSE chart windows to continue.")
    LOG.info("Terminate this process with CTRL+c as needed.")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()
