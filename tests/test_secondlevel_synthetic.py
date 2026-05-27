"""Synthetic tests for second-level group analysis."""

from pathlib import Path
import tempfile
import unittest

import nibabel as nib
import pandas as pd

from lkm_connectivity.secondlevel import (
    build_second_level_design_matrix,
    make_synthetic_secondlevel_inputs,
    prepare_second_level_inputs,
    run_second_level_from_files,
)


class SecondLevelAnalysisTests(unittest.TestCase):
    def test_builds_group_design_matrix(self) -> None:
        metadata = pd.DataFrame(
            {
                "subject_id": ["sub-01", "sub-02"],
                "group": ["LKM", "PMR"],
            }
        )
        design = build_second_level_design_matrix(metadata)

        self.assertEqual(list(design.columns), ["subject_id", "group", "intercept", "group_lkm"])
        self.assertEqual(design["group_lkm"].tolist(), [1.0, 0.0])

    def test_rejects_missing_subject_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            participants_tsv, maps_tsv, _mask = make_synthetic_secondlevel_inputs(root, n_per_group=2)
            participants = pd.read_csv(participants_tsv, sep="\t")
            maps = pd.read_csv(maps_tsv, sep="\t").iloc[:-1].copy()

            with self.assertRaisesRegex(ValueError, "Missing contrast maps"):
                prepare_second_level_inputs(
                    participants=participants,
                    maps=maps,
                    contrast_name="other_pain_stimulation_vs_nopain",
                    seed_name="left_anterior_insula",
                )

    def test_rejects_duplicate_subject_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            participants_tsv, maps_tsv, _mask = make_synthetic_secondlevel_inputs(root, n_per_group=2)
            participants = pd.read_csv(participants_tsv, sep="\t")
            maps = pd.read_csv(maps_tsv, sep="\t")
            maps = pd.concat([maps, maps.iloc[[0]]], ignore_index=True)

            with self.assertRaisesRegex(ValueError, "more than one"):
                prepare_second_level_inputs(
                    participants=participants,
                    maps=maps,
                    contrast_name="other_pain_stimulation_vs_nopain",
                    seed_name="left_anterior_insula",
                )

    def test_runs_second_level_and_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            participants_tsv, maps_tsv, mask_path = make_synthetic_secondlevel_inputs(root / "inputs", n_per_group=3)
            output_dir = root / "secondlevel"

            result = run_second_level_from_files(
                participants_tsv=participants_tsv,
                maps_tsv=maps_tsv,
                contrast_name="other_pain_stimulation_vs_nopain",
                seed_name="left_anterior_insula",
                output_dir=output_dir,
                mask_img=mask_path,
            )

            self.assertEqual(result.n_subjects, 6)
            self.assertTrue(result.design_matrix_tsv.exists())
            self.assertEqual(set(result.z_maps), {"one_sample", "lkm_gt_pmr", "pmr_gt_lkm"})
            for path in result.z_maps.values():
                self.assertTrue(path.exists())
                self.assertEqual(nib.load(path).shape, (5, 5, 5))


if __name__ == "__main__":
    unittest.main()
