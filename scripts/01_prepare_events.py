#!/usr/bin/env python
"""Prepare ds006243 BIDS events for gPPI analyses.

This script reads local ``*_events.tsv`` files from a BIDS root and writes
collapsed event files to ``derivatives/events/``. It does not download data.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.events import prepare_bids_events


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bids-root",
        type=Path,
        default=Path("data/ds006243"),
        help="Local ds006243 BIDS root. Default: data/ds006243",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Output directory. Default: <bids-root>/derivatives/events",
    )
    parser.add_argument(
        "--no-rest",
        action="store_true",
        help="Do not include optional post-stimulation rest regressors.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any events file produces zero mapped rows.",
    )
    args = parser.parse_args()

    results = prepare_bids_events(
        bids_root=args.bids_root,
        output_root=args.output_root,
        include_rest=not args.no_rest,
        strict=args.strict,
    )

    for result in results:
        print(
            f"{result.source} -> {result.output} "
            f"({result.n_output_rows}/{result.n_input_rows} rows mapped; "
            f"{result.n_unmapped_rows} unmapped)"
        )


if __name__ == "__main__":
    main()
