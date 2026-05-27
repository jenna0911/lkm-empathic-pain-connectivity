"""Shared configuration helpers for the analysis scripts."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem locations used by the local analysis workflow."""

    bids_root: Path = Path("data/ds006243")
    fmriprep_dir: Path = Path("derivatives/fmriprep")
    output_dir: Path = Path("derivatives/lkm_connectivity")
    results_dir: Path = Path("results")


DEFAULT_PATHS = ProjectPaths()
