# Public Figure Guide

All figures are aggregate, public-safe PNG files without participant labels.

## 1. `pooled_AI_mentalizing_composite.png`

- **Figure purpose:** Test whether one pooled brain-behavior relationship
  describes all participants.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Sample size:** N = 54.
- **Statistical interpretation:** Spearman rho = -0.098, p = .480, model
  q = .236; no evidence of a simple pooled association.
- **Status:** Exploratory.
- **Figure level:** Summary-level network composite.

## 2. `interaction_beta_forest_plot.png`

- **Figure purpose:** Compare group interaction estimates across all tested
  ROI pathways and network composites before inspecting individual scatter
  plots.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Sample size:** N = 54; LKM n = 29, PMR n = 25.
- **Statistical interpretation:** Dots are interaction betas; horizontal lines
  are 95% confidence intervals; zero indicates no difference in group slopes.
  Intervals crossing zero indicate no clear evidence of a group slope
  difference in the tested model.
- **Status:** Exploratory.
- **Figure level:** Summary-level pathway comparison.

## 3. `leftAI_rightSTS_group_interaction.png`

- **Figure purpose:** Visualize the strongest positive group interaction
  estimate, Left AI-seeded connectivity with Right STS.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Sample size:** N = 54; LKM n = 29, PMR n = 25.
- **Statistical interpretation:** Interaction beta = +1.414, p = .005, FDR
  q = .029. Separate fitted lines visualize the full-sample interaction.
- **Status:** FDR-corrected exploratory finding; not confirmatory.
- **Figure level:** ROI-specific.

## 4. `leftAI_rightTPJ_group_interaction.png`

- **Figure purpose:** Visualize the related Left AI-seeded Right TPJ group
  interaction estimate.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Sample size:** N = 54; LKM n = 29, PMR n = 25.
- **Statistical interpretation:** Interaction beta = +1.383, p = .017, FDR
  q = .050; threshold-level result requiring cautious interpretation.
- **Status:** FDR-threshold exploratory finding; not confirmatory.
- **Figure level:** ROI-specific.

The figure files are stored in [`results/figures/`](../../results/figures/).
