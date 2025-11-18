"""
sitecustomize is a Python hook that is imported automatically (if found on sys.path)
after the 'site' module initialization. By placing this file at the container root
and ensuring the container root is on sys.path (which it typically is when running the app),
we can make sure the 'src' package is importable even when the working directory varies.

This avoids brittle sys.path hacks in application code.
"""
from __future__ import annotations

import os
import sys


def _ensure_repo_root_on_path() -> None:
    """
    Add the container root to sys.path if not already present so that 'src' is importable.

    This is a no-op if the path is already present.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)


_ensure_repo_root_on_path()
