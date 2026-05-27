#!/usr/bin/env python
"""Extract fMRIPrep nuisance regressors for first-level GLM and gPPI.

The script reads local fMRIPrep confounds files and writes selected nuisance
regressors. It does not download data or write raw neuroimaging files.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.confounds import (
    extract_confounds_directory,
    extract_confounds_file,
    output_path_for_confounds,
)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fmriprep-dir",
        type=Path,
        default=Path("derivatives/fmriprep"),
        help="Local fMRIPrep derivatives directory. Default: derivatives/fmriprep",
    )
    parser.add_argument(
        "--confounds-tsv",
        type=Path,
        default=None,
        help="Optional single confounds_timeseries.tsv file to process.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("derivatives/confounds"),
        help="Output directory for selected nuisance regressors.",
    )
    parser.add_argument(
        "--output-tsv",
        type=Path,
        default=None,
        help="Output TSV for single-file mode. Defaults to a derived filename under --output-root.",
    )
    parser.add_argument(
        "--n-scans",
        type=int,
        default=None,
        help="Expected BOLD volume count for single-file validation.",
    )
    parser.add_argument(
        "--prepared-events",
        type=Path,
        default=None,
        help="Optional prepared events TSV for single-file validation.",
    )
    parser.add_argument(
        "--tr",
        type=float,
        default=None,
        help="Repetition time in seconds for optional event timing validation.",
    )
    parser.add_argument(
        "--on-mismatch",
        choices=("warn", "error", "ignore"),
        default="warn",
        help="How to handle row-count validation mismatches.",
    )
    args = parser.parse_args()

    if args.confounds_tsv:
        output_tsv = args.output_tsv or output_path_for_confounds(
            args.confounds_tsv,
            args.fmriprep_dir,
            args.output_root,
        )
        results = [
            extract_confounds_file(
                confounds_tsv=args.confounds_tsv,
                output_tsv=output_tsv,
                n_scans=args.n_scans,
                prepared_events_tsv=args.prepared_events,
                repetition_time=args.tr,
                on_mismatch=args.on_mismatch,
            )
        ]
    else:
        results = extract_confounds_directory(
            fmriprep_dir=args.fmriprep_dir,
            output_root=args.output_root,
            on_mismatch=args.on_mismatch,
        )

    for result in results:
        print(
            f"{result.source} -> {result.output} "
            f"({len(result.selected_columns)} columns, {result.n_output_rows} rows)"
        )


if __name__ == "__main__":
    main()
