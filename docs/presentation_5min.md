# Five-Minute Presentation Guide

The presentation moves from the pooled result to the pathway summary, then
uses the two ROI scatter plots to explain the strongest candidate
interactions.

## 0:00-0:35

**Slide title:** Does reduced loneliness follow one shared neural relationship?

**What to show:** The opening research question.

**Speaker notes:** Begin by asking whether one brain-behavior relationship can
describe everyone whose loneliness decreases. The alternative is that the
relationship may differ between LKM and PMR.

**Audience prompt:** “Would you expect one shared neural relationship across
both groups?”

## 0:35-1:05

**Slide title:** Original paper versus this reanalysis

**What to show:** The README comparison table: pattern similarity versus
task-dependent connectivity.

**Speaker notes:** The original study examined self-other pattern similarity
during pain and fearful anticipation. This reanalysis examines whether
affective-empathy and social-cognitive regions show task-dependent
connectivity related to loneliness reduction.

**Audience prompt:** “Does similar activation necessarily mean stronger
connectivity?”

## 1:05-1:35

**Slide title:** No simple pooled association

**What to show:** `pooled_AI_mentalizing_composite.png`.

**Speaker notes:** Across all 54 participants, the pooled association was near
zero: Spearman rho = -0.098, p = .480, model q = .236. The figure uses one
regression line and does not separate LKM from PMR.

**Audience prompt:** “What might a single pooled line hide?”

## 1:35-2:05

**Slide title:** Why test a group interaction?

**What to show:**

```text
gPPI connectivity ~ loneliness reduction x group
```

**Speaker notes:** A near-zero pooled association does not necessarily mean
there is no group-dependent pattern. Opposite fitted slopes can cancel when
groups are combined. The interaction term formally tests whether the slopes
differ.

**Audience prompt:** “Can a pooled null result coexist with two different
group slopes?”

## 2:05-2:40

**Slide title:** Which pathways merit closer inspection?

**What to show:** `interaction_beta_forest_plot.png`.

**Speaker notes:** Each dot is an interaction beta, each horizontal line is a
95% confidence interval, and the vertical line marks zero slope difference.
The strongest positive estimates were concentrated in Left AI-seeded
connectivity with Right STS and Right TPJ, so those pathways are shown next.

**Audience prompt:** “What does it mean when a confidence interval crosses
zero?”

## 2:40-3:30

**Slide title:** Main pathway: Left AI-seeded Right STS connectivity

**What to show:** `leftAI_rightSTS_group_interaction.png`.

**Speaker notes:** State the full-sample interaction first: beta = +1.414,
p = .005, FDR q = .029. Then explain that the positive LKM and negative PMR
lines visualize the fitted slope difference. The statistical test is the
interaction term, not separate within-group correlations.

**Audience prompt:** “Does this result mean LKM had higher connectivity
overall?”

## 3:30-4:00

**Slide title:** Related pathway: Left AI-seeded Right TPJ connectivity

**What to show:** `leftAI_rightTPJ_group_interaction.png`.

**Speaker notes:** The interaction estimate was beta = +1.383, p = .017, with
FDR q = .050. This right TPJ finding is at the FDR threshold and should be
described cautiously as exploratory.

**Audience prompt:** “How should a finding exactly at the FDR threshold be
reported?”

## 4:00-4:30

**Slide title:** Conclusion

**What to show:** The three-point take-home message.

**Speaker notes:** A pooled null association can mask group-dependent slopes.
The strongest candidate pathway involved Left AI-seeded connectivity with
Right STS, with Right TPJ as a related threshold-level finding. The candidate
targets are right-lateralized social-cognitive regions.

**Audience prompt:** “Which pathway would you carry forward as primary?”

## 4:30-5:00

**Slide title:** Discussion and caveat

**What to show:** The limitations and next-step bullets.

**Speaker notes:** The findings are correlational, exploratory, and do not
establish causal influence or intervention superiority. The ROI pairs were
prioritized after preliminary inspection, so independent or preregistered
replication is required.

**Audience prompt:** “What would you preregister as the primary pathway for
replication, and why?”
