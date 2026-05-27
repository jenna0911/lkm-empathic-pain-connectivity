#!/usr/bin/env python
"""Extract seed-region BOLD time series for ds006243 gPPI.

This script reads local fMRIPrep MNI-normalized BOLD images and local binary
ROI masks. It writes lightweight TSV time series only; it does not download or
commit imaging data.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.seeds import DEFAULT_SEEDS, extract_seed_to_file


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--bold-img", type=Path, required=True, help="Local fMRIPrep MNI-normalized 4D BOLD NIfTI.")
    parser.add_argument("--mask-img", type=Path, required=True, help="Binary 3D ROI mask NIfTI.")
    parser.add_argument("--seed-name", choices=sorted(DEFAULT_SEEDS), required=True, help="Seed region label.")
    parser.add_argument("--output-tsv", type=Path, required=True, help="Output seed time-series TSV.")
    parser.add_argument("--n-scans", type=int, default=None, help="Expected BOLD volume count.")
    parser.add_argument(
        "--design-matrix-tsv",
        type=Path,
        default=None,
        help="Optional design matrix TSV for row-count validation.",
    )
    parser.add_argument("--standardize", action="store_true", help="Z-score the seed time series.")
    args = parser.parse_args()

    result = extract_seed_to_file(
        bold_img=args.bold_img,
        mask_img=args.mask_img,
        output_tsv=args.output_tsv,
        seed_name=args.seed_name,
        n_scans=args.n_scans,
        design_matrix_tsv=args.design_matrix_tsv,
        standardize=args.standardize,
    )
    print(
        f"{result.output_tsv} "
        f"({result.seed_name}, {result.n_scans} scans, standardized={result.standardized})"
    )


if __name__ == "__main__":
    main()
