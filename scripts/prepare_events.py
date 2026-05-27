#!/usr/bin/env python
"""Backward-compatible wrapper for scripts/01_prepare_events.py."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("01_prepare_events.py")), run_name="__main__")
