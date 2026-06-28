# Your Files

Projects include instructor example files that typically end with `_case`.
Keep these as working examples.

You will generally copy the instructor file,
rename it with your alias, and run your version
**in addition to** the example version.

## Choose Your Name (example: `stellar_analytics`)

You may use your real name or any professional alias.
You are **never required to use your real name**.

Naming rules:

- all lowercase
- no spaces
- use underscores as needed

## 1. Python Files

Copy an example Python file and rename the copy using your alias.
For example:

```text
src/**/app_case.py
src/**/app_stellar_analytics.py
```

## 2. Python Execution Command (as needed)

In your `README.md`,
add your execution command near the related example command.
Verify that your command runs your code.
For example:

```shell
uv run python -m bizintel.app_case
uv run python -m bizintel.app_stellar_analytics
```

The exact package name and script name depend on the project.

## 3. Data Files

Example data files are typically found in `data/raw/`.

Many data source names will not be customized.
Sometimes, it may be useful to copy the example data file
(e.g. if named \_case)
and rename the copy using your alias.

Renaming files is a great way to discover the importance of data paths.

For assistance, use VS Code "search in files" to find
everywhere that `data/` appears in the project.

Paths are critical and can be hard to get right.
That's why we log paths, learn how to search for paths, and
declare constants in Python to keep them consistent.

A renaming example might be:

```text
data/raw/data_case.csv
data/raw/data_stellar_analytics.csv
```

## Final Set Includes Example Files AND Your Alias Files

Keep the original example code and original data files
so the provided example continues to work.
Modify **your code files** and **your data files**
as you develop your custom project.

## Project Requirements

You may choose your own datasets.
For accountability and to earn maximum credit:
code **filenames** should include **your alias**.
