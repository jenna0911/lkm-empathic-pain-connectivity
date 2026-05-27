#!/usr/bin/env python
"""Build a first-level design matrix template for ds006243 gPPI.

This script combines prepared gPPI events with selected nuisance confounds. It
does not fit a full fMRI model or load BOLD image data.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.glm import DEFAULT_TR, make_first_level_from_files


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--events-tsv", type=Path, required=True, help="Prepared *_desc-gppi_events.tsv file.")
    parser.add_argument(
        "--confounds-tsv",
        type=Path,
        default=None,
        help="Selected nuisance regressors TSV from scripts/02_extract_confounds.py.",
    )
    parser.add_argument("--output-tsv", type=Path, required=True, help="Output design-matrix TSV.")
    parser.add_argument("--n-scans", type=int, required=True, help="Number of BOLD volumes in this run.")
    parser.add_argument("--tr", type=float, default=DEFAULT_TR, help="Repetition time in seconds. Default: 2.5")
    parser.add_argument(
        "--no-rest",
        action="store_true",
        help="Disallow optional post-stimulation rest regressors.",
    )
    parser.add_argument("--hrf-model", default="glover", help="Nilearn HRF model. Default: glover")
    parser.add_argument(
        "--drift-model",
        default=None,
        help="Nilearn drift model. Default: None because fMRIPrep cosine regressors are confounds.",
    )
    args = parser.parse_args()

    result = make_first_level_from_files(
        events_tsv=args.events_tsv,
        confounds_tsv=args.confounds_tsv,
        output_tsv=args.output_tsv,
        n_scans=args.n_scans,
        tr=args.tr,
        include_rest=not args.no_rest,
        hrf_model=args.hrf_model,
        drift_model=args.drift_model,
    )
    print(
        f"{result.output_tsv} "
        f"({result.n_scans} scans, TR={result.tr}, {len(result.columns)} columns)"
    )


if __name__ == "__main__":
    main()
