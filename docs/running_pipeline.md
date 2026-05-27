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
