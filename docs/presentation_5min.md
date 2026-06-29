# Five-Minute Presentation Guide

The central inferential result is the full-sample group interaction. Explain
the separate LKM and PMR lines only after introducing that model.

## 0:00-0:35 - Opening Question

**Slide title:** Do LKM and PMR reduce loneliness through the same neural relationship?

**What to show:** The research question over a minimal LKM-versus-PMR graphic.

**Speaker notes:** Both training groups may show changes in loneliness, but the
same behavioral outcome need not have the same brain-connectivity
relationship. This project asks whether the connectivity-loneliness
relationship differs between groups.

**Interaction question:** “Would you expect the same brain-behavior
relationship in both groups?”

## 0:35-1:10 - Original Paper vs New Question

**Slide title:** Pattern similarity versus task-dependent connectivity

**What to show:** The README comparison table.

**Speaker notes:** The original paper examined whether self and other neural
patterns were similar. This reanalysis asks whether affective-empathy and
social-cognitive regions show task-dependent connectivity during anticipation
of another person's pain.

**Interaction question:** “Does similar activation necessarily imply stronger
communication?”

## 1:10-1:55 - Full-Sample Interaction Model

**Slide title:** The formal test is a difference in slopes

**What to show:** `N = 54`, `LKM = 29`, `PMR = 25`, followed by:

```text
gPPI connectivity ~ loneliness reduction x group
```

**Speaker notes:** The model uses all 54 participants at once. Its interaction
term tests whether the relationship between loneliness reduction and
connectivity has a different slope in LKM and PMR. It is not a test of which
group has higher average connectivity.

**Interaction question:** “Are we testing average group differences, or
differences in slopes?” Answer: “Differences in slopes.”

## 1:55-2:40 - Left AI-Right STS

**Slide title:** Main full-sample interaction: Left AI-seeded Right STS connectivity

**What to show:** `leftAI_rightSTS_group_interaction.png`.

**Speaker notes:** First report the full-sample interaction: beta = +1.414,
p = .005, FDR q = .029. Then explain that the blue LKM line has a positive
fitted slope and the red PMR line has a negative fitted slope. The lines
visualize the interaction; the evidence comes from the interaction term.

**Interaction question:** “What does this interaction not tell us?” Answer:
“It does not show that one group had uniformly higher connectivity.”

## 2:40-3:15 - Left AI-Right TPJ

**Slide title:** Second full-sample interaction: Left AI-seeded Right TPJ connectivity

**What to show:** `leftAI_rightTPJ_group_interaction.png`.

**Speaker notes:** The interaction estimate was beta = +1.383, p = .017, with
FDR q = .050. Describe this as an FDR-threshold exploratory result, not as
stronger confirmation. Again, interpret the group lines only as a
visualization of the full-sample slope difference.

## 3:15-3:50 - Interaction Summary

**Slide title:** Which interaction estimates stood out?

**What to show:** `interaction_beta_forest_plot.png`.

**Speaker notes:** The strongest positive interaction estimates were
concentrated in Left AI-seeded connectivity with Right STS and Right TPJ.
Other tested ROI pairs and composites had confidence intervals overlapping
zero, so they are not presented as significant findings.

**Interaction question:** “Would you carry one ROI pair or both into a
preregistered replication?”

## 3:50-4:25 - Neurocognitive Interpretation

**Slide title:** Linking affective and social-cognitive systems

**What to show:** Left AI beside Right STS and Right TPJ labels.

**Speaker notes:** Left AI is commonly linked to affective salience and
interoceptive-affective processing. Right STS and TPJ are commonly linked to
social perception, mentalizing, and perspective-taking. The results are
consistent with group differences in how these systems' connectivity relates
to loneliness reduction; they do not show causal influence.

## 4:25-5:00 - Reproducibility and Caveat

**Slide title:** Full-sample and FDR-corrected, but exploratory

**What to show:** The README caveat and links to `scripts/`, `src/`, `tests/`,
and reproducibility documentation.

**Speaker notes:** These were full-sample, FDR-corrected interaction results
within the tested family. However, the highlighted ROI pairs were prioritized
after preliminary inspection of the same dataset, so they remain
hypothesis-generating. Independent or preregistered replication is needed.

**Interaction question:** “What would you preregister for replication?”
