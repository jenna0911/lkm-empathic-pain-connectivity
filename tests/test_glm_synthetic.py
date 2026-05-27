"""Synthetic tests for first-level GLM design matrix construction."""

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from lkm_connectivity.glm import (
    DEFAULT_TR,
    build_first_level_design_matrix,
    make_first_level_from_files,
    make_synthetic_first_level_inputs,
)


class FirstLevelDesignTests(unittest.TestCase):
    def test_builds_design_with_task_and_confound_columns(self) -> None:
        events, confounds = make_synthetic_first_level_inputs(n_scans=40, tr=DEFAULT_TR)

        design = build_first_level_design_matrix(
            events=events,
            confounds=confounds,
            n_scans=40,
            tr=DEFAULT_TR,
        )

        self.assertEqual(len(design), 40)
        self.assertIn("self_fear_anticipation", design.columns)
        self.assertIn("other_nopain_stimulation", design.columns)
        self.assertIn("post_self_pain_rest", design.columns)
        self.assertIn("trans_x", design.columns)
        self.assertIn("a_comp_cor_00", design.columns)

    def test_rejects_events_beyond_run_duration(self) -> None:
        events, confounds = make_synthetic_first_level_inputs(n_scans=40, tr=DEFAULT_TR)
        events.loc[0, "onset"] = 500.0

        with self.assertRaisesRegex(ValueError, "beyond the modeled run duration"):
            build_first_level_design_matrix(
                events=events,
                confounds=confounds,
                n_scans=40,
                tr=DEFAULT_TR,
            )

    def test_rejects_mismatched_confound_rows(self) -> None:
        events, confounds = make_synthetic_first_level_inputs(n_scans=40, tr=DEFAULT_TR)

        with self.assertRaisesRegex(ValueError, "Confound rows"):
            build_first_level_design_matrix(
                events=events,
                confounds=confounds.iloc[:-1],
                n_scans=40,
                tr=DEFAULT_TR,
            )

    def test_missing_task_conditions_are_zero_filled(self) -> None:
        events, confounds = make_synthetic_first_level_inputs(n_scans=40, tr=DEFAULT_TR)
        events = events.loc[events["trial_type"] != "other_safety_anticipation"].copy()

        design = build_first_level_design_matrix(
            events=events,
            confounds=confounds,
            n_scans=40,
            tr=DEFAULT_TR,
        )

        self.assertIn("other_safety_anticipation", design.columns)
        self.assertEqual(float(design["other_safety_anticipation"].sum()), 0.0)

    def test_writes_design_matrix_from_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            events, confounds = make_synthetic_first_level_inputs(n_scans=40, tr=DEFAULT_TR)
            events_tsv = root / "events.tsv"
            confounds_tsv = root / "confounds.tsv"
            output_tsv = root / "design.tsv"
            events.to_csv(events_tsv, sep="\t", index=False)
            confounds.to_csv(confounds_tsv, sep="\t", index=False)

            result = make_first_level_from_files(
                events_tsv=events_tsv,
                confounds_tsv=confounds_tsv,
                output_tsv=output_tsv,
                n_scans=40,
                tr=DEFAULT_TR,
            )
            written = pd.read_csv(output_tsv, sep="\t")

            self.assertTrue(output_tsv.exists())
            self.assertEqual(result.n_scans, 40)
            self.assertEqual(len(written), 40)
            self.assertIn("frame_time", written.columns)


if __name__ == "__main__":
    unittest.main()
