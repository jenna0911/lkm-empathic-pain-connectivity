"""Synthetic tests for seed time-series extraction."""

from pathlib import Path
import tempfile
import unittest

import nibabel as nib
import numpy as np
import pandas as pd

from lkm_connectivity.seeds import (
    extract_mean_seed_timeseries,
    extract_seed_to_file,
    load_binary_mask,
    make_synthetic_bold_and_masks,
    standardize_timeseries,
    validate_seed_length,
)


class SeedExtractionTests(unittest.TestCase):
    def test_extracts_mean_seed_timeseries(self) -> None:
        bold, masks = make_synthetic_bold_and_masks(n_scans=6)

        series = extract_mean_seed_timeseries(bold, masks["left_anterior_insula"])

        self.assertEqual(len(series), 6)
        np.testing.assert_allclose(series.to_numpy(), np.arange(6, dtype=float) + 10.0)

    def test_standardizes_seed_timeseries(self) -> None:
        bold, masks = make_synthetic_bold_and_masks(n_scans=6)

        series = extract_mean_seed_timeseries(bold, masks["right_anterior_insula"], standardize=True)

        self.assertAlmostEqual(float(series.mean()), 0.0, places=7)
        self.assertAlmostEqual(float(series.std(ddof=1)), 1.0, places=7)

    def test_rejects_nonbinary_mask(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mask_data = np.zeros((3, 3, 3), dtype=float)
            mask_data[0, 0, 0] = 2.0
            mask_path = Path(tmpdir) / "mask.nii.gz"
            nib.save(nib.Nifti1Image(mask_data, np.eye(4)), mask_path)

            with self.assertRaisesRegex(ValueError, "binary"):
                load_binary_mask(mask_path)

    def test_validates_seed_length_against_design(self) -> None:
        design = pd.DataFrame({"constant": np.ones(5)})

        with self.assertRaisesRegex(ValueError, "design matrix rows"):
            validate_seed_length(np.arange(4), n_scans=4, design_matrix=design)

    def test_extract_seed_to_file_uses_synthetic_nifti_only_in_tempdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bold, masks = make_synthetic_bold_and_masks(n_scans=6)
            bold_path = root / "bold.nii.gz"
            mask_path = root / "left_ai_mask.nii.gz"
            design_path = root / "design.tsv"
            output_path = root / "seed.tsv"
            nib.save(bold, bold_path)
            nib.save(masks["left_anterior_insula"], mask_path)
            pd.DataFrame({"constant": np.ones(6)}).to_csv(design_path, sep="\t", index=False)

            result = extract_seed_to_file(
                bold_img=bold_path,
                mask_img=mask_path,
                output_tsv=output_path,
                seed_name="left_anterior_insula",
                n_scans=6,
                design_matrix_tsv=design_path,
                standardize=False,
            )
            written = pd.read_csv(output_path, sep="\t")

            self.assertEqual(result.n_scans, 6)
            self.assertEqual(list(written.columns), ["left_anterior_insula"])
            np.testing.assert_allclose(written["left_anterior_insula"].to_numpy(), np.arange(6) + 10.0)

    def test_constant_standardization_returns_zeros(self) -> None:
        standardized = standardize_timeseries(np.ones(4))

        np.testing.assert_allclose(standardized, np.zeros(4))


if __name__ == "__main__":
    unittest.main()
