import pandas as pd
from scipy.stats import pointbiserialr

# Correlation Point-Biserial
def calculate_point_biserial(df, numeric_vars, dummy_vars):
    """
    Calcule la corrélation point-biserial entre des variables numériques et des variables binaires.

    Paramètres :
    - df (DataFrame) : DataFrame contenant les données.
    - numeric_vars (list) : Liste des variables numériques.
    - dummy_vars (list) : Liste des variables binaires.

    Retourne :
    - DataFrame : Matrice des corrélations point-biserial.
    """
    point_biserial_results = pd.DataFrame(index=numeric_vars, columns=dummy_vars)
    for num_var in numeric_vars:
        for dummy_var in dummy_vars:
            if num_var not in df.columns or dummy_var not in df.columns:
                raise ValueError(f"Variable introuvable dans le DataFrame : {num_var} ou {dummy_var}.")
            corr, _ = pointbiserialr(df[num_var], df[dummy_var])
            point_biserial_results.loc[num_var, dummy_var] = corr
    return point_biserial_results