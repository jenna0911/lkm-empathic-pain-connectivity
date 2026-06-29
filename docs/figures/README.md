# Public Figure Guide

All figures listed here are aggregate, public-safe PNG files, and participant
labels have been removed. The pooled figure uses one model across N = 54. The
interaction figures use separate fitted lines only to visualize a full-sample
group interaction; they are not separate LKM-only or PMR-only tests.

## `ai_mentalizing_composite_pooled.png`

- **What is plotted:** Loneliness reduction against the AI mentalizing
  composite across all 54 participants, using one color and one pooled
  regression line.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Statistics shown:** Spearman rho = -0.098, p = .480, model q = .236.
- **Group display:** No group colors, group labels, or separate group fits.
- **Status:** Exploratory pooled analysis; no evidence of a simple pooled
  association.
- **Participant labels:** Removed.

## `leftAI_rightSTS_group_interaction.png`

- **What is plotted:** Full-sample group interaction analysis (N = 54).
  Points are individual participants; colors and marker shapes indicate group.
  Separate fitted lines visualize the group-by-loneliness reduction
  interaction.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Model:** gPPI effect ~ loneliness reduction x group.
- **Statistics shown:** Interaction beta = +1.414, p = .005, FDR q = .029.
- **Status:** Exploratory and post hoc; not confirmatory.
- **Participant labels:** Removed.

## `leftAI_rightTPJ_group_interaction.png`

- **What is plotted:** Full-sample group interaction analysis (N = 54) for
  Left AI-seeded connectivity with Right TPJ. Separate LKM and PMR fitted lines
  visualize the interaction.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Model:** gPPI effect ~ loneliness reduction x group.
- **Statistics shown:** Interaction beta = +1.383, p = .017, FDR q = .050.
- **Status:** Exploratory and post hoc; not confirmatory.
- **Participant labels:** Removed.

## `interaction_beta_forest_plot.png`

- **What is plotted:** Group-by-loneliness reduction interaction estimates and
  95% confidence intervals for selected ROI pairs and network composites.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Status:** Exploratory summary; not confirmatory.
- **Participant labels:** Not applicable; only aggregate estimates are shown.
- **Interpretation:** The strongest positive estimates were concentrated in
  Left AI-seeded connectivity with Right STS and Right TPJ; other displayed
  confidence intervals overlap zero.

## `other_fear_anticipation_heatmap.png`

- **What is plotted:** Spearman associations between loneliness reduction and
  gPPI effects across seed-target pairs for the full sample, LKM, and PMR.
- **Contrast:** Other Fear Anticipation > Other Safety.
- **Status:** Exploratory pattern display; not confirmatory.
- **Participant labels:** Not shown.

The figure files are stored in [`results/figures/`](../../results/figures/).
