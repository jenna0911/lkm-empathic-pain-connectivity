"""Confound selection utilities for fMRIPrep outputs.

The ds006243 notes indicate that confound files may be trimmed differently from
the BOLD series. The helpers below therefore keep confound selection separate
from length validation and make mismatches explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import numpy as np
import pandas as pd


MOTION_PARAMETERS = (
    "trans_x",
    "trans_y",
    "trans_z",
    "rot_x",
    "rot_y",
    "rot_z",
)

EXACT_OPTIONAL_COLUMNS = ("framewise_displacement",)
PREFIX_OPTIONAL_COLUMNS = (
    "cosine",
    "a_comp_cor",
    "non_steady_state_outlier",
    "motion_outlier",
)

DEFAULT_CONFOUND_COLUMNS = list(MOTION_PARAMETERS) + list(EXACT_OPTIONAL_COLUMNS)


@dataclass(frozen=True)
class ConfoundExtractionResult:
    """Summary of one confounds file converted to nuisance regressors."""

    source: Path
    output: Path
    n_input_rows: int
    n_output_rows: int
    selected_columns: tuple[str, ...]
    validation_messages: tuple[str, ...]


def load_confounds(confounds_tsv: Path) -> pd.DataFrame:
    """Load one fMRIPrep ``confounds_timeseries.tsv`` file."""

    return pd.read_csv(confounds_tsv, sep="\t")


def select_confounds(confounds: pd.DataFrame) -> pd.DataFrame:
    """Select nuisance regressors for first-level GLM and gPPI models.

    Selected columns include six motion parameters, framewise displacement when
    present, cosine drift regressors, anatomical CompCor regressors,
    non-steady-state outlier regressors, and fMRIPrep motion outlier columns.
    Missing optional columns are skipped. Missing values in selected columns are
    filled with zero, which handles the first framewise-displacement sample.
    """

    selected_columns = get_confound_columns(confounds)
    selected = confounds.loc[:, selected_columns].copy()
    return selected.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def get_confound_columns(confounds: pd.DataFrame) -> list[str]:
    """Return available nuisance columns in a stable, interpretable order."""

    columns = []
    columns.extend(column for column in MOTION_PARAMETERS if column in confounds.columns)
    columns.extend(column for column in EXACT_OPTIONAL_COLUMNS if column in confounds.columns)
    for prefix in PREFIX_OPTIONAL_COLUMNS:
        columns.extend(column for column in confounds.columns if column.startswith(prefix))
    return list(dict.fromkeys(columns))


def extract_confounds(
    confounds_tsv: Path,
    columns: list[str] | None = None,
    n_scans: int | None = None,
    prepared_events: pd.DataFrame | None = None,
    repetition_time: float | None = None,
    on_mismatch: str = "warn",
) -> pd.DataFrame:
    """Load and select nuisance regressors from a fMRIPrep confounds file.

    Parameters
    ----------
    confounds_tsv
        Path to a fMRIPrep ``*_desc-confounds_timeseries.tsv`` file.
    columns
        Optional explicit columns for backward compatibility. When omitted,
        ds006243 nuisance regressors are selected with :func:`select_confounds`.
    n_scans
        Number of BOLD volumes expected for this run. When provided, the
        confounds row count is validated against it.
    prepared_events
        Optional prepared event table. Event-wise BIDS tables are not expected
        to have one row per scan, but validation can flag scan-wise tables that
        do not match ``n_scans`` and can check event timing when TR is provided.
    repetition_time
        TR in seconds, used only for event timing validation.
    on_mismatch
        One of ``"warn"``, ``"error"``, or ``"ignore"``.
    """

    confounds = load_confounds(confounds_tsv)
    validation_messages = validate_run_lengths(
        confounds=confounds,
        n_scans=n_scans,
        prepared_events=prepared_events,
        repetition_time=repetition_time,
        on_mismatch=on_mismatch,
    )
    _emit_validation_messages(validation_messages, on_mismatch=on_mismatch)

    if columns is not None:
        available_columns = [column for column in columns if column in confounds.columns]
        return confounds.loc[:, available_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return select_confounds(confounds)


def validate_run_lengths(
    confounds: pd.DataFrame,
    n_scans: int | None = None,
    prepared_events: pd.DataFrame | None = None,
    repetition_time: float | None = None,
    on_mismatch: str = "warn",
) -> list[str]:
    """Validate BOLD, confound, and prepared-event lengths.

    If ``n_scans`` is provided, the confounds table must have the same number of
    rows as BOLD volumes. Prepared BIDS events are usually event-wise rather
    than scan-wise, so row-count mismatches for event tables are reported as
    guidance instead of a hard failure unless the table appears scan-wise.
    """

    _validate_mismatch_policy(on_mismatch)
    if n_scans is not None and n_scans <= 0:
        raise ValueError("n_scans must be a positive integer when provided.")

    messages = []
    if n_scans is not None and len(confounds) != n_scans:
        messages.append(_length_mismatch_message("confounds", len(confounds), n_scans))

    if n_scans is not None and prepared_events is not None:
        messages.extend(
            _validate_prepared_events(
                prepared_events=prepared_events,
                n_scans=n_scans,
                repetition_time=repetition_time,
            )
        )

    return messages


def extract_confounds_file(
    confounds_tsv: Path,
    output_tsv: Path,
    n_scans: int | None = None,
    prepared_events_tsv: Path | None = None,
    repetition_time: float | None = None,
    on_mismatch: str = "warn",
) -> ConfoundExtractionResult:
    """Write selected nuisance regressors for one fMRIPrep confounds file."""

    prepared_events = load_prepared_events(prepared_events_tsv) if prepared_events_tsv else None
    raw_confounds = load_confounds(confounds_tsv)
    validation_messages = validate_run_lengths(
        raw_confounds,
        n_scans=n_scans,
        prepared_events=prepared_events,
        repetition_time=repetition_time,
        on_mismatch=on_mismatch,
    )
    _emit_validation_messages(validation_messages, on_mismatch=on_mismatch)

    selected = select_confounds(raw_confounds)
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(output_tsv, sep="\t", index=False)
    return ConfoundExtractionResult(
        source=confounds_tsv,
        output=output_tsv,
        n_input_rows=len(raw_confounds),
        n_output_rows=len(selected),
        selected_columns=tuple(selected.columns),
        validation_messages=tuple(validation_messages),
    )


def extract_confounds_directory(
    fmriprep_dir: Path,
    output_root: Path,
    on_mismatch: str = "warn",
) -> list[ConfoundExtractionResult]:
    """Select nuisance regressors for every fMRIPrep confounds file in a tree."""

    fmriprep_dir = Path(fmriprep_dir)
    output_root = Path(output_root)
    if not fmriprep_dir.exists():
        raise FileNotFoundError(f"fMRIPrep directory does not exist: {fmriprep_dir}")

    confound_files = find_confounds_files(fmriprep_dir)
    if not confound_files:
        raise FileNotFoundError(f"No confounds_timeseries.tsv files found under: {fmriprep_dir}")

    results = []
    for confounds_tsv in confound_files:
        output_tsv = output_path_for_confounds(confounds_tsv, fmriprep_dir, output_root)
        results.append(
            extract_confounds_file(
                confounds_tsv=confounds_tsv,
                output_tsv=output_tsv,
                on_mismatch=on_mismatch,
            )
        )
    return results


def find_confounds_files(fmriprep_dir: Path) -> list[Path]:
    """Find fMRIPrep confounds time-series files under a derivatives tree."""

    return sorted(Path(fmriprep_dir).rglob("*confounds_timeseries.tsv"))


def output_path_for_confounds(confounds_tsv: Path, fmriprep_dir: Path, output_root: Path) -> Path:
    """Build a derivative output path for selected nuisance regressors."""

    try:
        relative = confounds_tsv.relative_to(fmriprep_dir)
    except ValueError:
        relative = Path(confounds_tsv.name)
    name = confounds_tsv.name
    if name.endswith("_desc-confounds_timeseries.tsv"):
        name = name.replace("_desc-confounds_timeseries.tsv", "_desc-nuisance_regressors.tsv")
    else:
        name = name.replace("_confounds_timeseries.tsv", "_desc-nuisance_regressors.tsv")
    return Path(output_root) / relative.parent / name


def load_prepared_events(prepared_events_tsv: Path) -> pd.DataFrame:
    """Load a prepared event table for optional validation."""

    return pd.read_csv(prepared_events_tsv, sep="\t")


def make_synthetic_confounds(n_scans: int = 5) -> pd.DataFrame:
    """Return a small fMRIPrep-like confounds table for tests/examples."""

    data = {
        "trans_x": np.linspace(0.0, 0.4, n_scans),
        "trans_y": np.linspace(0.1, 0.5, n_scans),
        "trans_z": np.linspace(0.2, 0.6, n_scans),
        "rot_x": np.linspace(0.0, 0.04, n_scans),
        "rot_y": np.linspace(0.1, 0.14, n_scans),
        "rot_z": np.linspace(0.2, 0.24, n_scans),
        "framewise_displacement": [np.nan] + [0.1] * (n_scans - 1),
        "cosine00": np.linspace(1.0, -1.0, n_scans),
        "a_comp_cor_00": np.linspace(0.3, 0.7, n_scans),
        "non_steady_state_outlier00": [1] + [0] * (n_scans - 1),
        "motion_outlier00": [1 if index == 2 else 0 for index in range(n_scans)],
        "unused_signal": np.arange(n_scans),
    }
    return pd.DataFrame(data)


def _validate_prepared_events(
    prepared_events: pd.DataFrame,
    n_scans: int,
    repetition_time: float | None,
) -> list[str]:
    messages = []
    if _looks_scanwise(prepared_events, n_scans) and len(prepared_events) != n_scans:
        messages.append(_length_mismatch_message("prepared events", len(prepared_events), n_scans))
    elif len(prepared_events) != n_scans:
        messages.append(
            "Prepared events have "
            f"{len(prepared_events)} rows while n_scans={n_scans}. "
            "This is expected for event-wise BIDS files, but if this file is a "
            "scan-wise design matrix, trim or regenerate it to match the BOLD "
            "and confounds rows."
        )

    required_event_columns = {"onset", "duration"}
    if repetition_time is not None and required_event_columns.issubset(prepared_events.columns):
        run_duration = n_scans * repetition_time
        event_offsets = prepared_events["onset"] + prepared_events["duration"]
        if event_offsets.max() > run_duration:
            messages.append(
                "Prepared events extend beyond the BOLD run duration "
                f"({event_offsets.max():.3f}s > {run_duration:.3f}s). "
                "Check whether BOLD or confounds were trimmed, and consider "
                "shifting event onsets or trimming the design consistently."
            )
    return messages


def _looks_scanwise(prepared_events: pd.DataFrame, n_scans: int) -> bool:
    if len(prepared_events) == n_scans:
        return True
    scanwise_columns = {"scan", "volume", "frame", "timepoint"}
    return bool(scanwise_columns.intersection(prepared_events.columns))


def _length_mismatch_message(name: str, n_rows: int, n_scans: int) -> str:
    return (
        f"{name} rows ({n_rows}) do not match BOLD n_scans ({n_scans}). "
        "ds006243 documentation notes that confounds may be trimmed differently "
        "from BOLD files. Suggested options: verify the fMRIPrep provenance, "
        "drop matching non-steady-state volumes from BOLD/events, trim confounds "
        "to the BOLD series only when justified, or regenerate confounds so all "
        "first-level inputs share the same number of scans."
    )


def _emit_validation_messages(messages: list[str], on_mismatch: str) -> None:
    _validate_mismatch_policy(on_mismatch)
    if not messages or on_mismatch == "ignore":
        return
    if on_mismatch == "error":
        raise ValueError("\n".join(messages))
    for message in messages:
        warnings.warn(message, UserWarning, stacklevel=2)


def _validate_mismatch_policy(on_mismatch: str) -> None:
    if on_mismatch not in {"warn", "error", "ignore"}:
        raise ValueError("on_mismatch must be one of: warn, error, ignore.")
