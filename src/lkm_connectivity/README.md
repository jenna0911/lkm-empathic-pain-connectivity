# Package Modules

Each module owns one stage or concern in the analysis:

| Module | Responsibility |
| --- | --- |
| `config.py` | Shared project path configuration. |
| `events.py` | Event loading and gPPI condition preparation. |
| `confounds.py` | fMRIPrep confound selection and run-length validation. |
| `glm.py` | First-level design-matrix construction. |
| `seeds.py` | ROI mask validation and seed time-series extraction. |
| `gppi.py` | gPPI interaction regressors and contrast definitions. |
| `firstlevel.py` | First-level gPPI model fitting and contrast maps. |
| `secondlevel.py` | Group design, validation, and second-level models. |

The package uses `secondlevel.py` as the canonical second-level implementation.
The earlier `second_level.py` placeholder and unused compatibility wrappers
were removed to avoid parallel APIs for the same operation.
