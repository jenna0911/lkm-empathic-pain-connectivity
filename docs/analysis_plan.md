# Analysis Plan

## Project Aim

This project reanalyzes OpenNeuro `ds006243` to test whether Loving-Kindness Meditation (LKM) changes task-based functional connectivity during empathic pain anticipation and observation compared with Progressive Muscle Relaxation (PMR).

The main analysis will use first-level GLM models and generalized psychophysiological interaction (gPPI) models to estimate condition-dependent connectivity between predefined seed regions and target networks.

## Main Hypotheses

### H1: LKM modulates empathy-network connectivity during anticipation

During anticipation of another person's pain, LKM participants are expected to show altered connectivity between salience/affective seeds and regions involved in mentalizing, self-other processing, and emotion regulation compared with PMR participants.

Candidate pattern:

- stronger coupling between anterior insula or anterior cingulate seeds and medial prefrontal or temporoparietal regions
- reduced coupling patterns consistent with lower defensive or threat-related responding, depending on the direction of behavioral effects

### H2: LKM modulates empathy-network connectivity during pain observation

During observation of painful stimulation to another person, LKM participants are expected to show altered connectivity within empathy-related sensorimotor, salience, and affective networks compared with PMR participants.

Candidate pattern:

- altered anterior insula and cingulate coupling with somatosensory and affective targets
- altered connectivity with mentalizing regions that may support compassionate appraisal

### H3: Connectivity effects are phase-specific

Training-related connectivity effects may differ between anticipation and stimulation periods. Anticipation may emphasize prediction, affective preparation, and regulation; stimulation may emphasize observed pain processing and embodied empathy.

## Task Phases

The first-level models should distinguish at least two task periods:

- `anticipation`: cue or expectation period before stimulation
- `stimulation`: observation of painful or non-painful stimulation

Condition labels should be derived from the dataset's event files and original task documentation. The final event model should preserve enough detail to estimate pain versus non-pain and anticipation versus stimulation effects.

## Planned First-Level Contrasts

Exact condition names should be verified against the BIDS `events.tsv` files before implementation. Planned contrasts include:

- pain anticipation > non-pain anticipation
- pain stimulation/observation > non-pain stimulation/observation
- anticipation pain effect versus stimulation pain effect
- LKM-relevant task effects within subject, to be carried into group models

For gPPI, psychological regressors should represent condition-specific task periods. Physiological regressors should be seed time series extracted from predefined ROIs. Interaction regressors should model seed-by-condition coupling.

## Seed Regions

Seed definitions should use reproducible atlas labels or documented binary masks. Candidate seed regions:

- bilateral anterior insula
- anterior mid-cingulate cortex or dorsal anterior cingulate cortex
- supplementary motor area
- temporoparietal junction
- medial prefrontal cortex
- primary or secondary somatosensory cortex

Seed selection should be finalized before confirmatory analyses. Exploratory seed analyses should be labeled as exploratory.

## Target Regions

Target regions may be evaluated using whole-brain maps and/or ROI summaries. Candidate targets:

- empathy and pain-observation network regions
- salience network regions
- mentalizing network regions
- sensorimotor regions
- affective and regulatory regions, including medial prefrontal and cingulate cortices

When ROI-to-ROI summaries are used, atlas choice, label names, hemisphere handling, and multiple-comparison correction should be documented.

## Group-Level Models

Second-level models should test training-group differences and task effects. Candidate models:

- one-sample group maps for each first-level contrast
- two-sample LKM versus PMR comparisons
- interaction-style tests comparing phase-specific or condition-specific gPPI effects between groups

Potential covariates should be determined from available behavioral and demographic files and documented before inclusion.

## Expected Outputs

Expected outputs should be written to ignored directories such as `derivatives/lkm_connectivity/` and `results/`:

- cleaned and harmonized event files
- confound files used for first-level models
- first-level design matrices and model reports
- seed time series summaries
- gPPI beta and contrast maps
- second-level statistical maps
- ROI summary tables
- publication-ready figures
- provenance notes describing software versions and analysis parameters

## Reproducibility Notes

The public repository should contain code, documentation, and lightweight metadata only. Raw BIDS data, fMRIPrep derivatives, NIfTI files, statistical maps, and large generated outputs should remain outside Git.
