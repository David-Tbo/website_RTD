#!/usr/bin/env python
# coding: utf-8

# # **Scorecard: Reject Inference**  

# > **Author**: David Thébault.  
# > **Date**: February 8, 2026.
# > 
# > **Objective**:  
# This notebook aims to provide a **comprehensive use cas of the logistic regression** to build a performing scorecard for diabete predictions.

# ## Packages & functions

# In[5]:


import sys
sys.executable


# In[8]:


# The libraries imports
import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# ## Load the Dataset

# We will use the diabetes dataset to show how to perform logistic regression in Python.

# In[12]:


# Load the dataset
data_path = '/Users/davidtbo/Library/Mobile Documents/com~apple~CloudDocs/data/external'
file_path = os.path.join(data_path, 'german_credit.csv')

if not os.path.exists(file_path):
    raise FileNotFoundError(f"Fichier introuvable : {file_path}")

df = pd.read_csv(file_path)

# Standardize column names
df.columns = df.columns.str.lower()

# Drop duplicates
df = df.drop_duplicates()

df.head().transpose()


# ## Exploratory Data Analysis

# In[13]:


# Quick diagnostic
print(df.info())


# In[14]:


# Quick missing values diagnostic
print(df.isna().mean())


# Analyse the distribution of each variable

# In[15]:


print(df.describe(include='all').to_string())


# Duration and amount are highly correlated, we will keep only one of them (amount) for the modeling phase.

# In[ ]:


import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Initialisation du générateur aléatoire pour la reproductibilité
np.random.seed(42)

# 1. PRÉPARATION DU "OLD SCORE"
# On suppose que df est déjà chargé avec les colonnes duration, installment_commitment, age
features_old = ['duration', 'installment_commitment', 'age']

# Mapping de la cible historique (good=0, bad=1)
df['target'] = df['class'].map({'good': 0, 'bad': 1})

# Entraînement du modèle logistique simple
old_model = LogisticRegression()
old_model.fit(df[features_old], df['target'])

# Calcul des probabilités et transformation en score (0 à 1000)
df['old_proba'] = old_model.predict_proba(df[features_old])[:, 1]
df['old_score'] = (1 - df['old_proba']) * 1000

# 2. LOGIQUE DE SEGMENTATION MUTUELLEMENT EXCLUSIVE (LOAN_CLASS)
def segment_loans(row):
    # Priorité 1 : Business Rules (Rejected)
    # Exemple : Durée trop longue ou âge trop avancé
    if row['duration'] > 48 or row['age'] > 75 or row['job'] == 'unemployed':
        return 'Rejected: Rule-based'

    # Priorité 2 : Score (Rejected) - Uniquement si les règles sont OK
    if row['old_score'] < 400:
        return 'Rejected: Score-only'

    # Priorité 3 : Comportement client (Accepted but not financed)
    if np.random.rand() < 0.08:
        return 'Accepted: No Follow-up'

    # Priorité 4 : Données manquantes/Seniorité (Accepted but not financed)
    if row['residence_since'] == 1 and np.random.rand() < 0.10:
        return 'Accepted: Missing Outcome'

    # Par défaut : Accepté pour le dataset de développement/validation
    return 'Accepted: Dev/Val'

df['loan_class'] = df.apply(segment_loans, axis=1)

# Split du bloc Dev/Val (70/30)
dev_indices = df[df['loan_class'] == 'Accepted: Dev/Val'].index
train_idx, val_idx = train_test_split(dev_indices, test_size=0.3, random_state=42)

df.loc[train_idx, 'loan_class'] = 'Accepted: Development'
df.loc[val_idx, 'loan_class'] = 'Accepted: Validation'

# 3. CRÉATION DES COLONNES final_decision ET top_financed
# Correspondance basée sur votre matrice métier
class_mapping = {
    'Accepted: Development':     {'decision': 'Accepted', 'financed': 1},
    'Accepted: Validation':      {'decision': 'Accepted', 'financed': 1},
    'Accepted: Missing Outcome': {'decision': 'Accepted', 'financed': 0},
    'Accepted: No Follow-up':    {'decision': 'Accepted', 'financed': 0},
    'Rejected: Score-only':      {'decision': 'Rejected', 'financed': 0},
    'Rejected: Rule-based':      {'decision': 'Rejected', 'financed': 0}
}

df['final_decision'] = df['loan_class'].map(lambda x: class_mapping[x]['decision'])
df['top_financed'] = df['loan_class'].map(lambda x: class_mapping[x]['financed'])

# Vérification de la cohérence de la base
summary = df.groupby(['loan_class', 'final_decision', 'top_financed']).size().reset_index(name='Count')
print(summary)


