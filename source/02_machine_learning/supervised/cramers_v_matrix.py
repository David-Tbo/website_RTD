import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import cramers_v

def cramers_v_matrix(df, categorical_columns):
    """
    Calculate a symmetric Cramer's V matrix for a list of categorical columns.
    """
    n = len(categorical_columns)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):  # moitié supérieure uniquement
            v = cramers_v(df[categorical_columns[i]], df[categorical_columns[j]])
            matrix[i, j] = v
            matrix[j, i] = v  # symétrie

    # Conversion en DataFrame
    cramersv_df = pd.DataFrame(matrix, 
                               index=categorical_columns, 
                               columns=categorical_columns)

    return cramersv_df