import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

def chi_merge(x, y, max_bins=5, min_pvalue=0.05):
    """Chi-square discretization (ChiMerge)
    - Supervised method.  
    - Iteratively merges adjacent intervals while the Chi-square statistic is not statistically significant.
    - Widely used in banking credit scoring."""
    
    df = pd.DataFrame({"x": x, "y": y})
    df = df.sort_values("x")

    # Initial bins: each unique value is its own bin
    bins = [[v] for v in df["x"].unique()]

    def chi2_for_bins(bins):
        # Build contingency table
        groups = []
        for b in bins:
            mask = df["x"].isin(b)
            groups.append(df.loc[mask, "y"].value_counts().reindex([0,1], fill_value=0))
        table = np.array(groups)
        chi2, p, _, _ = chi2_contingency(table)
        return p

    while len(bins) > max_bins:
        p_values = []
        for i in range(len(bins)-1):
            merged = bins[i] + bins[i+1]
            temp_bins = bins[:i] + [merged] + bins[i+1+1:]
            p_values.append((chi2_for_bins(temp_bins), i))

        best_p, idx = max(p_values)
        if best_p < min_pvalue:
            break

        bins[idx] = bins[idx] + bins[idx+1]
        del bins[idx+1]

    cut_points = [max(b) for b in bins[:-1]]
    return cut_points