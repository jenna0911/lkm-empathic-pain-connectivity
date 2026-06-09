# Running the ds006243 gPPI Pipeline

This repository does not download or store OpenNeuro data. Keep BIDS data,
fMRIPrep derivatives, ROI masks, and generated outputs outside Git-tracked
paths or under ignored directories.

## Required Inputs

The batch runners expect:

- `--bids-root`: local ds006243 BIDS dataset containing `sub-*/func/*_events.tsv`
- `--fmriprep-root`: local fMRIPrep derivatives containing preprocessed BOLD and confounds
- `--output-root`: ignored output directory for pipeline derivatives
- `--participant-label`: participant label, with or without `sub-`
- `--seed-mask-dir`: directory containing binary masks for supported seeds

The OpenNeuro `ds006243` release is a derivative dataset. In that layout, the
runner can also read timing and confound files from:

```text
data/ds006243/events/sub-001/regressors/*_timing-*.txt
data/ds006243/events/sub-001/regressors/*_run-*_confounds.txt
data/ds006243/sub-001/func/*_acq-MNI152NLin2009cAsym_rec-preproc_run-*_bold.nii.gz
```

Timing files are converted from `onset:duration` entries into the collapsed
gPPI regressors. Headerless numeric confound matrices are kept as
`custom_confound_00`, `custom_confound_01`, and so on.

Supported seed mask filenames:

```text
left_anterior_insula.nii.gz
left_anterior_insula_mask.nii.gz
right_anterior_insula.nii.gz
right_anterior_insula_mask.nii.gz
dacc_amcc.nii.gz
dacc_amcc_mask.nii.gz
```

## One Subject

Preview commands and outputs without running models:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --dry-run
```

Run the pipeline:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --participant-label sub-001 \
  --seed-mask-dir masks
```

Completed outputs are skipped by default. Add `--overwrite` to regenerate them.

## OpenNeuro ds006243 Smoke Run

Install the environment and editable package:

```bash
conda env create -f environment.yml
conda activate lkm-connectivity
python -m pip install --no-build-isolation -e .
python -m pip install git-annex
```

Clone the OpenNeuro dataset metadata and retrieve only the files needed for one
participant:

```bash
git clone https://github.com/OpenNeuroDatasets/ds006243.git data/ds006243
datalad get data/ds006243/events/sub-001/regressors
datalad get data/ds006243/sub-001/func/sub-001_task-empathy_acq-MNI152NLin2009cAsym_rec-preproc_run-01_bold.nii.gz
datalad get data/ds006243/sub-001/func/sub-001_task-empathy_acq-MNI152NLin2009cAsym_rec-preproc_run-02_bold.nii.gz
```

For sub-001, the downloaded BOLD runs have 296 volumes while the provided
confound matrices have 290 rows. For a local smoke test, create a gitignored
trimmed BOLD copy with 290 volumes and point `--fmriprep-root` to that local
shim. Keep the original OpenNeuro files unchanged and document the trimming
choice before using the outputs for inference.

Example dry-run:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root outputs/smoke/fmriprep \
  --output-root outputs/smoke/derivatives \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --dry-run
```

Example one-subject smoke run:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root outputs/smoke/fmriprep \
  --output-root outputs/smoke/derivatives \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --overwrite
```

## All Subjects

Discover all `sub-*` folders under the BIDS root:

```bash
python scripts/run_all_subjects.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --seed-mask-dir masks \
  --dry-run
```

Limit the batch to selected participants:

```bash
python scripts/run_all_subjects.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --seed-mask-dir masks \
  --participant-label sub-001 \
  --participant-label sub-002
```

## Pipeline Steps

For each subject/run and seed, the runner performs:

1. Prepare gPPI events.
2. Extract selected fMRIPrep confounds.
3. Build the first-level design matrix.
4. Extract seed time series.
5. Build the gPPI design matrix and contrast JSON.
6. Fit first-level gPPI contrasts.

## Data Safety

Do not commit:

- raw BIDS or OpenNeuro data
- fMRIPrep derivatives
- NIfTI, GIFTI, or CIFTI files
- `derivatives/`, `results/`, or large generated outputs

Use `--dry-run` before a full run to verify the planned inputs and outputs.
