# Preparing Seed ROI Masks

This project uses three seed regions for task-based gPPI analyses:

- left anterior insula
- right anterior insula
- dACC / aMCC

Seed masks should be binary 3D NIfTI images in the same MNI space, resolution,
shape, and affine as the fMRIPrep preprocessed BOLD images used for extraction.
The repository does not include ROI NIfTI files.

## Option 1: Use Original-Study Masks

If the original paper, OSF project, or associated GitHub repository provides
ROI masks, use those masks when their provenance, coordinate space, and license
allow reuse.

Before using them, document:

- source URL or citation
- mask name and region definition
- image space and template
- resampling steps, if any
- whether the mask is unilateral or bilateral

Keep the NIfTI files local, for example:

```text
masks/left_anterior_insula_mask.nii.gz
masks/right_anterior_insula_mask.nii.gz
masks/dacc_amcc_mask.nii.gz
```

## Option 2: Use Standard Atlases

Standard atlas masks are acceptable when original-study masks are unavailable.
Possible sources include:

- Harvard-Oxford cortical atlas labels for anterior insula or cingulate regions
- other documented anatomical atlases available through Nilearn or FSL
- Neurosynth-derived association masks for terms such as anterior insula, dACC,
  anterior mid-cingulate, pain, empathy, or salience

When atlas masks are used, record:

- atlas name and version
- label names or thresholding rule
- probability threshold, if using probabilistic maps
- hemisphere split rule for left and right anterior insula
- any resampling to fMRIPrep MNI space

## Region-Specific Notes

### Left Anterior Insula

Use a unilateral left anterior insula mask. If starting from a bilateral atlas
label, split by hemisphere and retain only the left-side anterior insula voxels.

### Right Anterior Insula

Use a unilateral right anterior insula mask. It should be prepared with the same
atlas, thresholding, and resampling choices as the left anterior insula mask.

### dACC / aMCC

Use a midline dorsal anterior cingulate or anterior mid-cingulate mask. Be clear
about whether the mask reflects anatomical dACC, aMCC, a functional pain/salience
cluster, or a merged dACC/aMCC region.

## Local Storage

Store masks locally under an ignored directory such as:

```text
masks/
```

The batch runner searches for these filenames:

```text
left_anterior_insula.nii.gz
left_anterior_insula_mask.nii.gz
right_anterior_insula.nii.gz
right_anterior_insula_mask.nii.gz
dacc_amcc.nii.gz
dacc_amcc_mask.nii.gz
```

## Git Policy

Do not commit large NIfTI masks or generated mask derivatives unless the project
explicitly decides that a small, redistribution-safe mask should be versioned.
If masks are ever committed, confirm license compatibility and keep file sizes
small. Raw fMRI data, fMRIPrep derivatives, and generated statistical maps
should never be committed.
