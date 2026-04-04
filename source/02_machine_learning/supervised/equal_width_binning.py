import numpy as np

def equal_width_binning(x, bins=5):
    """Equal width binning
    - Constant width intervals.
    - Simple but sensitive to outliers.
    Parameters
    ----------
    x : array-like, shape (n_samples,)
        Input data to be binned.
    bins : int, optional (default=5)
        Number of bins to create.
    Returns
    -------
    bin_edges : list
        List of bin edges.
    """

    return list(np.linspace(min(x), max(x), bins+1))