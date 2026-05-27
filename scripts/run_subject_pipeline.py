#!/usr/bin/env python
"""Run the ds006243 gPPI pipeline for one participant.

This runner orchestrates existing pipeline functions. It never downloads data
and writes outputs only under the requested output root.
"""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import pandas as pd

from lkm_connectivity.confounds import extract_confounds_file
from lkm_connectivity.events import collapse_events_for_gppi, load_events
from lkm_connectivity.firstlevel import MAIN_CONTRAST_NAMES, fit_first_level_gppi_from_files
from lkm_connectivity.glm import DEFAULT_TR, make_first_level_from_files
from lkm_connectivity.gppi import make_gppi_from_files
from lkm_connectivity.seeds import DEFAULT_SEEDS, extract_seed_to_file


@dataclass(frozen=True)
class RunFiles:
    """Input and output paths for one subject/run."""

    participant_label: str
    run_prefix: str
    events_tsv: Path
    confounds_tsv: Path
    bold_img: Path
    prepared_events_tsv: Path
    selected_confounds_tsv: Path
    design_matrix_tsv: Path


@dataclass(frozen=True)
class PipelineOptions:
    """Execution options shared across subject runs."""

    bids_root: Path
    fmriprep_root: Path
    output_root: Path
    seed_mask_dir: Path
    tr: float = DEFAULT_TR
    dry_run: bool = False
    overwrite: bool = False
    standardize_seed: bool = True


def normalize_participant_label(participant_label: str) -> str:
    """Return a BIDS-style participant label with ``sub-`` prefix."""

    return participant_label if participant_label.startswith("sub-") else f"sub-{participant_label}"


def discover_subject_runs(options: PipelineOptions, participant_label: str) -> list[RunFiles]:
    """Find BIDS events, fMRIPrep confounds, and MNI BOLD files for a subject."""

    subject = normalize_participant_label(participant_label)
    events_files = sorted((options.bids_root / subject / "func").glob("*_events.tsv"))
    if not events_files:
        raise FileNotFoundError(f"No events files found for {subject} under {options.bids_root}")

    runs = []
    for events_tsv in events_files:
        run_prefix = events_tsv.name.removesuffix("_events.tsv")
        confounds_tsv = _find_one(
            sorted((options.fmriprep_root / subject / "func").glob(f"{run_prefix}*confounds_timeseries.tsv")),
            f"confounds file for {subject} {run_prefix}",
        )
        bold_img = _find_one(
            sorted((options.fmriprep_root / subject / "func").glob(f"{run_prefix}*space-MNI*desc-preproc_bold.nii.gz"))
            or sorted((options.fmriprep_root / subject / "func").glob(f"{run_prefix}*desc-preproc_bold.nii.gz")),
            f"MNI preprocessed BOLD image for {subject} {run_prefix}",
        )
        func_out = Path(subject) / "func"
        runs.append(
            RunFiles(
                participant_label=subject,
                run_prefix=run_prefix,
                events_tsv=events_tsv,
                confounds_tsv=confounds_tsv,
                bold_img=bold_img,
                prepared_events_tsv=options.output_root / "events" / func_out / f"{run_prefix}_desc-gppi_events.tsv",
                selected_confounds_tsv=options.output_root
                / "confounds"
                / func_out
                / f"{run_prefix}_desc-nuisance_regressors.tsv",
                design_matrix_tsv=options.output_root
                / "design_matrices"
                / func_out
                / f"{run_prefix}_desc-design_matrix.tsv",
            )
        )
    return runs


def run_subject_pipeline(options: PipelineOptions, participant_label: str) -> None:
    """Run all discovered runs and seeds for one participant."""

    subject = normalize_participant_label(participant_label)
    print(f"[subject] {subject}")
    for run_files in discover_subject_runs(options, subject):
        print(f"[run] {run_files.run_prefix}")
        run_single_run(options, run_files)


