import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

def cramers_v(x, y):
    """
    Calculate Cramer's V statistic for categorical-categorical association
    with bias correction (Bergsma & Wicher).
    """
    # Crosstab
    confusion_matrix = pd.crosstab(x, y)

    # Si tableau dégénéré (1 ligne ou 1 colonne)
    if confusion_matrix.shape[0] < 2 or confusion_matrix.shape[1] < 2:
        return 0.0

    # Chi2
    chi2, _, _, _ = chi2_contingency(confusion_matrix)

    # Taille de l'échantillon
    n = confusion_matrix.sum().sum()
    if n == 0:
        return np.nan

    # Phi2
    phi2 = chi2 / n
    r, k = confusion_matrix.shape

    # Correction du biais
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    r_corr = r - ((r - 1)**2) / (n - 1)
    k_corr = k - ((k - 1)**2) / (n - 1)

    denom = min((k_corr - 1), (r_corr - 1))
    if denom <= 0:
        return np.nan

    return np.sqrt(phi2corr / denom)