# Five-Minute Presentation Guide

The story moves from a pooled null result to the possibility of opposing group
slopes, then to the formal full-sample interaction test.

## Opening Question

**What to show:** “Do you feel lonely? When loneliness decreases, do people
simply feel better—or does their brain become better at connecting with other
people?”

**Speaker notes:** A pooled analysis assumes that one brain-behavior
relationship can describe all participants. Before comparing groups, we first
ask whether loneliness reduction has a simple overall association with
connectivity.

**Interaction question:** “Would you expect one shared relationship across
both training groups?”

## Original Paper vs This Reanalysis

**What to show:** The README comparison table.

**Speaker notes:** The original study examined self-other pattern similarity
during pain and fearful anticipation. This reanalysis instead examines
task-dependent communication between affective-empathy and social-cognitive
regions.

**Interaction question:** “Does similar activation necessarily mean stronger
functional connectivity?”

## Pooled AI Mentalizing Composite

**What to show:** `ai_mentalizing_composite_pooled.png`.

**Speaker notes:** Across all 54 participants, the pooled association was near
zero: Spearman rho = -0.098, p = .480, model q = .236. The figure uses one
color and one regression line because this step deliberately ignores group.
The null pooled result does not show that the groups have identical slopes.

**Interaction question:** “What information might be hidden when everyone is
fit with one line?”

## Why a Null Pooled Result May Hide Structure

**What to show:** One positive and one negative schematic line converging on a
near-flat pooled line.

**Speaker notes:** If LKM has a positive fitted slope and PMR has a negative
fitted slope, combining both groups can produce a near-zero overall
association. Therefore, a pooled null result does not rule out group-dependent
relationships.

**Interaction question:** “If the pooled relationship is near zero, does that
mean there is no effect?” Answer: “Not necessarily. Opposite group slopes can
cancel each other.”

## Full-Sample Interaction Model

**What to show:**

```text
gPPI connectivity ~ loneliness reduction x group
N = 54; LKM = 29; PMR = 25
```

**Speaker notes:** This model uses all 54 participants simultaneously. The
interaction term tests whether the connectivity-loneliness slope differs
between LKM and PMR. It does not test whether one group has higher average
connectivity.

**Interaction question:** “Which term formally tests whether the two slopes
differ?” Answer: “The loneliness reduction x group interaction.”

## Left AI-Right STS Interaction

**What to show:** `leftAI_rightSTS_group_interaction.png`.

**Speaker notes:** Report the full-sample interaction first: beta = +1.414,
p = .005, FDR q = .029. Then explain that the positive LKM and negative PMR
lines visualize the fitted slope difference. The inferential evidence comes
from the full-sample interaction term, not two separate group tests.

**Interaction question:** “Does this plot show that LKM had higher connectivity
overall?” Answer: “No; it shows different fitted slopes.”

## Left AI-Right TPJ Interaction

**What to show:** `leftAI_rightTPJ_group_interaction.png`.

**Speaker notes:** A similar interaction pattern appeared for Right TPJ:
beta = +1.383, p = .017, FDR q = .050. Because q is at the .05 threshold,
describe this finding cautiously and explicitly as exploratory.

**Interaction question:** “How would you describe a result exactly at the FDR
threshold?”

## Tested Pathways

**What to show:** `interaction_beta_forest_plot.png`.

**Speaker notes:** The strongest positive estimates were for Left AI-seeded
connectivity with Right STS and Right TPJ. Other tested pathways had
confidence intervals overlapping zero and are not presented as significant
findings.

**Interaction question:** “Which pathway would you prioritize for
preregistered replication?”

## Transparent Analysis

**What to show:** The six-step vertical Mermaid pipeline and the exploratory
caveat.

**Speaker notes:** The repository documents events, confounds, first-level
design, seed time series, gPPI fitting, and the final group interaction model.
Raw imaging and participant-level derivatives remain local. These findings are
hypothesis-generating and require preregistered or independent replication.

**Interaction question:** “Which step would you audit first?”

**Closing line:** “This repository makes the full pathway from OpenNeuro data
to group interaction test transparent and reproducible.”
