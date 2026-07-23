# Glossary

Use this page to record terms and ideas that help you understand
professional analytics projects.

This project covers OLAP reporting:
querying the data warehouse using slice, dice, and drilldown operations.

Pro-tip: Expand the VS Code **Outline** view (below the navigator on the right)
to see this file organization at-a-glance.

## OLAP Concepts

### OLAP

OLAP (Online Analytical Processing) is an approach to analyzing
multidimensional business data at different levels of detail.
OLAP supports slice, dice, drilldown, and rollup operations
used in BI reporting.

### slice

A slice filters data to one value of a single dimension.
For example, filtering sales to only the Electronics category
is a slice operation.
Slicing isolates a subset for focused analysis.

### dice

Dicing filters data across two or more dimensions simultaneously.
For example, filtering by both product category and customer region
is a dice operation.
Dicing reveals which combinations of dimensions drive performance.

### drilldown

Drilldown moves from a high-level summary to more granular detail.
For example, moving from annual sales totals to monthly totals
is a drilldown operation.
Drilldown helps identify which time periods or subcategories
explain a trend.

### rollup

Rollup is the opposite of drilldown.
It moves from granular detail to a higher-level summary.
For example, aggregating daily sales into monthly totals is a rollup.

### data cube

A data cube is a multidimensional view of data organized by dimensions and metrics.
It allows analysts to quickly pivot, slice, and dice large datasets.
A data cube can be pre-computed or generated on the fly from a warehouse.

### pivot table

A pivot table reorganizes data by placing dimension values as row and column headers
and aggregated metrics as cell values.
It is a common way to compare performance across two dimensions at once.

## SQL for Reporting

### SELECT

`SELECT` specifies which columns to return in a query result.
`SELECT *` returns all columns.
Good practice is to name only the columns you need.

### WHERE

`WHERE` filters rows based on a condition.
`WHERE Category = 'Electronics'` returns only Electronics rows.
`WHERE` can implement a slice by selecting one value
from a dimension.

### GROUP BY

`GROUP BY` organizes rows into groups based on one or more columns
and allows aggregation functions to be applied to each group.
`GROUP BY Region` with `SUM(SaleAmount)` gives total sales per region.

### ORDER BY

`ORDER BY` sorts query results by one or more columns.
`ORDER BY TotalSales DESC` sorts results from highest to lowest.

### strftime

`strftime` is a DuckDB function that formats date values as strings.
`strftime(SaleDate, '%Y-%m')` extracts the year and month from a date.
It is used to group sales by month for trend analysis.

### subquery

A subquery is a SELECT statement nested inside another SELECT statement.
It can be used to filter, rank, or compute intermediate results
before the outer query runs.

## Visualization for Reporting

### seaborn

seaborn is a Python visualization library built on matplotlib.
It provides high-level chart functions with sensible defaults.
`sns.barplot()` and `sns.lineplot()` are used throughout this course.

### bar chart

A bar chart compares values across categories using rectangular bars.
It is the most common chart for comparing totals by dimension.

### line chart

A line chart shows values over time by connecting data points with a line.
It is the standard chart for visualizing trends and time series.
