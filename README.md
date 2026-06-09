# Does Loving-Kindness Meditation Modulate Empathy Network Connectivity During Anticipation and Observation of Others' Pain?

This repository contains a public, reproducible scaffold for a task-based functional connectivity reanalysis of OpenNeuro dataset `ds006243`.

The project asks whether Loving-Kindness Meditation (LKM), relative to Progressive Muscle Relaxation (PMR), modulates empathy-related brain network connectivity during two phases of an empathic pain task:

- anticipation of another person's pain or non-painful stimulation
- observation of painful or non-painful stimulation

The original study focused on self-other multi-voxel pattern similarity during pain and fearful anticipation. This reanalysis shifts the emphasis to task-based functional connectivity, with generalized psychophysiological interaction (gPPI) models used to estimate condition-dependent coupling among empathy, salience, affective, and mentalizing regions.

## Research Question

Does LKM training change task-evoked connectivity within empathy-related networks during anticipation and observation of others' pain compared with PMR training?

Planned analyses will test whether LKM is associated with altered condition-specific connectivity between seed regions such as anterior insula, anterior/mid-cingulate cortex, temporoparietal junction, medial prefrontal cortex, and somatosensory regions during anticipation and stimulation periods.

## Data Sources

Primary fMRI data should be downloaded from OpenNeuro dataset `ds006243`, which includes BIDS-organized, fMRIPrep MNI-normalized BOLD data for the empathic pain task.

Behavioral, task-code, and paper-related resources should be obtained from the corresponding OSF and GitHub resources linked by the original dataset or publication.

Raw neuroimaging data, derivatives, and large outputs must not be committed to this repository. Keep data in local ignored directories such as `data/`, `derivatives/`, and `results/`.

See [docs/data_sources.md](docs/data_sources.md) for details.

## Planned Analysis

The analysis will use Python-based neuroimaging tools to:

1. Prepare task events for anticipation and stimulation periods.
2. Extract nuisance confounds from fMRIPrep outputs.
3. Define first-level GLM regressors for task phases and conditions.
4. Estimate seed-based gPPI models.
5. Run second-level group analyses comparing LKM and PMR effects.
6. Export reproducible tables, figures, and statistical maps.

See [docs/analysis_plan.md](docs/analysis_plan.md) for the current analysis plan.

## Repository Layout

```text
.
├── docs/
│   ├── analysis_plan.md
│   └── data_sources.md
├── scripts/
│   ├── 01_prepare_events.py
│   ├── 02_extract_confounds.py
│   ├── 03_make_first_level.py
│   ├── 04_extract_seed_timeseries.py
│   ├── 05_run_gppi.py
│   ├── 06_fit_first_level_gppi.py
│   ├── 07_second_level.py
│   ├── prepare_events.py
│   ├── extract_confounds.py
│   ├── define_first_level_regressors.py
│   ├── run_gppi.py
│   └── second_level_group_analysis.py
├── src/
│   └── lkm_connectivity/
│       ├── __init__.py
│       ├── config.py
│       ├── events.py
│       ├── confounds.py
│       ├── glm.py
│       ├── seeds.py
│       ├── gppi.py
│       ├── firstlevel.py
│       ├── secondlevel.py
│       └── second_level.py
├── environment.yml
├── requirements.txt
└── .gitignore
```

## Setup

Create a conda environment:

```bash
conda env create -f environment.yml
conda activate lkm-connectivity
```

Or install with pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Expected Local Paths

The scripts assume data and outputs are kept outside version control:

```text
data/ds006243/              # OpenNeuro BIDS dataset, not committed
derivatives/fmriprep/       # fMRIPrep derivatives, not committed
derivatives/lkm_connectivity/
results/
```

These paths are intentionally ignored by Git.

## Batch Runner

Use the subject and all-subject batch runners to execute the full gPPI workflow
from event preparation through first-level model fitting:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --dry-run
```

See [docs/running_pipeline.md](docs/running_pipeline.md) for the full
one-subject, all-subject, and OpenNeuro ds006243 smoke-run workflow.

## Prepare Events

After downloading `ds006243` locally, prepare collapsed event regressors for the gPPI workflow:

```bash
python scripts/01_prepare_events.py \
  --bids-root data/ds006243 \
  --output-root derivatives/events
