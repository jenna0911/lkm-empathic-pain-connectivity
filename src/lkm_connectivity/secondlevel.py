"""Second-level group analysis for LKM versus PMR gPPI maps.

This module runs group-level models from first-level contrast maps. It expects
lightweight metadata tables and local NIfTI contrast maps; it does not download
or create raw neuroimaging data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd


GROUPS = ("LKM", "PMR")


@dataclass(frozen=True)
class SecondLevelResult:
    """Summary of written second-level outputs."""

    contrast_name: str
    seed_name: str
    output_dir: Path
    design_matrix_tsv: Path
    z_maps: dict[str, Path]
    n_subjects: int


def load_participants(participants_tsv: Path) -> pd.DataFrame:
    """Load and validate participant group metadata."""

    participants = pd.read_csv(participants_tsv, sep="\t")
    required = {"subject_id", "group"}
    missing = required.difference(participants.columns)
    if missing:
        raise ValueError(f"Participants TSV is missing required columns: {', '.join(sorted(missing))}")
    participants = participants.loc[:, ["subject_id", "group"]].copy()
    participants["subject_id"] = participants["subject_id"].astype(str)
    participants["group"] = participants["group"].astype(str).str.upper()
    unknown = sorted(set(participants["group"]) - set(GROUPS))
    if unknown:
        raise ValueError(f"Unknown group labels: {', '.join(unknown)}. Expected LKM or PMR.")
    if participants["subject_id"].duplicated().any():
        duplicates = sorted(participants.loc[participants["subject_id"].duplicated(), "subject_id"].unique())
        raise ValueError(f"Duplicate participants found: {', '.join(duplicates)}")
    return participants


def load_contrast_map_table(maps_tsv: Path) -> pd.DataFrame:
    """Load first-level contrast-map metadata."""

    maps = pd.read_csv(maps_tsv, sep="\t")
    required = {"subject_id", "contrast_name", "seed_name", "map_path"}
    missing = required.difference(maps.columns)
    if missing:
        raise ValueError(f"Maps TSV is missing required columns: {', '.join(sorted(missing))}")
    maps = maps.loc[:, ["subject_id", "contrast_name", "seed_name", "map_path"]].copy()
    maps["subject_id"] = maps["subject_id"].astype(str)
    return maps


def prepare_second_level_inputs(
    participants: pd.DataFrame,
    maps: pd.DataFrame,
    contrast_name: str,
    seed_name: str,
) -> tuple[list[str], pd.DataFrame]:
    """Merge metadata and validate one first-level map per subject."""

    selected = maps.loc[(maps["contrast_name"] == contrast_name) & (maps["seed_name"] == seed_name)].copy()
    if selected.empty:
        raise ValueError(f"No maps found for contrast `{contrast_name}` and seed `{seed_name}`.")

    counts = selected.groupby("subject_id").size()
    duplicated = sorted(counts[counts > 1].index.astype(str))
    if duplicated:
        raise ValueError(f"Subjects with more than one matching contrast map: {', '.join(duplicated)}")

    merged = participants.merge(selected, on="subject_id", how="left", validate="one_to_one")
    missing_maps = sorted(merged.loc[merged["map_path"].isna(), "subject_id"].astype(str))
    if missing_maps:
        raise ValueError(f"Missing contrast maps for subjects: {', '.join(missing_maps)}")

    for group in GROUPS:
        if group not in set(merged["group"]):
            raise ValueError(f"Group `{group}` has no participants for this analysis.")

    map_paths = [str(Path(path)) for path in merged["map_path"]]
    missing_files = [path for path in map_paths if not Path(path).exists()]
    if missing_files:
        raise FileNotFoundError(f"Contrast map files do not exist: {', '.join(missing_files)}")

    design = build_second_level_design_matrix(merged)
    return map_paths, design


def build_second_level_design_matrix(merged_metadata: pd.DataFrame) -> pd.DataFrame:
    """Build a second-level design matrix for one-sample and LKM-vs-PMR tests."""

    design = pd.DataFrame(
        {
            "subject_id": merged_metadata["subject_id"].astype(str).to_numpy(),
            "group": merged_metadata["group"].astype(str).to_numpy(),
            "intercept": 1.0,
            "group_lkm": (merged_metadata["group"].astype(str) == "LKM").astype(float).to_numpy(),
        }
    )
    return design


def run_second_level_models(
    map_paths: list[str],
    design: pd.DataFrame,
    output_dir: Path,
    contrast_name: str,
    seed_name: str,
    mask_img: Path | None = None,
    smoothing_fwhm: float | None = None,
) -> dict[str, Path]:
    """Fit one-sample and LKM-vs-PMR second-level models and write z maps."""

    try:
        from nilearn.glm.second_level import SecondLevelModel
    except ImportError as exc:
        raise ImportError("nilearn is required for second-level analysis.") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    one_sample_design = design.loc[:, ["intercept"]]
    group_design = design.loc[:, ["intercept", "group_lkm"]]

    z_maps = {}
    one_sample_model = SecondLevelModel(
        mask_img=str(mask_img) if mask_img else None,
        smoothing_fwhm=smoothing_fwhm,
        minimize_memory=False,
    ).fit(map_paths, design_matrix=one_sample_design)
    z_maps["one_sample"] = _write_z_map(
        one_sample_model.compute_contrast("intercept", output_type="z_score"),
        output_dir,
        "one_sample",
        contrast_name,
        seed_name,
    )

    group_model = SecondLevelModel(
        mask_img=str(mask_img) if mask_img else None,
        smoothing_fwhm=smoothing_fwhm,
        minimize_memory=False,
    ).fit(map_paths, design_matrix=group_design)
    z_maps["lkm_gt_pmr"] = _write_z_map(
        group_model.compute_contrast([0.0, 1.0], output_type="z_score"),
        output_dir,
        "lkm_gt_pmr",
        contrast_name,
        seed_name,
    )
    z_maps["pmr_gt_lkm"] = _write_z_map(
        group_model.compute_contrast([0.0, -1.0], output_type="z_score"),
        output_dir,
        "pmr_gt_lkm",
        contrast_name,
        seed_name,
    )
    return z_maps


def run_second_level_from_files(
    participants_tsv: Path,
    maps_tsv: Path,
    contrast_name: str,
    seed_name: str,
    output_dir: Path,
    mask_img: Path | None = None,
    smoothing_fwhm: float | None = None,
) -> SecondLevelResult:
    """Load metadata, run second-level models, and write group z maps."""

    participants = load_participants(participants_tsv)
    maps = load_contrast_map_table(maps_tsv)
    map_paths, design = prepare_second_level_inputs(participants, maps, contrast_name, seed_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    design_path = output_dir / f"{contrast_name}_seed-{seed_name}_second_level_design.tsv"
    design.to_csv(design_path, sep="\t", index=False)
    z_maps = run_second_level_models(
        map_paths=map_paths,
        design=design,
        output_dir=output_dir,
        contrast_name=contrast_name,
        seed_name=seed_name,
        mask_img=mask_img,
        smoothing_fwhm=smoothing_fwhm,
    )
    return SecondLevelResult(
        contrast_name=contrast_name,
        seed_name=seed_name,
        output_dir=output_dir,
        design_matrix_tsv=design_path,
        z_maps=z_maps,
        n_subjects=len(design),
    )


def make_synthetic_secondlevel_inputs(
    output_dir: Path,
    n_per_group: int = 3,
    shape: tuple[int, int, int] = (5, 5, 5),
    contrast_name: str = "other_pain_stimulation_vs_nopain",
    seed_name: str = "left_anterior_insula",
) -> tuple[Path, Path, Path]:
    """Create synthetic first-level maps and metadata in a temporary directory."""

    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(123)
    participants_rows = []
    maps_rows = []
    affine = np.eye(4)
    mask_data = np.ones(shape, dtype=np.uint8)
    mask_path = output_dir / "mask.nii.gz"
    nib.Nifti1Image(mask_data, affine).to_filename(mask_path)

    for group, offset in [("LKM", 0.8), ("PMR", -0.2)]:
        for index in range(n_per_group):
            subject_id = f"sub-{group.lower()}-{index + 1:02d}"
            data = rng.normal(scale=0.05, size=shape)
            data[2, 2, 2] += offset
            map_path = output_dir / f"{subject_id}_{contrast_name}_seed-{seed_name}_zmap.nii.gz"
            nib.Nifti1Image(data, affine).to_filename(map_path)
            participants_rows.append({"subject_id": subject_id, "group": group})
            maps_rows.append(
                {
                    "subject_id": subject_id,
                    "contrast_name": contrast_name,
                    "seed_name": seed_name,
                    "map_path": str(map_path),
                }
            )

    participants_tsv = output_dir / "participants.tsv"
    maps_tsv = output_dir / "firstlevel_maps.tsv"
    pd.DataFrame(participants_rows).to_csv(participants_tsv, sep="\t", index=False)
    pd.DataFrame(maps_rows).to_csv(maps_tsv, sep="\t", index=False)
    return participants_tsv, maps_tsv, mask_path


def _write_z_map(img: nib.spatialimages.SpatialImage, output_dir: Path, model_name: str, contrast_name: str, seed_name: str) -> Path:
    path = output_dir / f"{model_name}_{contrast_name}_seed-{seed_name}_zmap.nii.gz"
    img.to_filename(path)
    return path
