#!/usr/bin/env python
"""Run the ds006243 gPPI pipeline for all discovered or requested subjects."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from run_subject_pipeline import PipelineOptions, run_subject_pipeline
from lkm_connectivity.glm import DEFAULT_TR


def discover_participants(bids_root: Path) -> list[str]:
    """Return sorted BIDS participant labels from a BIDS root."""

    participants = sorted(path.name for path in bids_root.glob("sub-*") if path.is_dir())
    if not participants:
        raise FileNotFoundError(f"No sub-* directories found under {bids_root}")
    return participants


def main() -> None:
    """CLI entry point."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--bids-root", type=Path, required=True)
    parser.add_argument("--fmriprep-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--participant-label", action="append", default=None)
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
    participants = args.participant_label or discover_participants(args.bids_root)
    print(f"[batch] {len(participants)} participant(s)")
    for participant_label in participants:
        run_subject_pipeline(options, participant_label)


if __name__ == "__main__":
    main()
