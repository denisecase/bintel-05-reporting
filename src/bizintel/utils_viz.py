"""utils_viz.py - reusable chart functions.

WHY: Consistent charts across all modules.
Same palette, same style, same axis conventions.
Generate professional-quality output from day one.

These functions are a starting point.
Change colors, sizes, and labels to match the data and audience.
Customize charts for the story they tell.
"""

# === IMPORTS ===

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bizintel.utils_logger import LOG

# === FUNCTIONS ===


def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    xlabel: str,
    ylabel: str,
    palette: str = "Blues_d",
) -> None:
    """Plot a vertical bar chart.

    WHY: Bar charts are the most common chart in BI reporting.
    A reusable function ensures consistent style and labeling
    across all modules.

    Args:
        df: DataFrame containing the data to plot.
        x: Column name for the x-axis (categories).
        y: Column name for the y-axis (values).
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        palette: Seaborn color palette name.

    Returns:
        None
    """
    LOG.info(f"Creating chart: {title}")

    _, ax = plt.subplots(figsize=(9, 5))

    bar: Axes = sns.barplot(
        data=df,
        x=x,
        y=y,
        hue=x,
        legend=False,
        palette=palette,
        ax=ax,
    )

    bar.set_title(f"{title} (CLOSE chart to continue)")
    bar.set_xlabel(xlabel)
    bar.set_ylabel(ylabel)

    plt.tight_layout()


def plot_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    xlabel: str,
    ylabel: str,
) -> None:
    """Plot a line chart.

    WHY: Line charts show trends over time, which is one of
    the most common BI use cases (weekly sales, monthly revenue, etc.).

    Args:
        df: DataFrame containing the data to plot.
        x: Column name for the x-axis (time or ordered categories).
        y: Column name for the y-axis (values).
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        None
    """
    LOG.info(f"Creating chart: {title}")

    _, ax = plt.subplots(figsize=(9, 5))

    line: Axes = sns.lineplot(
        data=df,
        x=x,
        y=y,
        ax=ax,
        marker="o",
    )

    line.set_title(f"{title} (CLOSE chart to continue)")
    line.set_xlabel(xlabel)
    line.set_ylabel(ylabel)

    plt.tight_layout()
