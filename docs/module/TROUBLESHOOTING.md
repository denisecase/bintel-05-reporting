# Troubleshooting

If you've created the .venv virtual environment,
installed the necessary packages with `uv sync`,
and selected a Kernel for your Jupyter Notebook, it should run -
even if VS Code shows a missing package error.

Check Kernel and `.venv`. VS Code may show an issue, but may still work.
Sometimes closing and reopening the notebook file is helpful.
Make sure your `.venv` is active and the kernel is selected.

## Why Your Notebook May Not See a Package

If the Jupyter notebook kernel is not set
to the same environment where you installed the package,
the package won't be found.
This can happen if:

- The terminal is using one virtual environment, but the Jupyter kernel is using another.
- You have multiple virtual environments and accidentally select the wrong one.
- Path conflicts or misconfigurations prevent the notebook from recognizing installed packages.

## Recommendations

### Recommendation 1: Keep Virtual Environment and Kernel Aligned

The environment where the Jupyter server runs might differ
from the environment where the notebook kernel runs.
This can lead to scenarios where a package appears
installed in the terminal but isn't accessible within the notebook.

When using uv:

1. Run `uv sync` in the root project folder to install dependencies from pyproject.toml
2. In VS Code, click **Select Kernel** in the top-right of your notebook
3. Choose **Python Environments** and select the `.venv` in your project folder

### Recommendation 2: Use uv to Add Missing Packages

If you need to add a package, use uv in the terminal:

```bash
uv add pandas
```

This updates your pyproject.toml and installs the package in your .venv.

Then restart your kernel: **Kernel > Restart Kernel** or click the restart button.

### Recommendation 3: Use Magic Commands as a Fallback

If your project virtual environment and kernel
are aligned but you still have issues, use magic commands.
Magic commands are interpreted by the IPython kernel
and install directly into the notebook's environment.

In a Python cell:

```python
%pip install pandas
```

Note: We don't use `py -m` like we do in the terminal.

### Avoid: Shell Commands for Installs

Don't use `!pip install` (with an exclamation mark).
This runs in the shell environment, which might not
be the same environment as your notebook kernel.
Use `%pip install` (with a percent sign) instead.
