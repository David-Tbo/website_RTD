import numpy as np

def quantile_binning(x, q=4):
    """Quantile (rank / equal-frequency) binning
    - Splits the variable into quantiles (quartiles, quintiles, deciles, etc.).
    - Each bin contains approximately the same number of observations.
    - Widely used in marketing and credit scoring.
    Parameters
    ----------
    x : array-like, shape (n_samples,)
        Input data to be binned.
    q : int, optional (default=4)
        Number of quantiles (e.g., 4 for quartiles).
    Returns
    -------
    bin_edges : list
        List of bin edges.
    """

    return list(np.unique(np.quantile(x, np.linspace(0, 1, q+1))))