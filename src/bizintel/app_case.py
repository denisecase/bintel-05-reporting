"""app_case.py - example application entry point.

This module provides the standard app_case entry point used across projects.

Author: Denise Case
Date: 2026-06

Terminal command to run this file from the root project folder:

uv run python -m bizintel.app_case

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

from bizintel.olap_case import main as run_olap_reporting
from bizintel.utils_logger import LOG, log_header

# === DECLARE GLOBAL CONSTANTS AND CONFIGURATION ===

# Path to the DuckDB data warehouse.
DW_FILE: Final[Path] = Path("artifacts/smart_sales.duckdb")

# Folder for reporting-ready data.
DATA_REPORTING: Final[Path] = Path("data/reporting")

# Reporting-ready CSV file used by Power BI or Spark.
REPORTING_FILE: Final[Path] = DATA_REPORTING / "sales_reporting_case.csv"

# === DEFINE THE MAIN FUNCTION (WHERE THE MAGIC HAPPENS) ===


def main() -> None:
    """Main function to run the BI logic.
    This is where the main logic starts
    when this script is run.
    """

    # First, log the header for the BI module to indicate the start of the workflow.
    log_header(LOG, "BI")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "Data warehouse:", DW_FILE)
    log_path(LOG, "Reporting data:", REPORTING_FILE)

    run_olap_reporting()

    LOG.info("App workflow complete")
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
