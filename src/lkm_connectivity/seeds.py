"""Seed time-series extraction for the ds006243 gPPI workflow.

The functions here operate on local fMRIPrep MNI-normalized BOLD images and
binary ROI masks. They do not download data and should write only lightweight
tabular time series to ignored derivatives directories.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd


DEFAULT_SEEDS = {
    "left_anterior_insula": "Left anterior insula",
    "right_anterior_insula": "Right anterior insula",
    "dacc_amcc": "dACC / aMCC",
}


@dataclass(frozen=True)
class SeedExtractionResult:
    """Summary of one extracted seed time series."""

    bold_img: Path
    mask_img: Path
    output_tsv: Path
    seed_name: str
    n_scans: int
    standardized: bool


def load_binary_mask(mask_img: Path | str) -> nib.Nifti1Image:
    """Load and validate a binary ROI mask.

    Parameters
    ----------
    mask_img
        Path to a NIfTI ROI mask. Non-zero voxels are treated as in-mask.

    Returns
    -------
    nibabel.Nifti1Image
        Loaded mask image.
    """

    mask = nib.load(str(mask_img))
    data = np.asanyarray(mask.dataobj)
    if data.ndim != 3:
        raise ValueError(f"ROI mask must be 3D, got shape {data.shape}.")
    if not np.isfinite(data).all():
        raise ValueError("ROI mask contains non-finite values.")
    unique = set(np.unique(data).tolist())
    if not unique.issubset({0, 1, 0.0, 1.0, False, True}):
        raise ValueError("ROI mask must be binary with values 0/1.")
    if int(np.count_nonzero(data)) == 0:
        raise ValueError("ROI mask is empty.")
    return mask


def extract_mean_seed_timeseries(
    bold_img: Path | str | nib.spatialimages.SpatialImage,
    mask_img: Path | str | nib.spatialimages.SpatialImage,
    standardize: bool = False,
) -> pd.Series:
    """Extract the mean BOLD time series from one seed ROI.

    The extraction uses ``nilearn.masking.apply_mask`` and averages across all
    voxels in the binary mask. Optional standardization returns a z-scored time
    series with mean 0 and sample standard deviation 1 when variance is present.
    """

    try:
        from nilearn.masking import apply_mask
    except ImportError as exc:
        raise ImportError("nilearn is required for seed time-series extraction.") from exc

    bold = nib.load(str(bold_img)) if isinstance(bold_img, (str, Path)) else bold_img
    mask = load_binary_mask(mask_img) if isinstance(mask_img, (str, Path)) else _validate_mask_image(mask_img)
    validate_bold_and_mask(bold, mask)

    masked = apply_mask(bold, mask)
    if masked.ndim != 2:
        raise ValueError("Masked BOLD data should be a 2D time-by-voxel array.")
    timeseries = np.asarray(masked, dtype=float).mean(axis=1)
    if standardize:
        timeseries = standardize_timeseries(timeseries)
    return pd.Series(timeseries, name="seed_timeseries")


def standardize_timeseries(timeseries: np.ndarray | pd.Series) -> np.ndarray:
    """Z-score a seed time series, returning zeros for constant series."""

    values = np.asarray(timeseries, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Seed time series contains non-finite values.")
    std = values.std(ddof=1) if len(values) > 1 else 0.0
    if std == 0 or np.isclose(std, 0.0):
        return np.zeros_like(values, dtype=float)
    return (values - values.mean()) / std


def validate_bold_and_mask(
    bold_img: nib.spatialimages.SpatialImage,
    mask_img: nib.spatialimages.SpatialImage,
) -> None:
    """Validate that a 4D BOLD image and 3D mask are spatially compatible."""

    if len(bold_img.shape) != 4:
        raise ValueError(f"BOLD image must be 4D, got shape {bold_img.shape}.")
    if len(mask_img.shape) != 3:
        raise ValueError(f"Mask image must be 3D, got shape {mask_img.shape}.")
    if bold_img.shape[:3] != mask_img.shape:
        raise ValueError(f"BOLD spatial shape {bold_img.shape[:3]} does not match mask shape {mask_img.shape}.")
    if not np.allclose(bold_img.affine, mask_img.affine):
        raise ValueError("BOLD and mask affines do not match.")


def validate_seed_length(
    seed_timeseries: pd.Series | np.ndarray,
    n_scans: int | None = None,
    design_matrix: pd.DataFrame | None = None,
) -> None:
    """Validate seed length against BOLD scan count and design matrix rows."""

    length = len(seed_timeseries)
    if n_scans is not None and length != n_scans:
        raise ValueError(f"Seed time series length ({length}) does not match n_scans ({n_scans}).")
    if design_matrix is not None and length != len(design_matrix):
        raise ValueError(
            f"Seed time series length ({length}) does not match design matrix rows ({len(design_matrix)})."
        )


def extract_seed_to_file(
    bold_img: Path,
    mask_img: Path,
    output_tsv: Path,
    seed_name: str,
    n_scans: int | None = None,
    design_matrix_tsv: Path | None = None,
    standardize: bool = False,
) -> SeedExtractionResult:
    """Extract one seed time series and write it to TSV."""

    design = pd.read_csv(design_matrix_tsv, sep="\t") if design_matrix_tsv else None
    series = extract_mean_seed_timeseries(bold_img=bold_img, mask_img=mask_img, standardize=standardize)
    validate_seed_length(series, n_scans=n_scans, design_matrix=design)
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({seed_name: series}).to_csv(output_tsv, sep="\t", index=False)
    return SeedExtractionResult(
        bold_img=bold_img,
        mask_img=mask_img,
        output_tsv=output_tsv,
        seed_name=seed_name,
        n_scans=len(series),
        standardized=standardize,
    )


def make_synthetic_bold_and_masks(
    n_scans: int = 6,
    shape: tuple[int, int, int] = (4, 4, 4),
) -> tuple[nib.Nifti1Image, dict[str, nib.Nifti1Image]]:
    """Create tiny in-memory synthetic BOLD and ROI masks for tests."""

    affine = np.eye(4)
    data = np.zeros((*shape, n_scans), dtype=float)
    for scan in range(n_scans):
        data[..., scan] = scan
    data[0, 0, 0, :] = np.arange(n_scans, dtype=float) + 10.0
    data[1, 1, 1, :] = np.arange(n_scans, dtype=float) + 20.0
    data[2, 2, 2, :] = np.arange(n_scans, dtype=float) + 30.0
    bold = nib.Nifti1Image(data, affine)

    masks = {}
    for seed_name, index in {
        "left_anterior_insula": (0, 0, 0),
        "right_anterior_insula": (1, 1, 1),
        "dacc_amcc": (2, 2, 2),
    }.items():
        mask_data = np.zeros(shape, dtype=np.uint8)
        mask_data[index] = 1
        masks[seed_name] = nib.Nifti1Image(mask_data, affine)
    return bold, masks


def _validate_mask_image(mask_img: nib.spatialimages.SpatialImage) -> nib.spatialimages.SpatialImage:
    data = np.asanyarray(mask_img.dataobj)
    if data.ndim != 3:
        raise ValueError(f"ROI mask must be 3D, got shape {data.shape}.")
    unique = set(np.unique(data).tolist())
    if not unique.issubset({0, 1, 0.0, 1.0, False, True}):
        raise ValueError("ROI mask must be binary with values 0/1.")
    if int(np.count_nonzero(data)) == 0:
        raise ValueError("ROI mask is empty.")
    return mask_img
