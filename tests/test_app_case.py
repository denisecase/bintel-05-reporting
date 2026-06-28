# ============================================================
# tests/test_app_case.py
# ============================================================
# WHY: Smoke test the example module to illustrate the role
# of tests in professional project workflows.
#
# Run:
#   uv run python -m pytest

from bizintel import app_case


def test_app_case_has_main() -> None:
    """Verify the example module exposes a main function."""
    assert callable(app_case.main)
