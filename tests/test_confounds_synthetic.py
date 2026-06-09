"""Synthetic tests for fMRIPrep confound selection."""

from pathlib import Path
import tempfile
import unittest
import warnings

import pandas as pd

from lkm_connectivity.confounds import (
    MOTION_PARAMETERS,
    extract_confounds,
    extract_confounds_file,
    load_confounds,
    make_synthetic_confounds,
    select_confounds,
)


class ConfoundSelectionTests(unittest.TestCase):
    def test_selects_expected_fmriprep_columns(self) -> None:
        confounds = make_synthetic_confounds(n_scans=5)
        selected = select_confounds(confounds)

        for column in MOTION_PARAMETERS:
            self.assertIn(column, selected.columns)
        self.assertIn("framewise_displacement", selected.columns)
        self.assertIn("cosine00", selected.columns)
        self.assertIn("a_comp_cor_00", selected.columns)
        self.assertIn("non_steady_state_outlier00", selected.columns)
        self.assertIn("motion_outlier00", selected.columns)
        self.assertNotIn("unused_signal", selected.columns)
        self.assertFalse(selected.isna().any().any())

    def test_length_mismatch_can_raise_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "confounds_timeseries.tsv"
            make_synthetic_confounds(n_scans=4).to_csv(source, sep="\t", index=False)

            with self.assertRaisesRegex(ValueError, "confounds rows"):
                extract_confounds(source, n_scans=5, on_mismatch="error")

    def test_length_mismatch_can_warn(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with tempfile.TemporaryDirectory() as tmpdir:
                source = Path(tmpdir) / "confounds_timeseries.tsv"
                make_synthetic_confounds(n_scans=4).to_csv(source, sep="\t", index=False)

                extract_confounds(source, n_scans=5, on_mismatch="warn")

        self.assertTrue(any("confounds rows" in str(item.message) for item in caught))

    def test_extract_confounds_file_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "sub-001_task-pain_desc-confounds_timeseries.tsv"
            output = root / "derivatives" / "confounds" / "sub-001_task-pain_desc-nuisance_regressors.tsv"
            make_synthetic_confounds(n_scans=5).to_csv(source, sep="\t", index=False)

            result = extract_confounds_file(source, output, n_scans=5, on_mismatch="error")
            written = pd.read_csv(output, sep="\t")

            self.assertEqual(result.n_output_rows, 5)
            self.assertEqual(len(written), 5)
            self.assertIn("a_comp_cor_00", written.columns)

    def test_loads_headerless_numeric_confounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "sub-001_task-empathy_run-01_confounds.txt"
            source.write_text("1\t2\t3\n4\t5\t6\n", encoding="utf-8")

            confounds = load_confounds(source)
            selected = select_confounds(confounds)

            self.assertEqual(len(confounds), 2)
            self.assertEqual(list(confounds.columns), ["custom_confound_00", "custom_confound_01", "custom_confound_02"])
            self.assertEqual(list(selected.columns), list(confounds.columns))


if __name__ == "__main__":
    unittest.main()