# In[71]:


# Sélection des variables pour le nouveau modèle (plus riche que l'ancien)
# On ajoute des variables comportementales et patrimoniales
features_new = ['duration', 'installment_commitment', 'age', 'residence_since', 'existing_credits']

# Entraînement sur le dataset de développement uniquement
dev_data = df[df['loan_class'] == 'Accepted: Development']
new_model = LogisticRegression()
new_model.fit(dev_data[features_new], dev_data['target'])

# Calcul du nouveau score pour TOUTE la base (0 à 1000)
df['new_proba'] = new_model.predict_proba(df[features_new])[:, 1]
df['new_score'] = (1 - df['new_proba']) * 1000


# In[89]:


NEW_CUTOFF = 550

def simulate_new_decision(row):
    # RÈGLE : Rule-based rejections restent REJETÉES quoi qu'il arrive
    if row['loan_class'] == 'Rejected: Rule-based':
        return 'Rejected (Rule-based)'

    # RÈGLE : Pour les autres (Score-only rejections et Acceptés actuels)
    if row['new_score'] >= NEW_CUTOFF:
        # Si le nouveau score passe le cut-off, on simule l'acceptation et le financement
        return 'Accepted & Financed (Simulated)'
    else:
        return 'Rejected (Score)'

df['new_decision'] = df.apply(simulate_new_decision, axis=1)

# Création de la variable binaire de financement simulé pour les calculs futurs
df['new_top_financed'] = df['new_decision'].apply(lambda x: 1 if x == 'Accepted & Financed (Simulated)' else 0)


# In[90]:


# Regardons les statistiques du nouveau score sur les "Score-only rejections"
stats_rejets = df[df['loan_class'] == 'Rejected: Score-only']['new_score'].describe()
print("Distribution du New Score sur les refusés :")
print(stats_rejets)

# Testons un cut-off plus haut, par exemple le 3ème quartile (top 25%)
new_cutoff_suggested = stats_rejets['75%']
print(f"\nSi on fixe le cut-off à {new_cutoff_suggested:.0f}, on n'acceptera que 25% des anciens refusés.")


# In[97]:


# Focus sur les "Score-only rejections" pour voir combien sont "récupérés"
recovered = df[df['loan_class'] == 'Rejected: Score-only']['new_decision'].value_counts(normalize=True)
print("Impact sur les Score-only rejections :")
print(recovered)


# In[96]:


# On calcule le score qui sépare les 70% moins bons des 30% meilleurs chez les refusés
new_cutoff_optimal = df[df['loan_class'] == 'Rejected: Score-only']['new_score'].quantile(0.70)

print(f"Nouveau Cut-off suggéré : {new_cutoff_optimal:.0f}")

# On relance la simulation avec ce seuil
def logic_refined(row):
    if row['loan_class'] == 'Rejected: Rule-based':
        return 'Rejected (Rule-based)'
    if row['new_score'] >= new_cutoff_optimal:
        return 'Accepted & Financed (Simulated)'
    return 'Rejected (Score)'

df['new_decision'] = df.apply(logic_refined, axis=1)

# Vérification du nouvel impact
impact = df[df['loan_class'] == 'Rejected: Score-only']['new_decision'].value_counts(normalize=True)
print("\nNouvel impact sur les Score-only rejections :")
print(impact)


# In[92]:


def simulate_impact(df, potential_cutoff):
    # Simulation selon vos règles 6.3
    def logic(row):
        if row['loan_class'] == 'Rejected: Rule-based':
            return 0 # Toujours rejeté
        if row['new_score'] >= potential_cutoff:
            return 1 # Simulé financé
        return 0 # Rejeté par le nouveau score

    return df.apply(logic, axis=1)

# Test sur plusieurs scénarios de Cut-off
cutoffs = [400, 450, 500, 550]
for c in cutoffs:
    simulated_financed = simulate_impact(df, c)
    acc_rate = simulated_financed.mean()
    print(f"Scénario Cut-off {c}: Taux d'acceptation simulé = {acc_rate:.1%}")


# In[98]:


# On fixe un cut-off qui n'accepte pas 100% des rejets pour avoir du relief
# Ici, on prend le percentile 60 (on garde les 40% meilleurs des Score-only rejections)
NEW_CUTOFF = df[df['loan_class'] == 'Rejected: Score-only']['new_score'].quantile(0.60)

# Simulation de la nouvelle décision (Règle 6.3)
df['new_top_financed'] = np.where(
    (df['loan_class'] != 'Rejected: Rule-based') & (df['new_score'] >= NEW_CUTOFF), 
    1, 0
)

