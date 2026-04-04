import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# --- Utility: compute IV ---
def compute_iv(x_binned, y):
    df = pd.DataFrame({"bin": x_binned, "y": y})
    grouped = df.groupby("bin")["y"]
    dist_good = (1 - grouped.mean()) * grouped.count() / len(df)
    dist_bad = grouped.mean() * grouped.count() / len(df)
    iv = ((dist_bad - dist_good) * np.log((dist_bad + 1e-6) / (dist_good + 1e-6))).sum()
    return iv

class DiscretizerSelector(BaseEstimator, TransformerMixin):
    """
    Automatically selects the best discretization method for each continuous
    variable based on Information Value (IV).

    This transformer evaluates several binning strategies, computes the IV
    associated with each discretization, and retains the method and cut points
    that maximize predictive power. It is typically used in scorecard modeling
    to identify the most informative binning before applying monotonic
    constraints and Weight of Evidence (WoE) encoding.

    The selector:
    - tests multiple discretization functions,
    - computes IV for each candidate binning,
    - selects the method with the highest IV,
    - stores the chosen cut points for each variable.

    Note
    ----
    This transformer does not modify the data during `transform`. It only
    identifies and stores the optimal discretization strategy. The actual
    binning is applied later in the pipeline.

    Parameters
    ----------
    methods_dict : dict
        Mapping of method names to functions of the form
        `func(x, y) -> list_of_cut_points`.
        Each function must return a list of numeric cut points.

    max_bins : int, default=5
        Maximum number of bins allowed for any discretization method.

    Attributes
    ----------
    best_methods_ : dict
        Mapping {feature_name: selected_method_name}.

    cut_points_ : dict
        Mapping {feature_name: list_of_selected_cut_points}.
    """

    def __init__(self, methods_dict, max_bins=5):
        """
        methods_dict : dict {method_name: function(x, y) -> cut_points}
        """
        self.methods_dict = methods_dict
        self.max_bins = max_bins
        self.best_methods_ = {}
        self.cut_points_ = {}

    def fit(self, X, y):
        X = pd.DataFrame(X)
        y = pd.Series(y)

        for col in X.columns:
            x = X[col].values
            best_iv = -np.inf
            best_method = None
            best_cut = None

            for name, func in self.methods_dict.items():
                try:
                    cut_points = func(x, y)
                    x_binned = pd.cut(x, bins=[-np.inf] + cut_points + [np.inf])
                    iv = compute_iv(x_binned, y)

                    if iv > best_iv:
                        best_iv = iv
                        best_method = name
                        best_cut = cut_points
                except:
                    continue

            self.best_methods_[col] = best_method
            self.cut_points_[col] = best_cut

        return self

    def transform(self, X):
        return X  # no transformation here, only selection