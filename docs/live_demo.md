# GitHub Live Demo

This script fits a 40-60 second walkthrough.

1. **Open `README.md` (0-8 seconds).**
   Point to the title and three-bullet overview: the original study examined
   pattern similarity; this project examines task-dependent connectivity.

2. **Show the audience question (8-14 seconds).**
   Read the three options and reveal that the repository tests communication
   between affective-empathy and social-cognitive systems.

3. **Scroll to the Mermaid pipeline (14-24 seconds).**
   Briefly trace events and confounds through first-level models, seed x task
   regressors, ROI extraction, and the group interaction.

4. **Open `scripts/05_run_gppi.py` (24-33 seconds).**
   Explain that it combines the first-level design matrix with a seed time
   series and writes gPPI task-interaction regressors and contrast definitions.

5. **Open `tests/` (33-40 seconds).**
   Show that synthetic tests validate events, confounds, design matrices,
   seeds, gPPI construction, and group logic without real participant data.

6. **Open `results/` (40-51 seconds).**
   Show the public-safe Left AI-Right STS and Left AI-Right TPJ figures. Note
   that participant labels and subject-level values are not published.

7. **Open `.gitignore` (51-60 seconds).**
   Point out exclusions for `data/`, `derivatives/`, `outputs/`, `masks/`,
   `*.nii`, `*.nii.gz`, GIFTI, and CIFTI files. End with: “The analysis is
   inspectable, while sensitive and large neuroimaging data remain local.”
