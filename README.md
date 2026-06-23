# Brain Connectivity During Observed Fear Anticipation and Loneliness Reduction After Meditation Training

This repository contains a public, reproducible gPPI reanalysis pipeline for
OpenNeuro `ds006243`, an fMRI empathic-pain task dataset collected after
loving-kindness meditation (LKM) or progressive muscle relaxation (PMR)
training.

The central question is:

> After training, is reduced loneliness associated with task-dependent brain
> connectivity while participants anticipate or observe another person's pain?

The project focuses on individual differences in generalized
psychophysiological interaction (gPPI) connectivity, especially communication
between affective-empathy regions such as anterior insula and dACC/aMCC and
social-cognitive regions such as TPJ, STS, mPFC, and PCC.

## Current Public Results

The public results package reports exploratory full-sample group-interaction
analyses for:

```text
Other Fear Anticipation > Other Safety
N = 54, LKM = 29, PMR = 25
```

These analyses test whether the association between loneliness reduction
(`T1 - T2`; positive values indicate decreased loneliness) and gPPI connectivity
differs between LKM and PMR.

Important caveat: these results are exploratory and post hoc. They do not
establish causality and require replication in an independent or preregistered
analysis.

### Key Exploratory Findings

- Left-AI-seeded connectivity with Right STS showed a group-by-loneliness
  reduction interaction: beta = +1.414, p = .005, FDR q = .029.
- Left-AI-seeded connectivity with Right TPJ showed a similar interaction:
  beta = +1.383, p = .017, FDR q = .050.
- In the fitted interaction model, greater loneliness reduction was associated
  with stronger Left AI-Right STS/TPJ gPPI connectivity in LKM and weaker
  connectivity in PMR.

`Left AI -> Right STS/TPJ` means Left-AI-seeded task-dependent connectivity
with the target ROI. It does not imply causal direction.

## Figure Guide

### Left AI - Right STS Interaction

![Left AI to Right STS group interaction](results/figures/leftAI_rightSTS_group_interaction.png)

This scatter plot shows the strongest exploratory interaction. The x-axis is
loneliness reduction and the y-axis is gPPI connectivity effect for the
Left AI-seeded Right STS target. Blue circles are LKM and red triangles are PMR.
Separate regression lines show that the loneliness-connectivity association is
positive in LKM and negative in PMR for this ROI pair.

### Left AI - Right TPJ Interaction

![Left AI to Right TPJ group interaction](results/figures/leftAI_rightTPJ_group_interaction.png)

This plot shows a similar exploratory pattern for Left AI-seeded Right TPJ
connectivity. The interaction reached the FDR threshold in the reported
six-test exploratory set, but should still be treated as hypothesis-generating.

### Interaction Beta Summary

![Interaction beta forest plot](results/figures/interaction_beta_forest_plot.png)

The forest plot compares interaction beta estimates across the selected ROI
pairs and network composites. Points farther to the right indicate a more
positive LKM-vs-PMR difference in the loneliness-connectivity slope.

### Other Fear Anticipation Heatmap

![Other Fear Anticipation heatmap](results/figures/other_fear_anticipation_heatmap.png)

The heatmap summarizes exploratory associations between loneliness reduction
and gPPI effects across seed-target pairs for the Other Fear Anticipation >
Other Safety contrast. It is useful for pattern inspection, not confirmatory
inference.

See [results/README.md](results/README.md) for public-safe result tables and
additional interpretation notes.

## What Is Included

This repository includes:

- event preparation for ds006243 BIDS `events.tsv` files
- fMRIPrep confound selection and row-count validation
- first-level design matrix construction
- seed time-series extraction
- gPPI design matrix and contrast construction
- first-level and second-level model templates
- synthetic tests for code paths that should not require real fMRI data
- public-safe exploratory summary tables and PNG figures

This repository does not include raw BIDS data, BOLD images, NIfTI/GIFTI/CIFTI
files, ROI mask files, subject-level fMRI maps, full confounds, or large
derivative outputs.

## Data

Download the fMRI dataset separately from:

- [OpenNeuro ds006243, version 1.1.2](https://openneuro.org/datasets/ds006243/versions/1.1.2)

Keep all downloaded data and generated outputs in ignored local folders such as:

```text
data/
derivatives/
outputs/
figures/
masks/
```

Do not commit raw neuroimaging data, derivatives, NIfTI files, masks, or large
outputs. See [docs/data_sources.md](docs/data_sources.md).

## Quick Setup

Create the conda environment:

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

Run synthetic tests:

```bash
PYTHONPATH=src python -m unittest discover tests
```

## Typical Workflow

Run the full pipeline for one subject in dry-run mode:

```bash
python scripts/run_subject_pipeline.py \
  --bids-root data/ds006243 \
  --fmriprep-root derivatives/fmriprep \
  --output-root derivatives/lkm_connectivity \
  --participant-label sub-001 \
  --seed-mask-dir masks \
  --dry-run
```

Then run one subject without `--dry-run`, inspect outputs, and scale up to all
subjects only after local path and mask checks pass.

## Documentation

- [Analysis plan](docs/analysis_plan.md)
- [Data sources](docs/data_sources.md)
- [Running the pipeline](docs/running_pipeline.md)
- [Preparing seed and target masks](docs/seed_masks.md)
- [ROI-to-ROI analysis](docs/roi_to_roi_analysis.md)
- [Public results package](results/README.md)

## Repository Layout

```text
docs/                 analysis notes and running guides
scripts/              command-line pipeline entry points
src/lkm_connectivity/ reusable Python package code
tests/                synthetic tests
results/              public-safe exploratory result summaries
environment.yml       conda environment
requirements.txt      pip requirements
```

## License

Code in this repository is released under the MIT License. Dataset use is
governed by the license and terms associated with OpenNeuro `ds006243` and
related study resources.
