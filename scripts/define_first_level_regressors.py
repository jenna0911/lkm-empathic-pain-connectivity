#!/usr/bin/env python
"""Define first-level GLM regressors for task phases and conditions."""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.events import load_events
from lkm_connectivity.glm import define_first_level_regressors


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("events_tsv", type=Path, help="Analysis-ready events.tsv file.")
    parser.add_argument("output_tsv", type=Path, help="Output first-level regressors TSV.")
    args = parser.parse_args()

    events = load_events(args.events_tsv)
    regressors = define_first_level_regressors(events)
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    regressors.to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()
