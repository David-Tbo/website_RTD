import pandas as pd

def equal_freq_binning(x, bins=5):
    """Equal frequency binning (pandas version)
    - Same number of observations per bin.
    - Very stable and robust.
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

    return pd.qcut(x, q=bins, duplicates='drop')