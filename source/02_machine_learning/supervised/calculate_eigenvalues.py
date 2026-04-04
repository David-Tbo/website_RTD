import numpy as np

def calculate_eigenvalues(df):
    """
    Calcule les valeurs propres, le condition number et fournit un diagnostic textuel
    sur la colinéarité (faible / modérée / forte / sévère).
    """

    # Matrice de corrélation
    corr_matrix = df.corr().fillna(0)

    # Valeurs propres
    eigenvalues = np.linalg.eigvals(corr_matrix)

    # On garde les valeurs propres positives pour éviter les divisions instables
    positive_eigen = eigenvalues[eigenvalues > 1e-12]

    if len(positive_eigen) == 0:
        condition_number = np.inf
    else:
        condition_number = positive_eigen.max() / positive_eigen.min()

    # Diagnostic basé sur les seuils classiques
    if condition_number < 10:
        diagnostic = "Faible colinéarité: pas de problème de colinéarité"
    elif condition_number < 30:
        diagnostic = "Colinéarité modérée: à surveiller, mais acceptable"
    elif condition_number < 100:
        diagnostic = "Forte colinéarité: risque réel d'instabilité des coefficients"
    else:
        diagnostic = "Colinéarité sévère (quasi-singularité: régression peu fiable)"

    return eigenvalues, condition_number, diagnostic