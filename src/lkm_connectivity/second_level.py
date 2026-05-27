"""Second-level group analysis helpers."""

import pandas as pd


def build_group_design(participants: pd.DataFrame) -> pd.DataFrame:
    """Create a placeholder second-level design matrix.

    The participants table should include a training-group column once the
    dataset metadata and behavioral files are harmonized.
    """

    if "group" not in participants.columns:
        raise ValueError("Expected a `group` column with LKM/PMR labels.")
    design = pd.get_dummies(participants["group"], prefix="group", drop_first=False)
    design.insert(0, "intercept", 1.0)
    return design
