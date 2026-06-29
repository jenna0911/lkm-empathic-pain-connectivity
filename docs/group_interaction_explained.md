# Understanding the Full-Sample Group Interaction

## What Was Tested?

The analysis used all 54 participants together: 29 LKM and 25 PMR.

```text
gPPI connectivity ~ loneliness reduction x group
```

The interaction term asks whether the slope linking loneliness reduction to
task-dependent connectivity differs between LKM and PMR. It does not ask
whether one group has higher average connectivity.

## What Do the Two Lines Mean?

The scatter plots show separate fitted lines so the interaction is easier to
see:

```text
Full sample N=54
        |
Test: loneliness reduction x group
        |
Evidence for a slope difference
        |
LKM: positive fitted slope
PMR: negative fitted slope
```

These group lines are descriptive components of the full-sample model. The
inferential evidence comes from the interaction beta, its p value, and the FDR
q value. A visible difference between lines alone is not sufficient evidence.

## What Does gPPI Mean Here?

The gPPI effect represents task-dependent functional connectivity during
**Other Fear Anticipation > Other Safety**. “Left AI-seeded connectivity with
Right STS” means that Left AI was the seed used to estimate this connectivity.
It does not show that Left AI causally drives Right STS.

## Why Is the Result Exploratory?

The interaction tests used the full sample and FDR correction within the
tested interaction family. However, the highlighted ROI pairs were prioritized
after preliminary inspection of the same dataset. They are therefore
hypothesis-generating and require independent or preregistered replication.
