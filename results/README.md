# Exploratory gPPI Group Interaction Results

This folder contains a public-safe summary of exploratory ROI-to-ROI gPPI group-interaction results for OpenNeuro `ds006243`, version 1.1.2.

## Full-Sample Analytic Question

Do LKM and PMR differ in the association between loneliness reduction and task-based gPPI connectivity during `Other Fear Anticipation > Other Safety`?

Loneliness reduction was defined as `loneliness_T1 - loneliness_T2`, so positive values indicate decreased loneliness after training.

Rather than testing whether either group had higher average connectivity, the
full-sample model tested whether the connectivity-loneliness reduction slopes
differed:

```text
gPPI connectivity ~ loneliness reduction x group
```

The analysis included all 54 participants: 29 LKM and 25 PMR.

## Main Full-Sample Interaction Results

1. **Left AI-seeded connectivity with Right STS:** interaction beta = +1.414,
   p = .005, FDR q = .029.
2. **Left AI-seeded connectivity with Right TPJ:** interaction beta = +1.383,
   p = .017, FDR q = .050; FDR-threshold exploratory finding.

The groups showed different connectivity-loneliness reduction slopes. The
positive LKM and negative PMR fitted lines explain the interaction pattern,
but the inferential test is the interaction term in the full-sample model, not
separate within-group correlations. One group did not necessarily have
uniformly higher connectivity.

## Neurocognitive Interpretation

Left AI is commonly linked to affective salience and
interoceptive-affective processing, while Right STS and Right TPJ are commonly
associated with social perception, mentalizing, and perspective-taking. The
interaction is therefore consistent with different links between
affective-empathy and social-cognitive systems after LKM versus PMR. “Left
AI-seeded connectivity” does not imply causal direction.

## Critical Caveat

These were full-sample, FDR-corrected group interaction results within the
tested interaction family. However, because the highlighted ROI pairs were
prioritized after preliminary inspection of the same dataset, they should be
interpreted as exploratory and hypothesis-generating rather than confirmatory.
Independent or preregistered replication is needed.

gPPI estimates task-dependent functional connectivity. Labels such as `Left AI -> Right STS` mean Left-AI-seeded connectivity with a Right STS target ROI; they do not imply causal directional influence from Left AI to Right STS.

No raw data, individual BOLD time series, NIfTI maps, GIFTI/CIFTI files, ROI masks, full confounds, subject-level fMRI maps, or complete subject-level effect tables are included.

## Files

- `fullsample_group_interaction_stats.tsv`: Public-safe ROI-pair interaction statistics.
- `fullsample_network_composite_stats.tsv`: Public-safe composite interaction statistics.
- `analysis_manifest_summary.tsv`: Public-safe analysis/sample summary.
- `figures/`: Public-safe PNG figures without participant labels.

## Related Documentation

- [ROI-to-ROI analysis](../docs/roi_to_roi_analysis.md)
- [Running the pipeline](../docs/running_pipeline.md)
- [OpenNeuro ds006243](https://openneuro.org/datasets/ds006243/versions/1.1.2)
- See [data sources](../docs/data_sources.md) for additional study-resource notes.
