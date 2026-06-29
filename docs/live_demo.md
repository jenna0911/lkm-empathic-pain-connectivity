# GitHub Live Demo

This 40-60 second demo keeps the full-sample interaction model ahead of any
description of separate group slopes.

1. **Open the README at “Primary Analytic Question.”**

   Say: “We are asking whether the brain-behavior relationship differs between
   LKM and PMR.”

2. **Point to the sample definition.**

   Emphasize that the analysis uses the full sample: N = 54, with 29 LKM and
   25 PMR participants. It is not introduced as an LKM-only test.

3. **Show the regression model.**

   Read `gPPI connectivity ~ loneliness reduction x group` and identify the
   interaction as the test of different regression slopes.

4. **Open the Left AI-Right STS figure.**

   Point to N = 54, interaction beta = +1.414, p = .005, and FDR q = .029.

5. **Explain the two lines.**

   Say: “The positive LKM and negative PMR fitted lines visualize the
   full-sample interaction. They are not separate primary inferential tests.”

6. **Open the forest plot.**

   Note that Left AI-seeded Right STS and Right TPJ connectivity had the
   strongest positive interaction estimates, while the other displayed
   confidence intervals overlap zero.

7. **End with caveat and reproducibility.**

   Show the exploratory caveat, then point to `scripts/`, `src/`, `tests/`,
   `docs/reproducibility.md`, and `.gitignore`. No raw BOLD, NIfTI, masks, or
   participant-level derivatives are published.
