# Exploratory gPPI Group Interaction Results

This folder contains a public-safe summary of exploratory ROI-to-ROI gPPI group-interaction results for OpenNeuro `ds006243`, version 1.1.2.

## Research Question

Do LKM and PMR differ in the association between loneliness reduction and task-based gPPI connectivity during `Other Fear Anticipation > Other Safety`?

Loneliness reduction was defined as `loneliness_T1 - loneliness_T2`, so positive values indicate decreased loneliness after training.

## Primary Reported Exploratory Findings

Within the six specified exploratory ROI/composite tests, the strongest group-by-loneliness reduction interactions were:

- Left-AI-seeded connectivity with Right STS: interaction beta = +1.414, p = .005, FDR q = .029.
- Left-AI-seeded connectivity with Right TPJ: interaction beta = +1.383, p = .017, FDR q = .050.

Greater loneliness reduction was associated with stronger Left AI-Right STS/TPJ gPPI connectivity in LKM and weaker connectivity in PMR, based on the fitted interaction model.

## Critical Caveat

These analyses are exploratory and post hoc. They do not establish causality and require replication in an independent or preregistered analysis. The ROI pairs were selected after preliminary inspection, so these results should be interpreted as hypothesis-generating.

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
