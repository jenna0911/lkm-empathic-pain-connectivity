#!/usr/bin/env python
"""Build gPPI design matrices and contrast definitions.

This script combines a first-level design matrix with one seed time series. It
writes tabular outputs only and does not fit a full fMRI model.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.gppi import make_gppi_from_files


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--design-matrix-tsv", type=Path, required=True, help="First-level design matrix TSV.")
    parser.add_argument("--seed-timeseries-tsv", type=Path, required=True, help="Seed time-series TSV.")
    parser.add_argument("--output-tsv", type=Path, required=True, help="Output gPPI design matrix TSV.")
    parser.add_argument("--contrasts-json", type=Path, required=True, help="Output gPPI contrast definitions JSON.")
    parser.add_argument(
        "--seed-column",
        default=None,
        help="Seed column to use when the seed TSV contains multiple columns.",
    )
    parser.add_argument("--no-center-seed", action="store_true", help="Do not mean-center the seed time series.")
    args = parser.parse_args()

    result = make_gppi_from_files(
        design_matrix_tsv=args.design_matrix_tsv,
        seed_timeseries_tsv=args.seed_timeseries_tsv,
        output_tsv=args.output_tsv,
        contrasts_json=args.contrasts_json,
        seed_column=args.seed_column,
        center_seed=not args.no_center_seed,
    )
    print(
        f"{result.output_tsv} and {result.contrasts_json} "
        f"({result.n_rows} rows, {len(result.interaction_columns)} interactions, "
        f"{len(result.contrast_names)} contrasts)"
    )


if __name__ == "__main__":
    main()