def run_single_run(options: PipelineOptions, run_files: RunFiles) -> None:
    """Run all pipeline steps for one subject/run."""

    n_scans = None if options.dry_run else _get_n_scans(run_files.bold_img)
    _prepare_events(options, run_files)
    _extract_confounds(options, run_files, n_scans)
    _make_design_matrix(options, run_files, n_scans)

    for seed_name, mask_path in discover_seed_masks(options.seed_mask_dir).items():
        print(f"[seed] {seed_name}")
        seed_tsv = (
            options.output_root
            / "seed_timeseries"
            / run_files.participant_label
            / "func"
            / f"{run_files.run_prefix}_seed-{seed_name}_timeseries.tsv"
        )
        gppi_tsv = (
            options.output_root
            / "gppi"
            / run_files.participant_label
            / "func"
            / f"{run_files.run_prefix}_seed-{seed_name}_desc-gppi_design.tsv"
        )
        contrasts_json = gppi_tsv.with_name(f"{run_files.run_prefix}_seed-{seed_name}_desc-gppi_contrasts.json")
        firstlevel_dir = options.output_root / "firstlevel" / run_files.participant_label / "func" / f"seed-{seed_name}"

        _extract_seed(options, run_files, seed_name, mask_path, seed_tsv, n_scans)
        _build_gppi(options, run_files, seed_tsv, gppi_tsv, contrasts_json)
        _fit_firstlevel(options, run_files, gppi_tsv, contrasts_json, firstlevel_dir)


def discover_seed_masks(seed_mask_dir: Path) -> dict[str, Path]:
    """Find seed masks for supported seed names."""

    masks = {}
    for seed_name in DEFAULT_SEEDS:
        candidates = [
            seed_mask_dir / f"{seed_name}.nii.gz",
            seed_mask_dir / f"{seed_name}_mask.nii.gz",
            seed_mask_dir / f"{seed_name}.nii",
            seed_mask_dir / f"{seed_name}_mask.nii",
        ]
        found = [path for path in candidates if path.exists()]
        if found:
            masks[seed_name] = found[0]
    if not masks:
        raise FileNotFoundError(f"No supported seed masks found in {seed_mask_dir}")
    return masks


def should_run(outputs: list[Path], overwrite: bool) -> bool:
    """Return True when a step should run based on outputs and overwrite."""

    return overwrite or not all(path.exists() for path in outputs)


def _prepare_events(options: PipelineOptions, run_files: RunFiles) -> None:
    _step("prepare events", [run_files.prepared_events_tsv], options)
    if not should_run([run_files.prepared_events_tsv], options.overwrite) or options.dry_run:
        return
    events = load_events(run_files.events_tsv)
    prepared = collapse_events_for_gppi(events)
    run_files.prepared_events_tsv.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(run_files.prepared_events_tsv, sep="\t", index=False)


def _extract_confounds(options: PipelineOptions, run_files: RunFiles, n_scans: int | None) -> None:
    _step("extract confounds", [run_files.selected_confounds_tsv], options)
    if not should_run([run_files.selected_confounds_tsv], options.overwrite) or options.dry_run:
        return
    extract_confounds_file(
        confounds_tsv=run_files.confounds_tsv,
        output_tsv=run_files.selected_confounds_tsv,
        n_scans=n_scans,
        prepared_events_tsv=run_files.prepared_events_tsv,
        repetition_time=options.tr,
        on_mismatch="warn",
    )


def _make_design_matrix(options: PipelineOptions, run_files: RunFiles, n_scans: int | None) -> None:
    _step("make first-level design", [run_files.design_matrix_tsv], options)
    if not should_run([run_files.design_matrix_tsv], options.overwrite) or options.dry_run:
        return
    if n_scans is None:
        raise ValueError("n_scans is required to create the first-level design matrix.")
    make_first_level_from_files(
        events_tsv=run_files.prepared_events_tsv,
        confounds_tsv=run_files.selected_confounds_tsv,
        output_tsv=run_files.design_matrix_tsv,
        n_scans=n_scans,
        tr=options.tr,
    )


