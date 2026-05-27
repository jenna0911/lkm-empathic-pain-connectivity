"""Generalized PPI design-matrix construction for ds006243.

This module builds tabular gPPI regressors and contrast definitions only. It
does not fit voxelwise fMRI models or read raw imaging data.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lkm_connectivity.events import GPPI_REGRESSORS


TASK_CONDITIONS = GPPI_REGRESSORS
GPPI_PREFIX = "gppi_"

MAIN_GPPI_CONTRASTS = {
    "other_fear_anticipation_gt_other_safety_anticipation": {
        "gppi_other_fear_anticipation": 1.0,
        "gppi_other_safety_anticipation": -1.0,
    },
    "other_pain_stimulation_gt_other_nopain_stimulation": {
        "gppi_other_pain_stimulation": 1.0,
        "gppi_other_nopain_stimulation": -1.0,
    },
    "other_vs_self_fear_anticipation": {
        "gppi_other_fear_anticipation": 1.0,
        "gppi_other_safety_anticipation": -1.0,
        "gppi_self_fear_anticipation": -1.0,
        "gppi_self_safety_anticipation": 1.0,
    },
    "other_vs_self_pain_stimulation": {
        "gppi_other_pain_stimulation": 1.0,
        "gppi_other_nopain_stimulation": -1.0,
        "gppi_self_pain_stimulation": -1.0,
        "gppi_self_nopain_stimulation": 1.0,
    },
}


@dataclass(frozen=True)
class GppiConstructionResult:
    """Summary of a generated gPPI design matrix and contrasts."""

    design_matrix_tsv: Path
    seed_timeseries_tsv: Path
    output_tsv: Path
    contrasts_json: Path
    n_rows: int
    interaction_columns: tuple[str, ...]
    contrast_names: tuple[str, ...]


def build_gppi_interactions(
    psychological_regressors: pd.DataFrame,
    seed_timeseries: pd.Series,
    center_seed: bool = True,
) -> pd.DataFrame:
    """Build seed-by-condition interaction regressors.

    Parameters
    ----------
    psychological_regressors
        Data frame containing task-condition columns.
    seed_timeseries
        Seed BOLD time series with one value per scan.
    center_seed
        Whether to mean-center the seed before multiplying by task regressors.
    """

    validate_row_counts(psychological_regressors, seed_timeseries, "psychological regressors", "seed time series")
    seed = prepare_seed_timeseries(seed_timeseries, center=center_seed)
    interactions = {}
    for column in psychological_regressors.columns:
        interactions[f"{GPPI_PREFIX}{column}"] = psychological_regressors[column].to_numpy(dtype=float) * seed
    return pd.DataFrame(interactions, index=psychological_regressors.index)


def build_gppi_design_matrix(
    design_matrix: pd.DataFrame,
    seed_timeseries: pd.Series | pd.DataFrame,
    task_conditions: tuple[str, ...] | list[str] = TASK_CONDITIONS,
    center_seed: bool = True,
    seed_column_name: str = "seed_timeseries",
) -> pd.DataFrame:
    """Append seed and gPPI interaction regressors to a first-level design matrix."""

    seed = coerce_seed_series(seed_timeseries)
    validate_row_counts(design_matrix, seed, "design matrix", "seed time series")
    missing = [column for column in task_conditions if column not in design_matrix.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Design matrix is missing task condition columns: {missing_text}")

    task_regressors = design_matrix.loc[:, list(task_conditions)].apply(pd.to_numeric, errors="raise")
    interactions = build_gppi_interactions(task_regressors, seed, center_seed=center_seed)

    gppi_design = design_matrix.copy()
    if seed_column_name in gppi_design.columns:
        raise ValueError(f"Design matrix already contains seed column `{seed_column_name}`.")
    gppi_design[seed_column_name] = prepare_seed_timeseries(seed, center=center_seed)
    for column in interactions.columns:
        if column in gppi_design.columns:
            raise ValueError(f"Design matrix already contains interaction column `{column}`.")
        gppi_design[column] = interactions[column]
    return gppi_design


def build_contrast_definitions(
    gppi_design: pd.DataFrame,
    contrast_specs: dict[str, dict[str, float]] | None = None,
) -> dict[str, dict[str, object]]:
    """Create named contrast definitions and full vectors for a gPPI design."""

    specs = contrast_specs or MAIN_GPPI_CONTRASTS
    definitions = {}
    columns = list(gppi_design.columns)
    for name, weights in specs.items():
        missing = [column for column in weights if column not in columns]
        if missing:
            missing_text = ", ".join(missing)
            raise ValueError(f"Contrast `{name}` references missing columns: {missing_text}")
        vector = np.zeros(len(columns), dtype=float)
        for column, weight in weights.items():
            vector[columns.index(column)] = float(weight)
        definitions[name] = {
            "weights": {column: float(weight) for column, weight in weights.items()},
            "columns": columns,
            "vector": vector.tolist(),
        }
    return definitions


def write_contrast_definitions(contrast_definitions: dict[str, dict[str, object]], output_json: Path) -> None:
    """Write contrast definitions as pretty JSON."""

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(contrast_definitions, indent=2) + "\n", encoding="utf-8")


def make_gppi_from_files(
    design_matrix_tsv: Path,
    seed_timeseries_tsv: Path,
    output_tsv: Path,
    contrasts_json: Path,
    seed_column: str | None = None,
    center_seed: bool = True,
) -> GppiConstructionResult:
    """Load inputs, write a gPPI design matrix TSV and contrast JSON."""

    design = pd.read_csv(design_matrix_tsv, sep="\t")
    seed_table = pd.read_csv(seed_timeseries_tsv, sep="\t")
    seed = seed_table.loc[:, seed_column] if seed_column else coerce_seed_series(seed_table)
    gppi_design = build_gppi_design_matrix(design, seed, center_seed=center_seed)
    contrasts = build_contrast_definitions(gppi_design)

    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    gppi_design.to_csv(output_tsv, sep="\t", index=False)
    write_contrast_definitions(contrasts, contrasts_json)
    return GppiConstructionResult(
        design_matrix_tsv=design_matrix_tsv,
        seed_timeseries_tsv=seed_timeseries_tsv,
        output_tsv=output_tsv,
        contrasts_json=contrasts_json,
        n_rows=len(gppi_design),
        interaction_columns=tuple(column for column in gppi_design.columns if column.startswith(GPPI_PREFIX)),
        contrast_names=tuple(contrasts),
    )


def coerce_seed_series(seed_timeseries: pd.Series | pd.DataFrame) -> pd.Series:
    """Return a single numeric seed time series from a Series or one-column table."""

    if isinstance(seed_timeseries, pd.DataFrame):
        if seed_timeseries.shape[1] != 1:
            raise ValueError("Seed time-series table must contain exactly one column or specify --seed-column.")
        seed = seed_timeseries.iloc[:, 0]
    else:
        seed = seed_timeseries
    return pd.to_numeric(seed, errors="raise").reset_index(drop=True)


def prepare_seed_timeseries(seed_timeseries: pd.Series | np.ndarray, center: bool = True) -> np.ndarray:
    """Convert a seed time series to a finite numeric vector, optionally centered."""

    seed = np.asarray(seed_timeseries, dtype=float)
    if seed.ndim != 1:
        raise ValueError("Seed time series must be one-dimensional.")
    if not np.isfinite(seed).all():
        raise ValueError("Seed time series contains non-finite values.")
    if center:
        seed = seed - seed.mean()
    return seed


def validate_row_counts(
    left: pd.DataFrame | pd.Series,
    right: pd.DataFrame | pd.Series,
    left_name: str,
    right_name: str,
) -> None:
    """Validate that two scan-wise tables have the same number of rows."""

    if len(left) != len(right):
        raise ValueError(f"{left_name} rows ({len(left)}) do not match {right_name} rows ({len(right)}).")


def make_synthetic_gppi_inputs(n_scans: int = 8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create tiny synthetic design and seed tables for tests/examples."""

    design = pd.DataFrame({condition: np.zeros(n_scans, dtype=float) for condition in TASK_CONDITIONS})
    for index, condition in enumerate(TASK_CONDITIONS):
        design.loc[index % n_scans, condition] = 1.0
    design["constant"] = 1.0
    design["trans_x"] = np.linspace(0.0, 0.1, n_scans)
    seed = pd.DataFrame({"left_anterior_insula": np.linspace(-1.0, 1.0, n_scans)})
    return design, seed