# Identification des Swaps
def identify_swaps(row):
    if row['top_financed'] == 1 and row['new_top_financed'] == 0:
        return 'A: Discarded (Swap-out)'
    if row['top_financed'] == 0 and row['new_top_financed'] == 1:
        return 'B: Added (Swap-in)'
    return 'No Change'

df['swap_type'] = df.apply(identify_swaps, axis=1)

# Affichage des volumes
print("Répartition des changements de décision :")
print(df['swap_type'].value_counts())


# In[99]:


total_apps = len(df)

# 1. Acceptance Rates
old_acc_rate = df['top_financed'].mean()
new_acc_rate = df['new_top_financed'].mean()

# 2. Decision Impact
pop_a_rate = (df['swap_type'] == 'A: Discarded (Swap-out)').sum() / total_apps
pop_b_rate = (df['swap_type'] == 'B: Added (Swap-in)').sum() / total_apps
decision_impact = pop_a_rate + pop_b_rate

# 3. Risk Rates (Initialisation avec les données connues pour l'instant)
# Note : Pour les populations A et B, le vrai Risk Rate viendra de la Reject Inference
old_risk_rate = df[df['top_financed'] == 1]['target'].mean()

print(f"\n--- Données pour votre Global Switch Table ---")
print(f"Previous Acceptance Rate : {old_acc_rate:.1%}")
print(f"New Acceptance Rate      : {new_acc_rate:.1%}")
print(f"Evolution                : {new_acc_rate - old_acc_rate:+.1%}")
print(f"----------------------------------------------")
print(f"Population A (Discarded) : {pop_a_rate:.1%}")
print(f"Population B (Added)     : {pop_b_rate:.1%}")
print(f"Decision Impact (A+B)    : {decision_impact:.1%}")


# In[ ]:


# 4. Reject inference


# In[ ]:


## Initialization


# In[51]:


# We hide the 'target' for all applications except Development and Validation
df['known_target'] = df['target']
df.loc[~df['loan_class'].isin(['Accepted: Development', 'Accepted: Validation']), 'known_target'] = np.nan


# In[53]:


df.known_target.value_counts(dropna=False)


# In[54]:


# --- METHOD 1: HARD CUT-OFF ---
df['target_hard'] = df['known_target']
df.loc[df['loan_class'].str.contains('Rejected'), 'target_hard'] = 1 # All the rejected applications are Bad


# In[55]:


df['target_hard'].value_counts(dropna=False)


# In[56]:


# --- METHOD 2: FUZZY AUGMENTATION ---
# Train on the known accepted applications
inf_model = LogisticRegression().fit(df[df['known_target'].notna()][features_old], df[df['known_target'].notna()]['known_target'])
df['prob_inf'] = inf_model.predict_proba(df[features_old])[:, 1]
# The fuzzy target is the probability itself for unknowns
df['target_fuzzy'] = df['known_target'].fillna(df['prob_inf'])


# In[68]:


# df['target_fuzzy'].value_counts(dropna=False)


# In[57]:


# --- METHOD 3: PARCELING (VOTRE CHAPITRE 6.5) ---
# 1. Creation of 20 brackets score on the accepted applications
df['bracket'] = pd.qcut(df['old_score'], 20, labels=False, duplicates='drop')
stats = df[df['known_target'].notna()].groupby('bracket')['known_target'].mean()
# 2. Assignation of the risk rate of the rejected brackets on the same bracket
df['target_parceling'] = df['known_target']
for b in stats.index:
    mask = (df['bracket'] == b) & (df['known_target'].isna())
    df.loc[mask, 'target_parceling'] = stats[b]


# In[58]:


# 5. GÉNÉRATION DE LA CUT-OFF TABLE (EXTRAIT)
def get_cutoff_table(target_col):
    table = df.sort_values('old_score', ascending=False)
    table['cum_apps'] = np.arange(1, len(table) + 1)
    table['cum_bads'] = table[target_col].cumsum()
    table['acc_rate'] = table['cum_apps'] / len(table)
    table['risk_rate'] = table['cum_bads'] / table['cum_apps']
    return table[['old_score', 'acc_rate', 'risk_rate']].iloc[::100] # Un point tous les 100 dossiers

print("--- Comparaison des Risques Simulés (Cut-off à 80% d'Acceptation) ---")
for m in ['target_hard', 'target_fuzzy', 'target_parceling']:
    res = get_cutoff_table(m)
    risk = res[res['acc_rate'] >= 0.8].iloc[0]['risk_rate']
    print(f"Méthode {m:18} : Taux de risque estimé = {risk:.2%}")


# # END
