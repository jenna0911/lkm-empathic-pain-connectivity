#!/usr/bin/env python
"""Fit first-level gPPI contrasts with Nilearn.

This script reads a local preprocessed BOLD image, a gPPI design matrix TSV, and
contrast definitions JSON. It writes z maps and effect-size maps as NIfTI files.
It does not download data.
"""

from argparse import ArgumentParser
from pathlib import Path

from lkm_connectivity.firstlevel import DEFAULT_TR, fit_first_level_gppi_from_files


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--bold-img", type=Path, required=True, help="Local preprocessed 4D BOLD image.")
    parser.add_argument("--design-matrix-tsv", type=Path, required=True, help="gPPI design matrix TSV.")
    parser.add_argument("--contrasts-json", type=Path, required=True, help="gPPI contrast definitions JSON.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for z/effect NIfTI maps.")
    parser.add_argument("--tr", type=float, default=DEFAULT_TR, help="Repetition time in seconds. Default: 2.5")
    parser.add_argument("--mask-img", type=Path, default=None, help="Optional brain mask image.")
    parser.add_argument("--smoothing-fwhm", type=float, default=None, help="Optional smoothing FWHM in mm.")
    args = parser.parse_args()

    result = fit_first_level_gppi_from_files(
        bold_img=args.bold_img,
        design_matrix_tsv=args.design_matrix_tsv,
        contrasts_json=args.contrasts_json,
        output_dir=args.output_dir,
        tr=args.tr,
        mask_img=args.mask_img,
        smoothing_fwhm=args.smoothing_fwhm,
    )
    print(
        f"Fit {len(result.z_maps)} contrasts for {result.n_scans} scans. "
        f"Maps written to {result.output_dir}"
    )


if __name__ == "__main__":
    main()
