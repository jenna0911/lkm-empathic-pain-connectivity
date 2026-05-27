"""First-level GLM design-matrix helpers for the ds006243 gPPI workflow.

This module builds design matrices only. It does not fit first-level fMRI
models or load BOLD images.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from lkm_connectivity.events import ALL_REGRESSORS, GPPI_REGRESSORS, POST_STIMULATION_REST_REGRESSORS


DEFAULT_TR = 2.5


@dataclass(frozen=True)
class FirstLevelDesignResult:
    """Summary of one generated first-level design matrix."""

    events_tsv: Path
    confounds_tsv: Path | None
    output_tsv: Path
    n_scans: int
    tr: float
    columns: tuple[str, ...]


def define_first_level_regressors(events: pd.DataFrame, include_rest: bool = True) -> pd.DataFrame:
    """Return validated first-level event regressors for Nilearn.

    Parameters
    ----------
    events
        Prepared gPPI event table with ``onset``, ``duration``, and
        ``trial_type`` columns.
    include_rest
        Whether post-stimulation rest regressors are allowed.
    """

    validate_events_for_first_level(events, n_scans=None, tr=DEFAULT_TR, include_rest=include_rest)
    return events.loc[:, ["onset", "duration", "trial_type"]].copy()


def make_frame_times(n_scans: int, tr: float = DEFAULT_TR) -> np.ndarray:
    """Create frame times for a run with ``n_scans`` and repetition time ``tr``."""

    if n_scans <= 0:
        raise ValueError("n_scans must be a positive integer.")
    if tr <= 0:
        raise ValueError("TR must be positive.")
    return np.arange(n_scans, dtype=float) * tr


def build_first_level_design_matrix(
    events: pd.DataFrame,
    n_scans: int,
    tr: float = DEFAULT_TR,
    confounds: pd.DataFrame | None = None,
    include_rest: bool = True,
    hrf_model: str = "glover",
    drift_model: str | None = None,
) -> pd.DataFrame:
    """Build a first-level design matrix from prepared events and confounds.

    The task regressors are generated with
    ``nilearn.glm.first_level.make_first_level_design_matrix``. Confounds are
    appended as nuisance regressors. This function validates timing and row
    counts but does not fit a GLM to imaging data.
    """

    try:
        from nilearn.glm.first_level import make_first_level_design_matrix
    except ImportError as exc:
        raise ImportError("nilearn is required to build first-level design matrices.") from exc

    validate_events_for_first_level(events, n_scans=n_scans, tr=tr, include_rest=include_rest)
    prepared_events = define_first_level_regressors(events, include_rest=include_rest)
    frame_times = make_frame_times(n_scans=n_scans, tr=tr)

    design = make_first_level_design_matrix(
        frame_times=frame_times,
        events=prepared_events,
        hrf_model=hrf_model,
        drift_model=drift_model,
    )
    design = ensure_expected_task_columns(design, include_rest=include_rest)

    if confounds is not None:
        nuisance = validate_and_prepare_confounds(confounds, n_scans=n_scans)
        overlap = set(design.columns).intersection(nuisance.columns)
        if overlap:
            nuisance = nuisance.rename(columns={column: f"confound_{column}" for column in overlap})
        design = pd.concat(
            [
                design.reset_index(drop=True),
                nuisance.reset_index(drop=True),
            ],
            axis=1,
        )
        design.index = frame_times

    return design


def validate_events_for_first_level(
    events: pd.DataFrame,
    n_scans: int | None,
    tr: float,
    include_rest: bool = True,
) -> None:
    """Validate prepared event names and timing before design-matrix creation."""

    required = {"onset", "duration", "trial_type"}
    missing = required.difference(events.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Events are missing required columns: {missing_text}")

    if events.empty:
        raise ValueError("Events table is empty.")
    if tr <= 0:
        raise ValueError("TR must be positive.")

    numeric = events.loc[:, ["onset", "duration"]].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise ValueError("Event onset and duration columns must be numeric.")
    if (numeric["onset"] < 0).any():
        raise ValueError("Event onsets must be non-negative.")
    if (numeric["duration"] < 0).any():
        raise ValueError("Event durations must be non-negative.")

    allowed = set(ALL_REGRESSORS if include_rest else GPPI_REGRESSORS)
    unknown = sorted(set(events["trial_type"]) - allowed)
    if unknown:
        raise ValueError(f"Unknown first-level trial_type values: {', '.join(unknown)}")

    if not set(events["trial_type"]).intersection(GPPI_REGRESSORS):
        raise ValueError("Events must contain at least one anticipation or stimulation regressor.")

    if n_scans is not None:
        if n_scans <= 0:
            raise ValueError("n_scans must be a positive integer.")
        run_duration = n_scans * tr
        event_offsets = numeric["onset"] + numeric["duration"]
        if event_offsets.max() > run_duration:
            raise ValueError(
                "Events extend beyond the modeled run duration "
                f"({event_offsets.max():.3f}s > {run_duration:.3f}s). "
                "Check TR, n_scans, and any trimming of BOLD/confounds/events."
            )
        if event_offsets.max() > max(run_duration - tr, 0):
            warnings.warn(
                "At least one event ends during the final TR. Verify this is expected for the run.",
                UserWarning,
                stacklevel=2,
            )

    if not include_rest:
        rest_columns = sorted(set(events["trial_type"]).intersection(POST_STIMULATION_REST_REGRESSORS))
        if rest_columns:
            raise ValueError(
                "Post-stimulation rest regressors are present but include_rest=False: "
                + ", ".join(rest_columns)
            )


def validate_and_prepare_confounds(confounds: pd.DataFrame, n_scans: int) -> pd.DataFrame:
    """Validate nuisance regressors and return a numeric scan-wise table."""

    if len(confounds) != n_scans:
        raise ValueError(
            f"Confound rows ({len(confounds)}) do not match n_scans ({n_scans}). "
            "Trim BOLD/confounds consistently before creating the first-level design."
        )
    if confounds.empty:
        return confounds.copy()

    nuisance = confounds.apply(pd.to_numeric, errors="coerce")
    nonnumeric = confounds.notna() & nuisance.isna()
    if nonnumeric.any().any() or np.isinf(nuisance.to_numpy()).any():
        warnings.warn("Confounds contain non-numeric or infinite values; filling with 0.", UserWarning, stacklevel=2)
    return nuisance.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def ensure_expected_task_columns(design: pd.DataFrame, include_rest: bool = True) -> pd.DataFrame:
    """Add zero-filled task columns that are absent from a single run."""

    expected = ALL_REGRESSORS if include_rest else GPPI_REGRESSORS
    completed = design.copy()
    for column in expected:
        if column not in completed.columns:
            completed[column] = 0.0
    return completed


def make_first_level_from_files(
    events_tsv: Path,
    output_tsv: Path,
    n_scans: int,
    tr: float = DEFAULT_TR,
    confounds_tsv: Path | None = None,
    include_rest: bool = True,
    hrf_model: str = "glover",
    drift_model: str | None = None,
) -> FirstLevelDesignResult:
    """Load prepared events/confounds and write a first-level design matrix."""

    events = pd.read_csv(events_tsv, sep="\t")
    confounds = pd.read_csv(confounds_tsv, sep="\t") if confounds_tsv else None
    design = build_first_level_design_matrix(
        events=events,
        n_scans=n_scans,
        tr=tr,
        confounds=confounds,
        include_rest=include_rest,
        hrf_model=hrf_model,
        drift_model=drift_model,
    )
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    design.to_csv(output_tsv, sep="\t", index_label="frame_time")
    return FirstLevelDesignResult(
        events_tsv=events_tsv,
        confounds_tsv=confounds_tsv,
        output_tsv=output_tsv,
        n_scans=n_scans,
        tr=tr,
        columns=tuple(design.columns),
    )


def make_synthetic_first_level_inputs(n_scans: int = 40, tr: float = DEFAULT_TR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create small synthetic events/confounds for tests and examples."""

    from lkm_connectivity.confounds import make_synthetic_confounds

    events = pd.DataFrame(
        {
            "onset": [0.0, 5.0, 10.0, 15.0, 25.0, 35.0, 45.0, 55.0, 65.0],
            "duration": [2.5, 2.5, 2.5, 2.5, 3.0, 3.0, 3.0, 3.0, 5.0],
            "trial_type": [
                "self_fear_anticipation",
                "self_safety_anticipation",
                "other_fear_anticipation",
                "other_safety_anticipation",
                "self_pain_stimulation",
                "self_nopain_stimulation",
                "other_pain_stimulation",
                "other_nopain_stimulation",
                "post_self_pain_rest",
            ],
        }
    )
    max_offset = float((events["onset"] + events["duration"]).max())
    if max_offset > n_scans * tr:
        raise ValueError("Synthetic events do not fit within the requested run duration.")
    confounds = make_synthetic_confounds(n_scans=n_scans)
    return events, confounds
