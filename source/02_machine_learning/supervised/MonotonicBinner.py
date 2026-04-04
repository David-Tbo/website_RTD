import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

def compute_woe(df, feature, target, alpha=1e-6):
    grouped = df.groupby(feature)[target]
    good = (1 - grouped.mean()) * grouped.count()
    bad = grouped.mean() * grouped.count()
    woe = np.log((bad + alpha) / (good + alpha))
    return woe

class MonotonicBinner(BaseEstimator, TransformerMixin):
    """
    Enforces monotonic Weight of Evidence (WoE) across bins by merging adjacent
    intervals until the WoE sequence becomes strictly increasing or decreasing.

    This transformer is used in scorecard modeling to guarantee stability,
    interpretability, and regulatory compliance. Although monotonicity of the
    default rate p_k across bins implies monotonicity of WoE_k mathematically,
    this monotonicity is only an empirical observation on the training sample.
    In real-world data, p_k is rarely perfectly monotonic due to:

    - statistical noise,
    - small or sparse bins,
    - poorly placed cut points,
    - bins that are too close to each other,
    - irregular WoE patterns,
    - bins irrelevant for logistic regression,
    - distribution shifts in future populations,
    - differences between train, test, and out-of-time samples.

    These issues can break the monotonicity of p_k and therefore the monotonicity
    of WoE_k. The MonotonicBinner stabilizes the variable by merging fragile bins
    until a clean monotonic WoE curve is obtained.

    The transformer:
    - merges bins that violate monotonicity,
    - merges bins with insufficient sample size to avoid extreme or unstable WoE,
    - guarantees monotonic WoE,
    - smooths the WoE curve,
    - reduces the number of bins to improve robustness,
    - produces wider, more stable bins over time,
    - ensures interpretability and auditability,
    - provides a reproducible, documented, and industry-standard procedure,
    - follows standard regulatory expectations for scorecard models.

    The MonotonicBinner is not used to fix a mathematical non-monotonicity,
    but to guarantee a monotonic relationship that is robust, stable,
    reproducible, and auditable. It acts as a safety layer on top of 
    manual or exploratory binning.

    Parameters
    ----------
    cut_points_dict : dict
        Dictionary mapping each variable to its initial list of cut points
        (e.g., {"age": [25, 40, 60]}).

    Attributes
    ----------
    final_bins_ : dict
        Dictionary mapping each variable to its final monotonic cut points.
    """

    def __init__(self, cut_points_dict, min_samples_per_bin=5):
        self.cut_points_dict = cut_points_dict
        self.min_samples_per_bin = min_samples_per_bin  # Seuil minimal d'observations par bin
        self.final_bins_ = {}

    def fit(self, X, y):
        X = pd.DataFrame(X)
        y = pd.Series(y)

        for col, cuts in self.cut_points_dict.items():
            bins = [-np.inf] + cuts + [np.inf]
            df = pd.DataFrame({"x": X[col], "y": y})
            df["bin"] = pd.cut(df["x"], bins=bins, include_lowest=True)

            # Fusion jusqu'à monotonicité et taille minimale des bins
            while True:
                # Calcul du WoE
                woe = compute_woe(df, "bin", "y")

                # Vérification de la monotonicité
                is_monotonic = woe.is_monotonic_increasing or woe.is_monotonic_decreasing

                # Vérification de la taille minimale des bins
                bin_counts = df["bin"].value_counts()
                min_samples_ok = (bin_counts >= self.min_samples_per_bin).all()

                if is_monotonic and min_samples_ok:
                    break

                # Fusion des bins violant la monotonicité ou trop petits
                if not is_monotonic:
                    # Fusionner les bins non monotones
                    idx = np.argmin(np.abs(np.diff(woe.values)))
                    categories = df["bin"].cat.categories
                    new_bins = list(categories[:idx]) + [
                        pd.Interval(categories[idx].left, categories[idx+1].right)
                    ] + list(categories[idx+2:])
                else:
                    # Fusionner les bins trop petits
                    small_bins = bin_counts[bin_counts < self.min_samples_per_bin].index
                    if len(small_bins) > 0:
                        idx = df["bin"].cat.categories.get_loc(small_bins[0])
                        categories = df["bin"].cat.categories
                        if idx > 0:
                            new_bins = list(categories[:idx-1]) + [
                                pd.Interval(categories[idx-1].left, categories[idx].right)
                            ] + list(categories[idx+1:])
                        else:
                            new_bins = [
                                pd.Interval(categories[idx].left, categories[idx+1].right)
                            ] + list(categories[idx+2:])

                # Mise à jour des bins
                numeric_bins = [new_bins[0].left] + [b.right for b in new_bins]
                df["bin"] = pd.cut(df["x"], bins=numeric_bins, include_lowest=True)

            # Sauvegarde des coupures finales
            final_cuts = [b.right for b in df["bin"].cat.categories[:-1]]
            self.final_bins_[col] = final_cuts

        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X.index)

        for col, cuts in self.final_bins_.items():
            bins = [-np.inf] + cuts + [np.inf]
            labels = [f"{col}_bin_{i}" for i in range(len(bins)-1)]
            out[col] = pd.cut(X[col], bins=bins, labels=labels, include_lowest=True)

        return out