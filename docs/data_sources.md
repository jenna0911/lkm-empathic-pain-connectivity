# Data Sources

## OpenNeuro fMRI Data

The primary neuroimaging data source is OpenNeuro dataset `ds006243`.

Download the BIDS dataset and available fMRIPrep derivatives directly from OpenNeuro using the OpenNeuro web interface, DataLad, or the OpenNeuro command-line tools. Do not commit the downloaded dataset to this repository.

Recommended local layout:

```text
data/ds006243/
derivatives/fmriprep/
```

Both locations are ignored by Git.

## Behavioral and Task Resources

Behavioral files, task-code resources, and publication-related materials should be obtained from the OSF and GitHub resources associated with the original study and OpenNeuro dataset. These resources may include:

- task timing and condition documentation
- behavioral ratings or training-related measures
- analysis scripts from the original study
- paper supplements and metadata

Only lightweight, redistribution-safe metadata or derived documentation should be committed. Do not commit private, restricted, identifying, or large source data.

## Data Handling Rules

This repository should not contain:

- raw BIDS neuroimaging files
- fMRIPrep derivatives
- NIfTI images
- CIFTI/GIFTI images
- statistical maps
- generated reports
- large tables or binary outputs
- subject-level data that should remain local

Use local ignored directories such as:

```text
data/
derivatives/
results/
scratch/
```

## Suggested Download Notes

Each analyst should keep a local note of:

- OpenNeuro dataset version or snapshot date
- download method
- fMRIPrep derivative version, if applicable
- any files excluded from local analysis
- checksums or DataLad commit identifiers, when available

These notes can be summarized in reproducibility reports without committing the dataset itself.
