# Analysis Scripts

The numbered scripts are the canonical command-line entry points for each
analysis stage:

| Step | Script | Purpose |
| --- | --- | --- |
| 1 | `01_prepare_events.py` | Collapse task events into analysis conditions. |
| 2 | `02_extract_confounds.py` | Select and validate fMRIPrep nuisance regressors. |
| 3 | `03_make_first_level.py` | Build the first-level design matrix. |
| 4 | `04_extract_seed_timeseries.py` | Extract seed-region BOLD time series. |
| 5 | `05_run_gppi.py` | Build gPPI regressors and contrast definitions. |
| 6 | `06_fit_first_level_gppi.py` | Fit first-level gPPI models and write contrast maps. |
| 7 | `07_second_level.py` | Run second-level LKM-versus-PMR analyses. |

For end-to-end execution:

- `run_subject_pipeline.py` runs steps 1-6 for one participant.
- `run_all_subjects.py` applies the subject pipeline across participants.

Legacy unnumbered wrappers were removed to keep one documented entry point per
analysis stage. Reusable implementation code remains under
`src/lkm_connectivity/`.