```

The script reads local BIDS `*_events.tsv` files and writes prepared files named `*_desc-gppi_events.tsv`. It creates collapsed regressors for:

- `self_fear_anticipation`
- `self_safety_anticipation`
- `other_fear_anticipation`
- `other_safety_anticipation`
- `self_pain_stimulation`
- `self_nopain_stimulation`
- `other_pain_stimulation`
- `other_nopain_stimulation`
- optional post-stimulation rest regressors such as `post_self_pain_rest`

To skip post-stimulation rest regressors, add `--no-rest`. The script does not download data and does not write raw neuroimaging files.

Run the synthetic event test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_events_synthetic
```

## Extract Confounds

After fMRIPrep derivatives are available locally, select nuisance regressors for first-level GLM and gPPI:

```bash
python scripts/02_extract_confounds.py \
  --fmriprep-dir derivatives/fmriprep \
  --output-root derivatives/confounds
```

For a single run with explicit length validation:

```bash
python scripts/02_extract_confounds.py \
  --confounds-tsv derivatives/fmriprep/sub-001/func/sub-001_task-empathicpain_desc-confounds_timeseries.tsv \
  --output-tsv derivatives/confounds/sub-001/func/sub-001_task-empathicpain_desc-nuisance_regressors.tsv \
  --n-scans 300 \
  --prepared-events derivatives/events/sub-001/func/sub-001_task-empathicpain_desc-gppi_events.tsv \
  --tr 2.0 \
  --on-mismatch warn
```

Selected columns include six motion parameters, framewise displacement when present, cosine regressors, anatomical CompCor regressors, non-steady-state outlier columns, and motion outlier columns. Because ds006243 notes possible trimming differences between confounds and BOLD files, pass `--n-scans` when validating a run. Use `--on-mismatch error` to stop on row-count mismatches.

Run the synthetic confound test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_confounds_synthetic
```

## Make First-Level Design Matrices

Create a first-level GLM design matrix template for one run using prepared gPPI events and selected confounds:

```bash
python scripts/03_make_first_level.py \
  --events-tsv derivatives/events/sub-001/func/sub-001_task-empathicpain_desc-gppi_events.tsv \
  --confounds-tsv derivatives/confounds/sub-001/func/sub-001_task-empathicpain_desc-nuisance_regressors.tsv \
  --output-tsv derivatives/design_matrices/sub-001/func/sub-001_task-empathicpain_desc-design_matrix.tsv \
  --n-scans 300 \
  --tr 2.5
```

This step uses `nilearn.glm.first_level.make_first_level_design_matrix` to create task regressors for anticipation and stimulation conditions, then appends selected confounds as nuisance regressors. Post-stimulation rest regressors are included when present; add `--no-rest` to disallow them. The script validates event timing against `n_scans * TR` and checks that confound rows match `n_scans`.

Run the synthetic first-level test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_glm_synthetic
```

## Extract Seed Time Series

Extract seed-region BOLD time series from a local fMRIPrep MNI-normalized functional image and a local binary ROI mask:

```bash
python scripts/04_extract_seed_timeseries.py \
  --bold-img derivatives/fmriprep/sub-001/func/sub-001_task-empathicpain_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz \
  --mask-img masks/left_anterior_insula_mask.nii.gz \
  --seed-name left_anterior_insula \
  --output-tsv derivatives/seed_timeseries/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_timeseries.tsv \
  --n-scans 300 \
  --design-matrix-tsv derivatives/design_matrices/sub-001/func/sub-001_task-empathicpain_desc-design_matrix.tsv \
  --standardize
```

Supported seed labels are `left_anterior_insula`, `right_anterior_insula`, and `dacc_amcc`. ROI masks must be binary 3D NIfTI images in the same space, shape, and affine as the 4D BOLD image. See [docs/seed_masks.md](docs/seed_masks.md) for mask preparation guidance. This step writes a lightweight TSV and validates the extracted time-series length against `--n-scans` and the design matrix row count when provided. Do not commit BOLD images, ROI NIfTI masks, or generated imaging outputs.

