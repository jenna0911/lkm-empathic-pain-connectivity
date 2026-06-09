"""Synthetic tests for event preparation."""

from pathlib import Path
import tempfile
import unittest

from lkm_connectivity.events import (
    ALL_REGRESSORS,
    collapse_events_for_gppi,
    load_ds006243_timing_events,
    make_synthetic_events,
    prepare_bids_events,
)


class EventPreparationTests(unittest.TestCase):
    def test_synthetic_events_map_to_expected_regressors(self) -> None:
        events = make_synthetic_events()
        prepared = collapse_events_for_gppi(events)

        self.assertEqual(len(prepared), len(events))
        self.assertEqual(set(prepared["trial_type"]), set(events["trial_type"]))
        self.assertTrue(set(prepared["trial_type"]).issubset(ALL_REGRESSORS))

    def test_rest_regressors_can_be_excluded(self) -> None:
        events = make_synthetic_events()
        prepared = collapse_events_for_gppi(events, include_rest=False)

        self.assertNotIn("post_self_pain_rest", set(prepared["trial_type"]))
        self.assertNotIn("post_other_nopain_rest", set(prepared["trial_type"]))

    def test_prepare_bids_events_writes_derivative_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bids_root = Path(tmpdir)
            func_dir = bids_root / "sub-001" / "func"
            func_dir.mkdir(parents=True)
            source = func_dir / "sub-001_task-empathicpain_events.tsv"
            make_synthetic_events().to_csv(source, sep="\t", index=False)

            results = prepare_bids_events(bids_root)

            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].output.exists())
            self.assertEqual(
                results[0].output.relative_to(bids_root).as_posix(),
                "derivatives/events/sub-001/func/sub-001_task-empathicpain_desc-gppi_events.tsv",
            )

    def test_loads_ds006243_timing_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            regressor_dir = Path(tmpdir)
            (regressor_dir / "sub-001_task-empathy_timing-otherpainanticipation.txt").write_text(
                "1.0:2\t5.0:3\n",
                encoding="utf-8",
            )
            (regressor_dir / "sub-001_task-empathy_timing-selfnopainrest.txt").write_text(
                "9.0:4\n",
                encoding="utf-8",
            )

            events = load_ds006243_timing_events(regressor_dir)

            self.assertEqual(len(events), 3)
            self.assertIn("other_fear_anticipation", set(events["trial_type"]))
            self.assertIn("post_self_nopain_rest", set(events["trial_type"]))


if __name__ == "__main__":
    unittest.main()
