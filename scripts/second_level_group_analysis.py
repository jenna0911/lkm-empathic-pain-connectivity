#!/usr/bin/env python
"""Build a placeholder second-level group design matrix."""

from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from lkm_connectivity.second_level import build_group_design


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("participants_tsv", type=Path)
    parser.add_argument("output_tsv", type=Path)
    args = parser.parse_args()

    participants = pd.read_csv(args.participants_tsv, sep="\t")
    design = build_group_design(participants)
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    design.to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()
