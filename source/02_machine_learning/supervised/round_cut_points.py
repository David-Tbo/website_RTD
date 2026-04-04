def round_cut_points(cuts, digits=0):
    """
    Rounds each cut-point in a list.
    - ignores None
    - ignores empty lists
    - converts numpy types to Python floats
    Parameters
    ----------
    cuts : list or None
        List of cut-points to be rounded.
    digits : int, optional (default=0)
        Number of decimal places to round to.
    Returns
    -------
    rounded_cuts : list or None
        List of rounded cut-points, or None if input is None.
    """
    
    if cuts is None:
        return None
    if len(cuts) == 0:
        return cuts
    
    return [round(float(c), digits) for c in cuts]