# Exploratory gPPI Group Interaction Results

This folder contains public-safe, summary-level results from OpenNeuro
`ds006243`, version 1.1.2. No participant-level effects or neuroimaging files
are included.

## Sample and Contrast

- **Full sample:** N = 54
- **LKM:** n = 29
- **PMR:** n = 25
- **Contrast:** Other Fear Anticipation > Other Safety
- **Status:** All reported findings are exploratory.

Loneliness reduction is `loneliness_T1 - loneliness_T2`; positive values
indicate decreased loneliness after training.

## 1. Pooled Result

Across all participants, loneliness reduction was not associated with the AI
mentalizing composite:

- Spearman rho = -0.098
- p = .480
- model q = .236

This pooled null result motivates testing whether LKM and PMR have different
brain-behavior slopes.

## 2. Group Interaction Model

```text
gPPI connectivity ~ loneliness reduction x group
```

The interaction tests whether the connectivity-loneliness slopes differ
between LKM and PMR. It does not test whether one group has higher average
connectivity.

## 3. Summary Across Tested Pathways

The forest plot summarizes all selected ROI-pair and network-composite
interaction estimates before the individual scatter plots are interpreted.
The strongest positive estimates were concentrated in Left AI-seeded
connectivity with Right STS and Right TPJ. For the other displayed pathways,
the confidence intervals crossed zero, indicating no clear evidence of a
group slope difference in the tested model.

## 4. Main Exploratory Pathway

**Left AI-seeded connectivity with Right STS**

- Interaction beta = +1.414
- p = .005
- FDR q = .029

The FDR-corrected full-sample interaction indicates that the
connectivity-loneliness relationship differed between LKM and PMR. The
separate fitted lines visualize that interaction; they are not separate
primary tests.

## 5. Related Exploratory Pathway

**Left AI-seeded connectivity with Right TPJ**

- Interaction beta = +1.383
- p = .017
- FDR q = .050
- Label: FDR-threshold exploratory finding

The Right TPJ estimate showed a similar pattern but should be interpreted
cautiously because its q value was at the .05 threshold.

## Conclusion

The pooled analysis did not show a simple overall association, while the
full-sample interaction model identified two candidate Left AI-seeded
pathways with right-lateralized social-cognitive targets. The repository
contributes a transparent gPPI workflow and candidate pathways for
confirmatory follow-up.

## Discussion

The pattern is consistent with different links between affective-empathy and
social-cognitive systems in LKM and PMR. It does not establish causal
direction, intervention superiority, mediation, or a clinical treatment
mechanism.

The highlighted ROI pairs were prioritized after preliminary inspection of
the same dataset. Although FDR correction was applied within the tested
interaction family, independent or preregistered replication is needed.

## Public-Safe Files

- `fullsample_group_interaction_stats.tsv`: Aggregate ROI-pair interaction
  statistics.
- `fullsample_network_composite_stats.tsv`: Aggregate composite interaction
  statistics.
- `analysis_manifest_summary.tsv`: Aggregate sample and analysis summary.
- `figures/pooled_AI_mentalizing_composite.png`: Pooled full-sample result.
- `figures/interaction_beta_forest_plot.png`: Summary across tested pathways.
- `figures/leftAI_rightSTS_group_interaction.png`: Main exploratory pathway.
- `figures/leftAI_rightTPJ_group_interaction.png`: Related exploratory pathway.

## Data Safety

No raw data, individual BOLD time series, NIfTI/GIFTI/CIFTI files, ROI masks,
confounds, subject-level maps, or participant-level effect tables are
included.

## Related Documentation

- [ROI-to-ROI analysis](../docs/roi_to_roi_analysis.md)
- [Running the pipeline](../docs/running_pipeline.md)
- [OpenNeuro ds006243](https://openneuro.org/datasets/ds006243/versions/1.1.2)
- [Data sources](../docs/data_sources.md)
