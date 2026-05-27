#!/usr/bin/env python
"""Backward-compatible wrapper for scripts/02_extract_confounds.py."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("02_extract_confounds.py")), run_name="__main__")
