"""Synthetic tests for gPPI design construction."""

from pathlib import Path
import json
import tempfile
import unittest

import numpy as np
import pandas as pd

from lkm_connectivity.gppi import (
    GPPI_PREFIX,
    MAIN_GPPI_CONTRASTS,
    TASK_CONDITIONS,
    build_contrast_definitions,
    build_gppi_design_matrix,
    build_gppi_interactions,
    make_gppi_from_files,
    make_synthetic_gppi_inputs,
)


class GppiConstructionTests(unittest.TestCase):
    def test_builds_seed_by_task_interactions(self) -> None:
        design, seed = make_synthetic_gppi_inputs(n_scans=8)
        interactions = build_gppi_interactions(design.loc[:, list(TASK_CONDITIONS)], seed.iloc[:, 0])

        self.assertEqual(len(interactions), 8)
        self.assertIn("gppi_other_fear_anticipation", interactions.columns)
        expected = design["other_fear_anticipation"].to_numpy() * (
            seed.iloc[:, 0].to_numpy() - seed.iloc[:, 0].mean()
        )
        np.testing.assert_allclose(interactions["gppi_other_fear_anticipation"], expected)

    def test_builds_full_gppi_design_and_contrasts(self) -> None:
        design, seed = make_synthetic_gppi_inputs(n_scans=8)
        gppi_design = build_gppi_design_matrix(design, seed)
        contrasts = build_contrast_definitions(gppi_design)

        self.assertEqual(len(gppi_design), 8)
        self.assertIn("seed_timeseries", gppi_design.columns)
        for condition in TASK_CONDITIONS:
            self.assertIn(f"{GPPI_PREFIX}{condition}", gppi_design.columns)
        self.assertEqual(set(contrasts), set(MAIN_GPPI_CONTRASTS))
        vector = contrasts["other_vs_self_pain_stimulation"]["vector"]
        self.assertEqual(len(vector), len(gppi_design.columns))

    def test_rejects_row_count_mismatch(self) -> None:
        design, seed = make_synthetic_gppi_inputs(n_scans=8)

        with self.assertRaisesRegex(ValueError, "rows"):
            build_gppi_design_matrix(design, seed.iloc[:-1])

    def test_rejects_missing_task_columns(self) -> None:
        design, seed = make_synthetic_gppi_inputs(n_scans=8)

        with self.assertRaisesRegex(ValueError, "missing task condition"):
            build_gppi_design_matrix(design.drop(columns=["other_fear_anticipation"]), seed)

    def test_writes_gppi_design_and_contrasts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            design, seed = make_synthetic_gppi_inputs(n_scans=8)
            design_tsv = root / "design.tsv"
            seed_tsv = root / "seed.tsv"
            output_tsv = root / "gppi_design.tsv"
            contrasts_json = root / "contrasts.json"
            design.to_csv(design_tsv, sep="\t", index=False)
            seed.to_csv(seed_tsv, sep="\t", index=False)

            result = make_gppi_from_files(
                design_matrix_tsv=design_tsv,
                seed_timeseries_tsv=seed_tsv,
                output_tsv=output_tsv,
                contrasts_json=contrasts_json,
            )
            written_design = pd.read_csv(output_tsv, sep="\t")
            written_contrasts = json.loads(contrasts_json.read_text(encoding="utf-8"))

            self.assertEqual(result.n_rows, 8)
            self.assertTrue(output_tsv.exists())
            self.assertTrue(contrasts_json.exists())
            self.assertIn("gppi_self_fear_anticipation", written_design.columns)
            self.assertIn("other_fear_anticipation_gt_other_safety_anticipation", written_contrasts)


if __name__ == "__main__":
    unittest.main()
