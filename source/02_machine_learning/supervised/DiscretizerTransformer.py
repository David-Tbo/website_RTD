import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class DiscretizerTransformer(BaseEstimator, TransformerMixin):
    """
    Applies predefined cut points to continuous variables and produces
    one-hot encoded discretized features.

    This transformer takes the cut points selected during the binning
    selection phase (e.g., via DiscretizerSelector), converts each
    continuous variable into interval-based bins, and generates a
    one-hot encoded representation with clean, auditable feature names.

    The transformer:
    - applies the retained cut points for each variable,
    - discretizes continuous features into interval bins,
    - performs one-hot encoding of the resulting bins,
    - generates interpretable and audit-friendly variable names.

    Parameters
    ----------
    cut_points_dict : dict
        Mapping {feature_name: list_of_cut_points} defining the binning
        structure for each variable.

    Attributes
    ----------
    cut_points_dict : dict
        Stores the cut points provided at initialization.
    """
    
    def __init__(self, cut_points_dict):
        self.cut_points_dict = cut_points_dict

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X.index)

        for col, cuts in self.cut_points_dict.items():
            bins = [-np.inf] + cuts + [np.inf]
            labels = [f"{col}_bin_{i}" for i in range(len(bins)-1)]
            X_binned = pd.cut(X[col], bins=bins, labels=labels)

            # One-hot encoding
            dummies = pd.get_dummies(X_binned, prefix="", prefix_sep="")
            out = pd.concat([out, dummies], axis=1)

        return out