Run the synthetic seed extraction test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_seeds_synthetic
```

## Build gPPI Regressors

Create a gPPI design matrix from a first-level design matrix and one seed time series:

```bash
python scripts/05_run_gppi.py \
  --design-matrix-tsv derivatives/design_matrices/sub-001/func/sub-001_task-empathicpain_desc-design_matrix.tsv \
  --seed-timeseries-tsv derivatives/seed_timeseries/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_timeseries.tsv \
  --output-tsv derivatives/gppi/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_desc-gppi_design.tsv \
  --contrasts-json derivatives/gppi/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_desc-gppi_contrasts.json
```

The script mean-centers the seed time series by default and creates interaction columns named `gppi_<task_condition>` for each anticipation and stimulation task regressor. Use `--no-center-seed` only for sensitivity checks. Main contrast definitions are written as JSON and include:

- `Other Fear Anticipation > Other Safety Anticipation`
- `Other Pain Stimulation > Other No-Pain Stimulation`
- `(Other Fear Anticipation > Other Safety Anticipation) - (Self Fear Anticipation > Self Safety Anticipation)`
- `(Other Pain Stimulation > Other No-Pain Stimulation) - (Self Pain Stimulation > Self No-Pain Stimulation)`

This step writes tabular design/contrast files only and does not fit a voxelwise fMRI model.

Run the synthetic gPPI test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_gppi_synthetic
```

## Fit First-Level gPPI Models

Fit first-level gPPI contrasts for one run using a local preprocessed BOLD image, a gPPI design matrix, and contrast definitions:

```bash
python scripts/06_fit_first_level_gppi.py \
  --bold-img derivatives/fmriprep/sub-001/func/sub-001_task-empathicpain_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz \
  --design-matrix-tsv derivatives/gppi/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_desc-gppi_design.tsv \
  --contrasts-json derivatives/gppi/sub-001/func/sub-001_task-empathicpain_seed-left_anterior_insula_desc-gppi_contrasts.json \
  --output-dir derivatives/firstlevel/sub-001/func/seed-left_anterior_insula \
  --tr 2.5
```

This step uses `nilearn.glm.first_level.FirstLevelModel`, validates that BOLD volumes match design matrix rows, and writes z maps plus effect-size maps for:

- `other_fear_anticipation_vs_safety`
- `other_pain_stimulation_vs_nopain`
- `other_specific_fear_anticipation`
- `other_specific_pain_stimulation`

The script does not download data. The generated NIfTI maps belong in ignored derivatives/results directories and should not be committed.

Run the synthetic first-level fitting test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_firstlevel_synthetic
```

## Run Second-Level Group Analyses

Run group-level analyses for one first-level gPPI contrast and seed:

```bash
python scripts/07_second_level.py \
  --participants-tsv derivatives/metadata/participants_groups.tsv \
  --maps-tsv derivatives/metadata/firstlevel_gppi_maps.tsv \
  --contrast-name other_pain_stimulation_vs_nopain \
  --seed-name left_anterior_insula \
  --output-dir derivatives/secondlevel/seed-left_anterior_insula/other_pain_stimulation_vs_nopain
```

The participants TSV must contain:

```text
subject_id	group
sub-001	LKM
sub-002	PMR
```

The maps TSV must contain one row per subject, contrast, and seed:

```text
subject_id	contrast_name	seed_name	map_path
sub-001	other_pain_stimulation_vs_nopain	left_anterior_insula	derivatives/firstlevel/sub-001/.../other_pain_stimulation_vs_nopain_zmap.nii.gz
```

This step validates that every subject has exactly one matching first-level map, writes a second-level design matrix TSV, and outputs group z maps for:

- one-sample test across all participants
- `LKM > PMR`
- `PMR > LKM`

Generated group NIfTI maps belong in ignored derivatives/results directories and should not be committed.

Run the synthetic second-level test/example with:

```bash
PYTHONPATH=src python -m unittest tests.test_secondlevel_synthetic
```

## Status

This repository currently provides the initial public project structure and placeholder analysis scripts. The dataset is not included and should be downloaded separately by each analyst.

## License

Code in this repository is released under the MIT License. Dataset use is governed by the license and terms associated with OpenNeuro `ds006243` and related project resources.
