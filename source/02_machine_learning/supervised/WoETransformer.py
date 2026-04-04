import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

def compute_woe(df, feature, target):
    grouped = df.groupby(feature)[target]
    good = (1 - grouped.mean()) * grouped.count()
    bad = grouped.mean() * grouped.count()
    woe = np.log((bad + 1e-6) / (good + 1e-6))
    return woe

class WoETransformer(BaseEstimator, TransformerMixin):
    """
    Converts categorical bins into Weight of Evidence (WoE) values for use in
    scorecard-style logistic regression models.

    WoE encodes each bin by a log-odds ratio, producing a numeric and
    monotonic representation of the relationship between the feature and the
    target. This transformation stabilizes the variable, improves linearity
    for logistic regression, enhances robustness to population drift, and
    enables interpretability and auditability. WoE is also the foundation for
    score computation and stability metrics such as PSI.

    The transformer:
    - replaces each bin with its WoE value,
    - stores WoE mappings for each feature,
    - produces a clean numeric dataset suitable for logistic regression.

    Without WoE, a model is simply a classical logistic regression; with WoE,
    it becomes a proper scorecard model.

    Attributes
    ----------
    woe_dict_ : dict
        Mapping {feature_name: {bin_label: woe_value}} learned during fitting.
    """

    def __init__(self):
        self.woe_dict_ = {}

    def fit(self, X, y):
        X = pd.DataFrame(X)
        y = pd.Series(y)

        for col in X.columns:
            df = pd.DataFrame({"bin": X[col], "y": y})
            woe = compute_woe(df, "bin", "y")
            self.woe_dict_[col] = woe.to_dict()

        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        for col in X.columns:
            X[col] = X[col].map(self.woe_dict_[col])
        return X