# Reproducibility Guide

This repository separates public code and summary results from locally stored
neuroimaging data. It never downloads data automatically.

## Clone the Repository

```bash
git clone https://github.com/jenna0911/lkm-empathic-pain-connectivity.git
cd lkm-empathic-pain-connectivity
```

## Create the Environment

With Conda:

```bash
conda env create -f environment.yml
conda activate lkm-connectivity
```

Alternatively, install the Python dependencies in an isolated environment:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run Synthetic Tests

The tests use generated tables and synthetic NIfTI images rather than real
participant data.

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Dry-Run One Participant

After separately obtaining the approved dataset files and preparing ROI masks:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --dry-run
```

Dry-run reports the discovered runs, masks, and planned outputs without fitting
the participant model. See [running_pipeline.md](running_pipeline.md) for the
full workflow and [seed_masks.md](seed_masks.md) for mask preparation.

## Folders That Must Remain Local

The following locations are intentionally excluded from Git:

```text
data/
rawdata/
sourcedata/
derivatives/
outputs/
figures/
masks/
```

Neuroimaging formats including NIfTI, GIFTI, and CIFTI are also ignored. This
prevents accidental publication of large BOLD images, ROI masks,
participant-level contrast maps, confounds, and generated derivatives.

## Why Imaging Data Are Excluded

OpenNeuro `ds006243` should be downloaded from its authoritative source under
its own terms. Re-hosting raw or preprocessed images in Git would duplicate
large files, weaken provenance, and increase the chance of accidentally
publishing participant-level derivatives. The repository instead records data
sources, processing decisions, runnable code, and synthetic validation.

## Public-Safe Result Summaries

The `results/` package was derived locally from the completed group analysis.
Only aggregate statistics and PNG figures without participant labels were
selected for publication. It excludes subject identifiers, participant-level
effect tables, BOLD time series, masks, maps, confounds, and large derivatives.

The public tables report the model, interaction estimate, uncertainty, sample
size, and exploratory label needed to audit the README claims. See
[results/README.md](../results/README.md) for file-level details.
