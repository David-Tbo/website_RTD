from statsmodels.stats.outliers_influence import variance_inflation_factor
import pandas as pd
import numpy as np

def calculate_gvif(dataframe: pd.DataFrame,
                   categorical_groups: dict) -> pd.DataFrame:
    """
    Calcule le GVIF pour les variables catégorielles (groupes de dummies)
    et le VIF pour les variables continues.

    Paramètres
    ----------
    dataframe : pd.DataFrame
        DataFrame contenant toutes les variables explicatives (continues + dummies).
    categorical_groups : dict
        Dictionnaire {nom_variable_catégorielle : [liste des colonnes dummies]}
        Exemple : {"color": ["color_red", "color_blue", "color_green"]}

    Retour
    ------
    pd.DataFrame
        Tableau contenant VIF ou GVIF^(1/(2*df)) selon le type de variable.
    """

    # Copie + ajout de constante
    df = dataframe.copy()
    df["const"] = 1

    # Liste des colonnes
    cols = df.columns.tolist()

    results = []

    # Pré-calcul des VIF bruts pour toutes les colonnes
    vif_raw = {}
    for i, col in enumerate(cols):
        try:
            vif_raw[col] = variance_inflation_factor(df.values, i)
        except Exception:
            vif_raw[col] = np.nan  # Cas de colinéarité parfaite ou colonne constante

    # Traitement des variables catégorielles
    for cat_var, dummies in categorical_groups.items():
        # Vérification
        for d in dummies:
            if d not in df.columns:
                raise ValueError(f"Dummy manquante : {d}")

        # Degrés de liberté = nombre de dummies
        df_cat = len(dummies)

        # GVIF = produit des VIF des dummies
        gvif = np.prod([vif_raw[d] for d in dummies if not np.isnan(vif_raw[d])])

        # Ajustement GVIF^(1/(2*df))
        gvif_adj = gvif ** (1 / (2 * df_cat))

        results.append([cat_var, gvif_adj])

    # Traitement des variables continues
    continuous_vars = [
        c for c in dataframe.columns
        if all(c not in dummies for dummies in categorical_groups.values())
    ]

    for var in continuous_vars:
        results.append([var, vif_raw[var]])

    # Conversion en DataFrame
    out = pd.DataFrame(results, columns=["Variable", "GVIF_adj"])

    return out