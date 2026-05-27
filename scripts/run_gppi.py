#!/usr/bin/env python
"""Backward-compatible wrapper for scripts/05_run_gppi.py."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("05_run_gppi.py")), run_name="__main__")
