"""Paths to binaries and data files.

:author: Shay Hill
:created: 2023-02-03
"""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES = _PROJECT_ROOT / "templates"
