# Brain Connectivity During Observed Fear Anticipation and Loneliness Reduction After Meditation Training

> **Can another researcher reproduce this fMRI analysis without asking for hidden scripts or undocumented preprocessing decisions?**

A reproducible gPPI reanalysis of OpenNeuro `ds006243` comparing
Loving-Kindness Meditation (LKM) and Progressive Muscle Relaxation (PMR).

**Quick navigation:** [30-second overview](#30-second-overview) |
[Pipeline](#pipeline-at-a-glance) | [Main results](#main-exploratory-result) |
[Reproducibility](#reproducibility) | [5-minute presentation](docs/presentation_5min.md) |
[Live demo](docs/live_demo.md)

## 30-Second Overview

- **Original study:** self-other pattern similarity during empathic pain.
- **This project:** task-dependent functional connectivity between affective-empathy and social-cognitive systems.
- **Main exploratory finding:** group-dependent Left AI-seeded connectivity with Right STS and Right TPJ during **Other Fear Anticipation > Other Safety**.

## Question for the Audience

> **When loneliness decreases, does the brain become more empathic, or better connected?**

- **A.** Stronger self-other pattern similarity
- **B.** Stronger pain response
- **C.** Stronger communication between affective-empathy and social-cognitive systems

**This repository tests option C.**

## Original Paper vs This Reanalysis

| Original study | This reanalysis |
| --- | --- |
| Self-other multi-voxel pattern similarity | Task-dependent functional connectivity |
| Are self and other neural patterns similar? | Do affective-empathy and social-cognitive regions communicate differently? |
| AI and dACC local pattern representation | AI/dACC-seeded connectivity with TPJ, STS, mPFC, and PCC |
| Loneliness and pattern similarity | Loneliness reduction x meditation group interaction |

## Pipeline at a Glance

```mermaid
flowchart LR
    A["OpenNeuro<br/>ds006243"] --> B["Task events<br/>+ confounds"]
    B --> C["First-level<br/>design matrix"]
    C --> D["AI/dACC seed<br/>time series"]
    D --> E["gPPI seed x task<br/>regressors"]
    E --> F["First-level<br/>contrast maps"]
    F --> G["ROI-to-ROI<br/>extraction"]
    G --> H["Loneliness reduction<br/>x group interaction"]
    H --> I["Public-safe<br/>results"]
```

gPPI estimates task-dependent functional connectivity. A label such as
“Left AI-seeded connectivity with Right STS” describes the seed used to
estimate connectivity; it does **not** imply causal influence from one region
to another.

**No raw BOLD data, NIfTI maps, or participant-level derivatives are committed
to this repository.**

## Main Exploratory Result

### Left AI-seeded connectivity with Right STS

- **Contrast:** Other Fear Anticipation > Other Safety
- **Interaction beta:** +1.414
- **p:** .005
- **FDR q:** .029
- **Interpretation:** The association between loneliness reduction and Left
  AI-Right STS connectivity differed between LKM and PMR.

![Exploratory Left AI-seeded connectivity with Right STS interaction](results/figures/leftAI_rightSTS_group_interaction.png)

### Left AI-seeded connectivity with Right TPJ

- **Interaction beta:** +1.383
- **p:** .017
- **FDR q:** .050
- **Label:** FDR-threshold exploratory finding

![Exploratory Left AI-seeded connectivity with Right TPJ interaction](results/figures/leftAI_rightTPJ_group_interaction.png)

### Selected Interaction Estimates

![Exploratory interaction beta forest plot](results/figures/interaction_beta_forest_plot.png)

All figures above are public-safe versions without participant labels. See the
[figure guide](docs/figures/README.md) and
[public result tables](results/README.md).

## How to Read the Interaction

> An interaction does not mean LKM had higher connectivity overall. It means
> the relationship between loneliness reduction and connectivity had
> different slopes in LKM and PMR.

```text
LKM:
loneliness reduction increases -> Left AI-Right STS/TPJ connectivity increases

PMR:
loneliness reduction increases -> connectivity shows the opposite trend
```

Loneliness reduction is `T1 - T2`; positive values indicate decreased
loneliness after training.

## Reproducibility

**`docs/`**

Research question, ROI definitions, data sources, and analysis rationale.

**`scripts/`**

Step-by-step runnable analysis commands.

**`src/lkm_connectivity/`**

Reusable Python functions for events, confounds, GLM, gPPI, and group models.

**`tests/`**

Synthetic tests that validate analysis logic without requiring real fMRI data.

Start here:

- [Run the pipeline](docs/running_pipeline.md)
- [Understand the ROI-to-ROI analysis](docs/roi_to_roi_analysis.md)
- [Prepare seed and target masks](docs/seed_masks.md)
- [Reproduce and audit the workflow](docs/reproducibility.md)

## Repository Layout

```text
docs/                 research decisions, presentation, and running guides
results/              small public-safe summary tables and figures
scripts/              command-line entry points for each pipeline stage
src/lkm_connectivity/ reusable analysis functions
tests/                synthetic validation without private or imaging data
README.md             research story and navigation
environment.yml       reproducible Conda environment
requirements.txt      Python package requirements
.gitignore            safeguards against committing imaging data and outputs
```

## Important Caveat

> **These findings are FDR-corrected exploratory results. The ROI pairs were
> prioritized after preliminary inspection of the same dataset, so the
> findings are hypothesis-generating rather than confirmatory. They require
> preregistered or independent replication.**

The interaction pattern is consistent with a group difference in the
loneliness-connectivity association, but it does not establish that LKM caused
the connectivity difference or the reduction in loneliness.

## Discussion Prompt

> **If you were preregistering the next study, would you select Left AI-Right
> STS, Left AI-Right TPJ, or both as the primary pathway? Why?**