def _extract_seed(
    options: PipelineOptions,
    run_files: RunFiles,
    seed_name: str,
    mask_path: Path,
    seed_tsv: Path,
    n_scans: int | None,
) -> None:
    _step("extract seed time series", [seed_tsv], options)
    if not should_run([seed_tsv], options.overwrite) or options.dry_run:
        return
    extract_seed_to_file(
        bold_img=run_files.bold_img,
        mask_img=mask_path,
        output_tsv=seed_tsv,
        seed_name=seed_name,
        n_scans=n_scans,
        design_matrix_tsv=run_files.design_matrix_tsv,
        standardize=options.standardize_seed,
    )


def _build_gppi(options: PipelineOptions, run_files: RunFiles, seed_tsv: Path, gppi_tsv: Path, contrasts_json: Path) -> None:
    _step("build gPPI design", [gppi_tsv, contrasts_json], options)
    if not should_run([gppi_tsv, contrasts_json], options.overwrite) or options.dry_run:
        return
    make_gppi_from_files(
        design_matrix_tsv=run_files.design_matrix_tsv,
        seed_timeseries_tsv=seed_tsv,
        output_tsv=gppi_tsv,
        contrasts_json=contrasts_json,
    )


def _fit_firstlevel(
    options: PipelineOptions,
    run_files: RunFiles,
    gppi_tsv: Path,
    contrasts_json: Path,
    firstlevel_dir: Path,
) -> None:
    expected_maps = [
        firstlevel_dir / f"{contrast}_zmap.nii.gz" for contrast in MAIN_CONTRAST_NAMES
    ] + [
        firstlevel_dir / f"{contrast}_effect_size.nii.gz" for contrast in MAIN_CONTRAST_NAMES
    ]
    _step("fit first-level gPPI", expected_maps, options)
    if not should_run(expected_maps, options.overwrite) or options.dry_run:
        return
    fit_first_level_gppi_from_files(
        bold_img=run_files.bold_img,
        design_matrix_tsv=gppi_tsv,
        contrasts_json=contrasts_json,
        output_dir=firstlevel_dir,
        tr=options.tr,
    )


def _step(name: str, outputs: list[Path], options: PipelineOptions) -> None:
    status = "run" if should_run(outputs, options.overwrite) else "skip"
    if options.dry_run:
        status = f"dry-run {status}"
    print(f"[{status}] {name}")
    for output in outputs:
        print(f"  -> {output}")


def _get_n_scans(bold_img: Path) -> int:
    img = nib.load(str(bold_img))
    if len(img.shape) != 4:
        raise ValueError(f"BOLD image must be 4D, got shape {img.shape}: {bold_img}")
    return int(img.shape[3])


def _find_one(paths: list[Path], description: str) -> Path:
    if not paths:
        raise FileNotFoundError(f"Missing {description}")
    if len(paths) > 1:
        raise ValueError(f"Found multiple candidates for {description}: {paths}")
    return paths[0]


def parse_args() -> PipelineOptions:
    """Parse CLI arguments and return pipeline options plus participant label."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--bids-root", type=Path, required=True)
    parser.add_argument("--fmriprep-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--participant-label", required=True)
    parser.add_argument("--seed-mask-dir", type=Path, required=True)
    parser.add_argument("--tr", type=float, default=DEFAULT_TR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-standardize-seed", action="store_true")
    args = parser.parse_args()
    options = PipelineOptions(
        bids_root=args.bids_root,
        fmriprep_root=args.fmriprep_root,
        output_root=args.output_root,
        seed_mask_dir=args.seed_mask_dir,
        tr=args.tr,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        standardize_seed=not args.no_standardize_seed,
    )
    return options, args.participant_label


def main() -> None:
    """CLI entry point."""

    options, participant_label = parse_args()
    run_subject_pipeline(options, participant_label)


if __name__ == "__main__":
    main()
