#!/usr/bin/env python
"""Run second-level LKM-vs-PMR analyses on first-level gPPI contrast maps."""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.secondlevel import run_second_level_from_files


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--participants-tsv", type=Path, required=True, help="TSV with subject_id and group columns.")
    parser.add_argument(
        "--maps-tsv",
        type=Path,
        required=True,
        help="TSV with subject_id, contrast_name, seed_name, and map_path columns.",
    )
    parser.add_argument("--contrast-name", required=True, help="First-level contrast name to analyze.")
    parser.add_argument("--seed-name", required=True, help="Seed name to analyze.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for design and z maps.")
    parser.add_argument("--mask-img", type=Path, default=None, help="Optional group analysis mask.")
    parser.add_argument("--smoothing-fwhm", type=float, default=None, help="Optional smoothing FWHM in mm.")
    args = parser.parse_args()

    result = run_second_level_from_files(
        participants_tsv=args.participants_tsv,
        maps_tsv=args.maps_tsv,
        contrast_name=args.contrast_name,
        seed_name=args.seed_name,
        output_dir=args.output_dir,
        mask_img=args.mask_img,
        smoothing_fwhm=args.smoothing_fwhm,
    )
    print(
        f"Ran second-level analysis for {result.n_subjects} subjects. "
        f"Design: {result.design_matrix_tsv}. Maps: {result.output_dir}"
    )


if __name__ == "__main__":
    main()
