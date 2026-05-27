"""First-level gPPI model fitting for ds006243.

This module fits a Nilearn first-level model from a local preprocessed BOLD
image, a precomputed gPPI design matrix, and JSON contrast definitions. It does
not download data.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd


DEFAULT_TR = 2.5

MAIN_CONTRAST_ALIASES = {
    "other_fear_anticipation_vs_safety": "other_fear_anticipation_gt_other_safety_anticipation",
    "other_pain_stimulation_vs_nopain": "other_pain_stimulation_gt_other_nopain_stimulation",
    "other_specific_fear_anticipation": "other_vs_self_fear_anticipation",
    "other_specific_pain_stimulation": "other_vs_self_pain_stimulation",
}

MAIN_CONTRAST_NAMES = tuple(MAIN_CONTRAST_ALIASES)


@dataclass(frozen=True)
class FirstLevelFitResult:
    """Summary of first-level gPPI contrast outputs."""

    bold_img: Path
    design_matrix_tsv: Path
    contrasts_json: Path
    output_dir: Path
    n_scans: int
    z_maps: dict[str, Path]
    effect_maps: dict[str, Path]


def load_gppi_design_matrix(design_matrix_tsv: Path) -> pd.DataFrame:
    """Load a gPPI design matrix TSV.

    If a ``frame_time`` column is present, it is used as the DataFrame index and
    removed from the model regressors.
    """

    design = pd.read_csv(design_matrix_tsv, sep="\t")
    if "frame_time" in design.columns:
        design = design.set_index("frame_time")
    return design.apply(pd.to_numeric, errors="raise")


def load_contrast_definitions(contrasts_json: Path, design_columns: list[str]) -> dict[str, np.ndarray]:
    """Load contrast definitions and return vectors aligned to ``design_columns``."""

    raw = json.loads(Path(contrasts_json).read_text(encoding="utf-8"))
    normalized = _normalize_main_contrast_names(raw)
    vectors = {}
    for name in MAIN_CONTRAST_NAMES:
        if name not in normalized:
            raise ValueError(f"Missing required contrast definition: {name}")
        vectors[name] = contrast_definition_to_vector(normalized[name], design_columns, contrast_name=name)
    return vectors


def contrast_definition_to_vector(
    definition: dict[str, object],
    design_columns: list[str],
    contrast_name: str,
) -> np.ndarray:
    """Convert a JSON contrast definition to a vector for current design columns."""

    if "weights" in definition:
        weights = definition["weights"]
        if not isinstance(weights, dict):
            raise ValueError(f"Contrast `{contrast_name}` has invalid weights.")
        vector = np.zeros(len(design_columns), dtype=float)
        missing = [column for column in weights if column not in design_columns]
        if missing:
            raise ValueError(f"Contrast `{contrast_name}` references missing design columns: {', '.join(missing)}")
        for column, weight in weights.items():
            vector[design_columns.index(column)] = float(weight)
        return vector

    if "vector" in definition and "columns" in definition:
        source_columns = list(definition["columns"])
        source_vector = np.asarray(definition["vector"], dtype=float)
        if len(source_columns) != len(source_vector):
            raise ValueError(f"Contrast `{contrast_name}` vector length does not match its columns.")
        weights = {
            column: float(weight)
            for column, weight in zip(source_columns, source_vector)
            if not np.isclose(float(weight), 0.0)
        }
        return contrast_definition_to_vector({"weights": weights}, design_columns, contrast_name)

    raise ValueError(f"Contrast `{contrast_name}` must define either weights or vector+columns.")


def validate_bold_design_rows(bold_img: Path | nib.spatialimages.SpatialImage, design_matrix: pd.DataFrame) -> int:
    """Validate that BOLD volumes match design matrix rows."""

    img = nib.load(str(bold_img)) if isinstance(bold_img, (str, Path)) else bold_img
    if len(img.shape) != 4:
        raise ValueError(f"BOLD image must be 4D, got shape {img.shape}.")
    n_scans = int(img.shape[3])
    if n_scans != len(design_matrix):
        raise ValueError(
            f"BOLD n_scans ({n_scans}) do not match gPPI design matrix rows ({len(design_matrix)}). "
            "Check trimming and regenerate confounds/events/design consistently."
        )
    return n_scans


def fit_first_level_gppi(
    bold_img: Path,
    design_matrix: pd.DataFrame,
    contrast_vectors: dict[str, np.ndarray],
    output_dir: Path,
    tr: float = DEFAULT_TR,
    mask_img: Path | None = None,
    smoothing_fwhm: float | None = None,
) -> tuple[dict[str, Path], dict[str, Path]]:
    """Fit a first-level model and write z/effect contrast maps."""

    try:
        from nilearn.glm.first_level import FirstLevelModel
    except ImportError as exc:
        raise ImportError("nilearn is required for first-level gPPI fitting.") from exc

    validate_bold_design_rows(bold_img, design_matrix)
    output_dir.mkdir(parents=True, exist_ok=True)
    model = FirstLevelModel(
        t_r=tr,
        mask_img=str(mask_img) if mask_img else None,
        smoothing_fwhm=smoothing_fwhm,
        drift_model=None,
        signal_scaling=False,
        minimize_memory=False,
    )
    model = model.fit(str(bold_img), design_matrices=[design_matrix])

    z_maps = {}
    effect_maps = {}
    for name, vector in contrast_vectors.items():
        z_img = model.compute_contrast(vector, output_type="z_score")
        effect_img = model.compute_contrast(vector, output_type="effect_size")
        z_path = output_dir / f"{name}_zmap.nii.gz"
        effect_path = output_dir / f"{name}_effect_size.nii.gz"
        z_img.to_filename(z_path)
        effect_img.to_filename(effect_path)
        z_maps[name] = z_path
        effect_maps[name] = effect_path
    return z_maps, effect_maps


def fit_first_level_gppi_from_files(
    bold_img: Path,
    design_matrix_tsv: Path,
    contrasts_json: Path,
    output_dir: Path,
    tr: float = DEFAULT_TR,
    mask_img: Path | None = None,
    smoothing_fwhm: float | None = None,
) -> FirstLevelFitResult:
    """Load inputs, fit first-level gPPI contrasts, and write NIfTI maps."""

    design = load_gppi_design_matrix(design_matrix_tsv)
    n_scans = validate_bold_design_rows(bold_img, design)
    contrasts = load_contrast_definitions(contrasts_json, list(design.columns))
    z_maps, effect_maps = fit_first_level_gppi(
        bold_img=bold_img,
        design_matrix=design,
        contrast_vectors=contrasts,
        output_dir=output_dir,
        tr=tr,
        mask_img=mask_img,
        smoothing_fwhm=smoothing_fwhm,
    )
    return FirstLevelFitResult(
        bold_img=bold_img,
        design_matrix_tsv=design_matrix_tsv,
        contrasts_json=contrasts_json,
        output_dir=output_dir,
        n_scans=n_scans,
        z_maps=z_maps,
        effect_maps=effect_maps,
    )


def make_synthetic_firstlevel_inputs(
    n_scans: int = 24,
    shape: tuple[int, int, int] = (5, 5, 5),
) -> tuple[nib.Nifti1Image, nib.Nifti1Image, pd.DataFrame, dict[str, dict[str, object]]]:
    """Create tiny synthetic BOLD, mask, gPPI design, and contrasts for tests."""

    from lkm_connectivity.gppi import build_contrast_definitions, build_gppi_design_matrix, make_synthetic_gppi_inputs

    design, seed = make_synthetic_gppi_inputs(n_scans=n_scans)
    gppi_design = build_gppi_design_matrix(design, seed)
    contrasts = build_contrast_definitions(gppi_design)
    canonical = _normalize_main_contrast_names(contrasts)

    rng = np.random.default_rng(42)
    data = rng.normal(scale=0.05, size=(*shape, n_scans))
    signal = gppi_design["gppi_other_fear_anticipation"].to_numpy(dtype=float)
    data[2, 2, 2, :] += signal
    affine = np.eye(4)
    bold = nib.Nifti1Image(data, affine)
    mask_data = np.ones(shape, dtype=np.uint8)
    mask = nib.Nifti1Image(mask_data, affine)
    return bold, mask, gppi_design, canonical


def _normalize_main_contrast_names(raw: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    normalized = dict(raw)
    for canonical, alias in MAIN_CONTRAST_ALIASES.items():
        if canonical not in normalized and alias in normalized:
            normalized[canonical] = normalized[alias]
    return normalized
