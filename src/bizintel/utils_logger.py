"""utils_logger.py - shared logger setup.

WHY: One place to configure logging for the entire project.
Import LOG and log_header from here in every module.
"""

from datafun_toolkit.logger import get_logger, log_header

__all__ = ["get_logger", "log_header"]

LOG = get_logger("BI", level="DEBUG")
