import numpy as np

def tukey_binning(x):
    """Tukey’s fences (IQR-based binning)
    - Unsupervised method.
    - Based on th quartiles to define natural borns.
    - Very robust to outliers.
    - Produce 4-5 typical intervals.
    Parameters
    ----------
    x : array-like, shape (n_samples,)
        Input data to be binned.
    Returns
    -------
    cut_points : list
        List of cut points based on Tukey's fences.
    """
    
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [lower, q1, q3, upper]