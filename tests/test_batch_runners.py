"""Mocked tests for batch pipeline runners."""

from pathlib import Path
import tempfile
import unittest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_all_subjects import discover_participants
from run_subject_pipeline import (
    PipelineOptions,
    discover_seed_masks,
    discover_subject_runs,
    normalize_participant_label,
    should_run,
)


class BatchRunnerTests(unittest.TestCase):
    def test_normalizes_participant_label(self) -> None:
        self.assertEqual(normalize_participant_label("001"), "sub-001")
        self.assertEqual(normalize_participant_label("sub-001"), "sub-001")

    def test_should_run_respects_outputs_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "done.tsv"
            self.assertTrue(should_run([output], overwrite=False))
            output.write_text("ok\n", encoding="utf-8")
            self.assertFalse(should_run([output], overwrite=False))
            self.assertTrue(should_run([output], overwrite=True))

    def test_discovers_subject_run_paths_without_loading_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bids_func = root / "bids" / "sub-001" / "func"
            fmriprep_func = root / "fmriprep" / "sub-001" / "func"
            bids_func.mkdir(parents=True)
            fmriprep_func.mkdir(parents=True)
            (bids_func / "sub-001_task-empathicpain_run-1_events.tsv").write_text("onset\tduration\ttrial_type\n", encoding="utf-8")
            (fmriprep_func / "sub-001_task-empathicpain_run-1_desc-confounds_timeseries.tsv").write_text(
                "trans_x\n",
                encoding="utf-8",
            )
            (fmriprep_func / "sub-001_task-empathicpain_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz").write_text(
                "placeholder\n",
                encoding="utf-8",
            )
            options = PipelineOptions(
                bids_root=root / "bids",
                fmriprep_root=root / "fmriprep",
                output_root=root / "out",
                seed_mask_dir=root / "masks",
                dry_run=True,
            )

            runs = discover_subject_runs(options, "001")

            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0].run_prefix, "sub-001_task-empathicpain_run-1")
            self.assertTrue(str(runs[0].prepared_events_tsv).endswith("_desc-gppi_events.tsv"))

    def test_discovers_seed_masks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mask_dir = Path(tmpdir)
            (mask_dir / "left_anterior_insula_mask.nii.gz").write_text("placeholder\n", encoding="utf-8")

            masks = discover_seed_masks(mask_dir)

            self.assertEqual(masks["left_anterior_insula"], mask_dir / "left_anterior_insula_mask.nii.gz")

    def test_discovers_all_participants(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "sub-002").mkdir()
            (root / "sub-001").mkdir()

            self.assertEqual(discover_participants(root), ["sub-001", "sub-002"])


if __name__ == "__main__":
    unittest.main()
