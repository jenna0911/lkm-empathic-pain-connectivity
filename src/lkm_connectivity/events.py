"""Prepare ds006243 BIDS events for task-based connectivity models.

The public repository does not include OpenNeuro data. These functions operate
on a local BIDS checkout and write lightweight, collapsed event files under
``derivatives/events/`` for first-level GLM and gPPI models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd


ANTICIPATION_REGRESSORS = (
    "self_fear_anticipation",
    "self_safety_anticipation",
    "other_fear_anticipation",
    "other_safety_anticipation",
)

STIMULATION_REGRESSORS = (
    "self_pain_stimulation",
    "self_nopain_stimulation",
    "other_pain_stimulation",
    "other_nopain_stimulation",
)

POST_STIMULATION_REST_REGRESSORS = (
    "post_self_pain_rest",
    "post_self_nopain_rest",
    "post_other_pain_rest",
    "post_other_nopain_rest",
)

GPPI_REGRESSORS = ANTICIPATION_REGRESSORS + STIMULATION_REGRESSORS
ALL_REGRESSORS = GPPI_REGRESSORS + POST_STIMULATION_REST_REGRESSORS

DS006243_TIMING_TO_REGRESSOR = {
    "selfpainanticipation": "self_fear_anticipation",
    "selfneutralanticipation": "self_safety_anticipation",
    "otherpainanticipation": "other_fear_anticipation",
    "otherneutralanticipation": "other_safety_anticipation",
    "selfpain": "self_pain_stimulation",
    "selfnopain": "self_nopain_stimulation",
    "otherpain": "other_pain_stimulation",
    "othernopain": "other_nopain_stimulation",
    "selfpainrest": "post_self_pain_rest",
    "selfnopainrest": "post_self_nopain_rest",
    "otherpainrest": "post_other_pain_rest",
    "othernopainrest": "post_other_nopain_rest",
}

TEXT_COLUMNS_PRIORITY = (
    "trial_type",
    "condition",
    "event_type",
    "stim_type",
    "stimulus",
    "stim_file",
    "cue",
    "phase",
    "period",
    "target",
    "recipient",
    "perspective",
)


@dataclass(frozen=True)
class EventPreparationResult:
    """Summary of a prepared BIDS events file."""

    source: Path
    output: Path
    n_input_rows: int
    n_output_rows: int
    n_unmapped_rows: int


def load_events(events_tsv: Path) -> pd.DataFrame:
    """Load a BIDS ``events.tsv`` file.

    Parameters
    ----------
    events_tsv
        Path to a BIDS-compatible events file.

    Returns
    -------
    pandas.DataFrame
        Event table read with tab separation.
    """

    return pd.read_csv(events_tsv, sep="\t")


def prepare_phase_events(events: pd.DataFrame, include_rest: bool = True) -> pd.DataFrame:
    """Collapse ds006243 event rows into gPPI task regressors.

    This compatibility wrapper delegates to :func:`collapse_events_for_gppi`.
    """

    return collapse_events_for_gppi(events, include_rest=include_rest)


def collapse_events_for_gppi(events: pd.DataFrame, include_rest: bool = True) -> pd.DataFrame:
    """Create collapsed gPPI regressors from one BIDS events table.

    The output contains BIDS-style ``onset``, ``duration``, and ``trial_type``
    columns. Rows are kept when their text metadata can be mapped onto one of
    the planned task regressors:

    - self/other fear or safety anticipation
    - self/other pain or no-pain stimulation
    - optional post-stimulation rest regressors

    The mapper is intentionally conservative and text based so it can handle
    BIDS files whose condition information is split across columns. Unmapped
    rows are dropped from the returned event table.
    """

    _validate_events(events)
    prepared = events.copy()
    prepared["trial_type"] = prepared.apply(
        lambda row: infer_collapsed_trial_type(row, include_rest=include_rest),
        axis=1,
    )
    prepared = prepared.dropna(subset=["trial_type"])
    prepared = prepared.loc[:, ["onset", "duration", "trial_type"]]
    prepared = prepared.sort_values(["onset", "duration", "trial_type"])
    return prepared.reset_index(drop=True)


def infer_collapsed_trial_type(row: pd.Series, include_rest: bool = True) -> str | None:
    """Infer one collapsed trial type from an event row.

    Parameters
    ----------
    row
        One row from a BIDS events table.
    include_rest
        Whether rows labeled as post-stimulation rest should be mapped to
        ``post_*_rest`` regressors.

    Returns
    -------
    str or None
        Collapsed regressor name, or ``None`` when the row should be excluded.
    """

    text = _row_text(row)
    if not text:
        return None

    actor = _infer_actor(text)
    if actor is None:
        return None

    if include_rest and _has_any(text, "post", "rest", "fixation", "iti", "isi", "jitter"):
        pain = _infer_pain(text)
        if pain is None:
            return None
        pain_label = "pain" if pain else "nopain"
        return f"post_{actor}_{pain_label}_rest"

    phase = _infer_phase(text)
    if phase == "anticipation":
        threat = _infer_threat(text)
        if threat is None:
            return None
        threat_label = "fear" if threat else "safety"
        return f"{actor}_{threat_label}_anticipation"

    if phase == "stimulation":
        pain = _infer_pain(text)
        if pain is None:
            return None
        pain_label = "pain" if pain else "nopain"
        return f"{actor}_{pain_label}_stimulation"

    return None


def prepare_bids_events(
    bids_root: Path,
    output_root: Path | None = None,
    include_rest: bool = True,
    strict: bool = False,
) -> list[EventPreparationResult]:
    """Prepare all BIDS event files under a local ds006243 checkout.

    Parameters
    ----------
    bids_root
        Local BIDS dataset root. No data are downloaded by this function.
    output_root
        Destination directory. Defaults to ``<bids_root>/derivatives/events``.
    include_rest
        Include optional post-stimulation rest regressors when present.
    strict
        Raise ``ValueError`` if an events file produces no mapped rows.

    Returns
    -------
    list[EventPreparationResult]
        One summary per processed ``*_events.tsv`` file.
    """

    bids_root = Path(bids_root)
    output_root = Path(output_root) if output_root else bids_root / "derivatives" / "events"

    if not bids_root.exists():
        raise FileNotFoundError(f"BIDS root does not exist: {bids_root}")

    event_files = sorted(
        path
        for path in bids_root.rglob("*_events.tsv")
        if "derivatives" not in path.relative_to(bids_root).parts
    )
    if not event_files:
        raise FileNotFoundError(f"No *_events.tsv files found under: {bids_root}")

    results = []
    for source in event_files:
        events = load_events(source)
        prepared = collapse_events_for_gppi(events, include_rest=include_rest)
        if strict and prepared.empty:
            raise ValueError(f"No rows mapped to collapsed regressors in {source}")

        output = _output_path_for_event_file(source, bids_root, output_root)
        output.parent.mkdir(parents=True, exist_ok=True)
        prepared.to_csv(output, sep="\t", index=False)
        results.append(
            EventPreparationResult(
                source=source,
                output=output,
                n_input_rows=len(events),
                n_output_rows=len(prepared),
                n_unmapped_rows=len(events) - len(prepared),
            )
        )

    return results


def load_ds006243_timing_events(regressor_dir: Path, include_rest: bool = True) -> pd.DataFrame:
    """Load ds006243 FSL-style timing files as prepared gPPI events.

    OpenNeuro ds006243 is distributed as a derivative dataset and stores task
    timing in files named ``*_timing-<condition>.txt`` under
    ``events/<subject>/regressors``. Each file contains whitespace-separated
    ``onset:duration`` entries. This helper maps the condition names onto the
    collapsed gPPI regressors used by this project.
    """

    regressor_dir = Path(regressor_dir)
    if not regressor_dir.exists():
        raise FileNotFoundError(f"ds006243 regressor directory does not exist: {regressor_dir}")

    rows = []
    for timing_file in sorted(regressor_dir.glob("*_timing-*.txt")):
        condition = timing_file.name.split("_timing-", 1)[1].removesuffix(".txt")
        trial_type = DS006243_TIMING_TO_REGRESSOR.get(condition)
        if trial_type is None or (not include_rest and trial_type in POST_STIMULATION_REST_REGRESSORS):
            continue
        for onset, duration in _parse_ds006243_timing_file(timing_file):
            rows.append({"onset": onset, "duration": duration, "trial_type": trial_type})

    if not rows:
        raise ValueError(f"No ds006243 timing rows mapped to gPPI regressors in {regressor_dir}")
    return pd.DataFrame(rows).sort_values(["onset", "duration", "trial_type"]).reset_index(drop=True)


def make_synthetic_events() -> pd.DataFrame:
    """Return a small ds006243-like synthetic events table for examples/tests."""

    return pd.DataFrame(
        {
            "onset": [0, 4, 8, 12, 20, 24, 28, 32, 38, 44],
            "duration": [2, 2, 2, 2, 3, 3, 3, 3, 4, 4],
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
                "post_other_nopain_rest",
            ],
        }
    )


def _parse_ds006243_timing_file(timing_file: Path) -> list[tuple[float, float]]:
    text = timing_file.read_text(encoding="utf-8").strip()
    if not text:
        return []

    pairs = []
    for token in text.split():
        if ":" not in token:
            raise ValueError(f"Expected onset:duration token in {timing_file}, got {token!r}")
        onset_text, duration_text = token.split(":", 1)
        pairs.append((float(onset_text), float(duration_text)))
    return pairs


def _validate_events(events: pd.DataFrame) -> None:
    required_columns = {"onset", "duration"}
    missing = required_columns.difference(events.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Events are missing required columns: {missing_text}")


def _output_path_for_event_file(source: Path, bids_root: Path, output_root: Path) -> Path:
    relative = source.relative_to(bids_root)
    filename = source.name.replace("_events.tsv", "_desc-gppi_events.tsv")
    return output_root / relative.parent / filename


def _row_text(row: pd.Series) -> str:
    parts = []
    ordered_columns = [column for column in TEXT_COLUMNS_PRIORITY if column in row.index]
    remaining_columns = [
        column
        for column in row.index
        if column not in {"onset", "duration", "sample"} and column not in ordered_columns
    ]
    for column in ordered_columns + remaining_columns:
        value = row[column]
        if pd.isna(value):
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            continue
        parts.append(str(value))
    return _normalize_text(" ".join(parts))


def _normalize_text(value: str) -> str:
    text = value.lower()
    text = text.replace("cs+", "csplus").replace("cs-", "csminus")
    text = re.sub(r"[^a-z0-9+.-]+", " ", text)
    return f" {text.strip()} "


def _infer_actor(text: str) -> str | None:
    if _has_any(text, "other", "others", "partner", "stranger", "participant2", "p2"):
        return "other"
    if _has_any(text, "self", "own", "participant1", "p1", "me"):
        return "self"
    return None


def _infer_phase(text: str) -> str | None:
    if _has_any(text, "anticipation", "anticipatory", "anticipate", "cue", "expectation", "csplus", "csminus"):
        return "anticipation"
    if _has_any(text, "stimulation", "stimulus", "stim", "shock", "thermal", "heat", "us", "rating"):
        return "stimulation"
    if _infer_pain(text) is not None and not _has_any(text, "post", "rest", "fixation", "iti", "isi"):
        return "stimulation"
    return None


def _infer_threat(text: str) -> bool | None:
    if _has_any(text, "safety", "safe", "neutral", "nonfear", "no fear", "csminus", "cs -"):
        return False
    if _has_any(text, "fear", "threat", "danger", "aversive", "csplus", "cs +"):
        return True
    return None


def _infer_pain(text: str) -> bool | None:
    if _has_any(text, "nopain", "no pain", "nonpain", "non pain", "notpain", "no-pain", "safe"):
        return False
    if _has_any(text, "painful", "pain", "shock", "heat", "us"):
        return True
    return None


def _has_any(text: str, *needles: str) -> bool:
    return any(_contains_token_or_phrase(text, needle) for needle in needles)


def _contains_token_or_phrase(text: str, needle: str) -> bool:
    normalized = _normalize_text(needle)
    if " " in normalized.strip():
        return normalized.strip() in text
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized.strip())}(?![a-z0-9])", text) is not None
