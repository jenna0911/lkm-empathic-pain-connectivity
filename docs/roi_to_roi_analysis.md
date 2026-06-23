# AI-TPJ and AI-mPFC ROI-to-ROI gPPI Analysis

## Research Question

This analysis asks whether reductions in loneliness after meditation training
are related to condition-dependent communication between anterior insula (AI)
and social-cognition or mentalizing regions during anticipation and observation
of another person's pain.

Loneliness reduction is defined as:

```text
loneliness_reduction = loneliness_T1 - loneliness_T2
```

Positive values indicate lower loneliness after training.

## Why AI-TPJ and AI-mPFC Connectivity Matters

Anterior insula contributes to affective salience, interoceptive representation,
and the affective component of observed pain. TPJ and mPFC are frequently
implicated in perspective taking, mental-state inference, self-other
distinction, and social appraisal.

AI-TPJ and AI-mPFC gPPI effects therefore test whether an affective/salience
region changes its task-dependent coupling with social-cognitive systems when a
participant anticipates or observes another person's pain. This is a
connectivity question: it does not assume that higher activation or stronger
coupling necessarily means greater empathy.

The six primary ROI pairs are:

- left AI to left TPJ
- left AI to right TPJ
- right AI to left TPJ
- right AI to right TPJ
- left AI to mPFC
- right AI to mPFC

## Difference From dACC-Right AI

The prior dACC/aMCC-right AI analysis focuses primarily on communication within
salience, affective, and pain-related systems. It is useful for testing how
cingulo-insular coupling varies with observed pain.

AI-TPJ and AI-mPFC analyses address a different network relationship:
communication between affective/salience representations and regions involved
in social cognition and mentalizing. These pairs are therefore more directly
aligned with the question of whether loneliness reduction is related to how
affective information about another person's pain is integrated with
perspective taking, self-other distinction, and social interpretation.

Both analyses can be informative, but they should not be treated as
interchangeable network tests.

## Contrasts

The ROI table is generated for four first-level gPPI effect maps:

1. `other_fear_anticipation_vs_safety`
2. `other_pain_stimulation_vs_nopain`
3. `other_specific_fear_anticipation`
4. `other_specific_pain_stimulation`

The two other-specific contrasts subtract the corresponding self-related
condition difference and therefore ask whether coupling is relatively specific
to processing another person's anticipated or observed pain.

## Effect Extraction

For each subject, seed, target, and contrast:

1. Find all available run-level first-level `effect_size` maps.
2. Extract the mean effect within the target ROI mask.
3. Average the run-level values.
4. Merge the result with group, pre/post loneliness, and any additional
   metadata columns, including empathy or state-empathy variables.

Missing masks or contrast maps generate warnings and skip only the affected
analysis cell.

## Group Models

Two ordinary least-squares models are fitted separately for each ROI pair and
contrast:

```text
Model 1: gppi_effect ~ loneliness_reduction + group
Model 2: gppi_effect ~ loneliness_reduction * group
```

Model 1 estimates the loneliness-connectivity association while adjusting for
LKM versus PMR group. Model 2 tests whether that association differs by group.

The statistics table reports coefficient estimates, standard errors, t values,
p values, Benjamini-Hochberg FDR q values, sample size, and the unadjusted
Spearman correlation between loneliness reduction and gPPI effect.

With small samples or many ROI tests, uncorrected p values must be treated as
exploratory. Primary conclusions should use prespecified pairs/contrasts and
FDR-corrected results.

## Interpreting Direction

A positive loneliness-connectivity association means that participants with
larger loneliness reductions tend to show a more positive gPPI contrast effect
for that seed-target pair. Depending on the contrast, this may reflect stronger
coupling during pain/fear relative to its comparison condition, or a less
negative coupling difference.

A negative association means that participants with larger loneliness
reductions tend to show a more negative gPPI contrast effect. This may reflect
weaker coupling in the focal condition, stronger coupling in the comparison
condition, or a shift toward anticorrelation.

Neither direction should automatically be labeled beneficial, empathic, or
maladaptive. Interpretation should consider:

- the exact psychological contrast
- the sign of the underlying condition-specific effects
- the seed and target definitions
- uncertainty and multiple-comparison correction
- whether the association is consistent across runs and groups

## Outputs

Default tabular outputs:

```text
derivatives/roi_to_roi/roi_to_roi_gppi_effects.tsv
derivatives/roi_to_roi/roi_to_roi_group_stats.tsv
```

Default figures:

```text
figures/roi_to_roi/
```

ROI masks, first-level NIfTI maps, derivatives, and generated results must
remain outside version control.
