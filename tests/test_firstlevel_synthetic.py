"""Synthetic tests for first-level gPPI fitting."""

from pathlib import Path
import json
import tempfile
import unittest

import nibabel as nib
import pandas as pd

from lkm_connectivity.firstlevel import (
    MAIN_CONTRAST_NAMES,
    fit_first_level_gppi_from_files,
    load_contrast_definitions,
    load_gppi_design_matrix,
    make_synthetic_firstlevel_inputs,
    validate_bold_design_rows,
)


class FirstLevelGppiFitTests(unittest.TestCase):
    def test_validates_bold_design_row_mismatch(self) -> None:
        bold, _mask, design, _contrasts = make_synthetic_firstlevel_inputs(n_scans=12)

        with self.assertRaisesRegex(ValueError, "BOLD n_scans"):
            validate_bold_design_rows(bold, design.iloc[:-1])

    def test_loads_required_contrast_aliases(self) -> None:
        _bold, _mask, design, contrasts = make_synthetic_firstlevel_inputs(n_scans=12)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "contrasts.json"
            path.write_text(json.dumps(contrasts), encoding="utf-8")
            loaded = load_contrast_definitions(path, list(design.columns))

        self.assertEqual(set(loaded), set(MAIN_CONTRAST_NAMES))
        for vector in loaded.values():
            self.assertEqual(len(vector), len(design.columns))

    def test_fits_model_and_writes_maps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bold, mask, design, contrasts = make_synthetic_firstlevel_inputs(n_scans=24)
            bold_path = root / "bold.nii.gz"
            mask_path = root / "mask.nii.gz"
            design_path = root / "gppi_design.tsv"
            contrasts_path = root / "contrasts.json"
            output_dir = root / "firstlevel"
            nib.save(bold, bold_path)
            nib.save(mask, mask_path)
            design.to_csv(design_path, sep="\t", index=False)
            contrasts_path.write_text(json.dumps(contrasts), encoding="utf-8")

            result = fit_first_level_gppi_from_files(
                bold_img=bold_path,
                design_matrix_tsv=design_path,
                contrasts_json=contrasts_path,
                output_dir=output_dir,
                mask_img=mask_path,
            )

            self.assertEqual(result.n_scans, 24)
            self.assertEqual(set(result.z_maps), set(MAIN_CONTRAST_NAMES))
            for path in result.z_maps.values():
                self.assertTrue(path.exists())
                self.assertEqual(nib.load(path).shape, bold.shape[:3])
            for path in result.effect_maps.values():
                self.assertTrue(path.exists())
                self.assertEqual(nib.load(path).shape, bold.shape[:3])

    def test_frame_time_column_is_not_modeled_as_regressor(self) -> None:
        _bold, _mask, design, _contrasts = make_synthetic_firstlevel_inputs(n_scans=12)
        design.insert(0, "frame_time", [index * 2.5 for index in range(len(design))])

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "design.tsv"
            design.to_csv(path, sep="\t", index=False)
            loaded = load_gppi_design_matrix(path)

        self.assertNotIn("frame_time", loaded.columns)


if __name__ == "__main__":
    unittest.main()
