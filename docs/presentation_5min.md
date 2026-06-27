# Five-Minute Presentation Guide

This outline is designed for a five-minute research presentation followed by a
short GitHub live demo. Keep the statistical claims explicitly exploratory.

## 0:00-0:35 - Opening Question

**Slide title:** Does the brain become more empathic, or better connected?

**What to show:** The audience question and options A-C from the README.

**Speaker notes:** Loneliness can change after meditation training, but a
behavioral change does not tell us which neural process changed. Ask whether
the key signal is more similar activity, a larger pain response, or stronger
communication between systems. This project tests the third possibility.

**Audience prompt:** “Which option would you predict before seeing the result?”

## 0:35-1:10 - Original Study vs Reanalysis

**Slide title:** Same dataset, a different question

**What to show:** The “Original Paper vs This Reanalysis” table.

**Speaker notes:** The original study tested self-other multi-voxel pattern
similarity during pain and fearful anticipation. This reanalysis instead asks
whether loneliness reduction is associated with task-dependent connectivity
between affective-empathy and social-cognitive regions, and whether that
association differs between LKM and PMR.

## 1:10-2:00 - Repository Architecture

**Slide title:** A public and auditable analysis

**What to show:** The `docs/`, `scripts/`, `src/lkm_connectivity/`, and `tests/`
folders.

**Speaker notes:** Research decisions live in `docs`, runnable stages in
`scripts`, reusable functions in `src`, and synthetic checks in `tests`. The
separation makes it possible to inspect the reasoning, implementation, and
validation independently. Real imaging data remain local.

**Audience prompt:** “Which folder would you inspect first if you wanted to
audit this analysis?”

## 2:00-3:00 - gPPI Pipeline

**Slide title:** From task timing to connectivity contrasts

**What to show:** The Mermaid pipeline in the README and
`scripts/05_run_gppi.py`.

**Speaker notes:** Events and confounds define the first-level design. A seed
time series from AI or dACC is combined with each task regressor to form gPPI
interaction terms. First-level contrast maps are summarized in target ROIs,
then modeled against loneliness reduction, group, and their interaction. These
are task-dependent associations, not causal arrows between regions.

## 3:00-4:15 - Exploratory Results

**Slide title:** Left AI-seeded connectivity with Right STS and TPJ

**What to show:** The two public-safe interaction plots followed by the forest
plot.

**Speaker notes:** For Other Fear Anticipation greater than Other Safety, the
Left AI-Right STS interaction was beta = 1.414, p = .005, FDR q = .029. The
Left AI-Right TPJ interaction was beta = 1.383, p = .017, FDR q = .050. The
slopes differed by group; this does not mean that LKM had higher connectivity
overall.

**Audience prompt:** “Would you prioritize STS, TPJ, or a preregistered network
composite in the next study?”

## 4:15-5:00 - Reproducibility and Caveat

**Slide title:** Reproducible, but not yet confirmatory

**What to show:** Synthetic tests, `.gitignore`, and the public-safe `results/`
folder.

**Speaker notes:** The repository exposes code, decisions, tests, summary
statistics, and figures while excluding raw BOLD and participant-level
derivatives. The ROI pairs were prioritized after preliminary inspection of
the same dataset. The findings are therefore hypothesis-generating and require
preregistered or independent replication.

**Audience prompt:** “What would make the next analysis genuinely
confirmatory?”
