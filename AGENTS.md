# ./AGENTS.md (ALL-COURSE-PY-SRC-REPOS)

## WHY

- This repo uses a uniform, reproducible workflow based on **uv** and **pyproject.toml**.
- These instructions exist to prevent tool drift (e.g., pip) and OS mismatch.

## Portfolio Project Work

This is a professional project repository intended to support portfolio-quality work.

When assisting with this repo:

- preserve the original example files unless the user explicitly says to remove them
- keep custom files alongside the working examples until the project has been assessed
- assist with small, understandable changes over large rewrites
- do not hide important project logic behind unnecessary abstraction
- do not replace the project with an unrelated solution
- keep filenames, paths, and commands consistent with the project instructions
- assist the user without taking over; the user must be able to
  review, explain, and maintain all of their contributions

## Requirements

- Use **uv** for all environment, dependency, and run commands in this repo.
- Do **not** recommend or use `pip install ...` as the primary workflow.
- This repo targets a specific version of Python, pinned via uv.
- Commands and guidance must work on **Windows, macOS, and Linux**.
- If shell-specific commands are unavoidable, provide both:
  - PowerShell (Windows)
  - bash/zsh (macOS/Linux)
- Do not overwrite project-specific source code, tests, notebooks, data, or
  documentation unless explicitly requested.

## Quickstart

- Install **uv** using the official method for your OS.
- Keep uv current.
- Pin Python using uv.
- Upgrade the lock file to assist with security.
- Sync all dependencies (dev + docs) and upgrade to keep current.

```shell
uv self update
uv python pin 3.14
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade
```

## Common Tasks

Run all commands via **uv**.

Lint / format:

```shell
uv run ruff format .
uv run ruff check . --fix
uv run python -m pyright
uv run python -m pytest
```

Build documentation:

```shell
uv run python -m zensical build
```

## pre-commit

- pre-commit runs only on tracked / staged files.
- Users should `git add -A` files before expecting hooks to run.
- Users may need to re-run pre-commit if changes were made.
