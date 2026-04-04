from sklearn.tree import DecisionTreeRegressor

def tree_binning(x, y, min_leaf_pct=0.05, max_depth=3):
    """Discretization through regression tree
    - Supervised method.
    - The tree automatically chooses the best cut points.
    - The min_leaf_pct parameter ensures bins are sufficiently large.
    - Very effective at capturing non-linearities.
    Parameters
    ----------
    x : array-like, shape (n_samples,)
        Input data to be binned.
    y : array-like, shape (n_samples,)
        Target variable.
    min_leaf_pct : float, optional (default=0.05)
        Minimum percentage of samples required in each leaf.
    max_depth : int, optional (default=3)
        Maximum depth of the tree.
    Returns
    -------
    cut_points : list
        List of cut points determined by the regression tree.
    """
    
    n = len(x)
    min_samples_leaf = int(n * min_leaf_pct)

    tree = DecisionTreeRegressor(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf
    )
    tree.fit(x.reshape(-1,1), y)

    thresholds = tree.tree_.threshold
    cut_points = sorted([t for t in thresholds if t != -2])
    return cut_points