#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import warnings
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# 1. CHARGEMENT ET NETTOYAGE
data_path = '/Users/davidtbo/Library/Mobile Documents/com~apple~CloudDocs/data/external'
file_path = os.path.join(data_path, 'german_credit.csv')
df = pd.read_csv(file_path)

df.columns = df.columns.str.lower()
df = df.drop_duplicates()
df['target'] = df['class'].map({'good': 0, 'bad': 1})

# 2. GÉNÉRATION DU OLD SCORE (Modèle de référence)
features_old = ['duration', 'installment_commitment', 'age']
old_model = LogisticRegression().fit(df[features_old], df['target'])
df['old_proba'] = old_model.predict_proba(df[features_old])[:, 1]
df['old_score'] = (1 - df['old_proba']) * 1000

# 3. LOGIQUE MÉTIER : LOAN_CLASS, DECISION ET FINANCEMENT
def segment_loans(row):
    # Priorité 1 : Business Rules
    if row['duration'] > 48 or row['age'] > 75:
        return 'rejected: rule-based'
    # Priorité 2 : Score (Old Cut-off à 400)
    if row['old_score'] < 400:
        return 'rejected: score-only'
    # Priorité 3 : Comportement / Seniorité
    if np.random.rand() < 0.08:
        return 'accepted: no follow-up'
    if row['residence_since'] == 1 and np.random.rand() < 0.10:
        return 'accepted: missing outcome'
    return 'accepted: dev/val'

np.random.seed(42)
df['loan_class'] = df.apply(segment_loans, axis=1)

# Split Dev/Val
dev_idx = df[df['loan_class'] == 'accepted: dev/val'].index
train_idx, val_idx = train_test_split(dev_idx, test_size=0.3, random_state=42)
df.loc[train_idx, 'loan_class'] = 'accepted: development'
df.loc[val_idx, 'loan_class'] = 'accepted: validation'

# Mapping Final Decision & Top Financed
class_map = {
    'accepted: development':     {'dec': 'accepted', 'fin': 1},
    'accepted: validation':      {'dec': 'accepted', 'fin': 1},
    'accepted: missing outcome': {'dec': 'accepted', 'fin': 0},
    'accepted: no follow-up':    {'dec': 'accepted', 'fin': 0},
    'rejected: score-only':      {'dec': 'rejected', 'fin': 0},
    'rejected: rule-based':      {'dec': 'rejected', 'fin': 0}
}
df['final_decision'] = df['loan_class'].map(lambda x: class_map[x]['dec'])
df['top_financed'] = df['loan_class'].map(lambda x: class_map[x]['fin'])

# 4. NEW SCORE & SIMULATION (POPULATIONS A & B)
features_new = ['duration', 'installment_commitment', 'age', 'residence_since', 'existing_credits']
dev_data = df[df['loan_class'] == 'accepted: development']
new_model = LogisticRegression().fit(dev_data[features_new], dev_data['target'])
df['new_score'] = (1 - new_model.predict_proba(df[features_new])[:, 1]) * 1000

# Fixation du nouveau Cut-off (Percentile 60 des rejets pour éviter le 100% d'acceptation)
new_cutoff = df[df['loan_class'] == 'rejected: score-only']['new_score'].quantile(0.60)

df['new_top_financed'] = np.where(
    (df['loan_class'] != 'rejected: rule-based') & (df['new_score'] >= new_cutoff), 1, 0
)

# Identification des Swaps (A et B)
df['swap_type'] = 'no change'
df.loc[(df['top_financed'] == 1) & (df['new_top_financed'] == 0), 'swap_type'] = 'a: discarded (swap-out)'
df.loc[(df['top_financed'] == 0) & (df['new_top_financed'] == 1), 'swap_type'] = 'b: added (swap-in)'

# 5. REJECT INFERENCE (PARCELING METHOD)
df['bracket'] = pd.qcut(df['new_score'], 20, labels=False, duplicates='drop')
known_mask = df['loan_class'].isin(['accepted: development', 'accepted: validation'])
df_known = df[known_mask]

# Agrégation par parcelle
parcel_stats = df_known.groupby('bracket')['target'].agg(['mean', 'count']).reset_index()
parcel_stats['log_odds'] = np.log((parcel_stats['mean'] + 0.01) / (1 - parcel_stats['mean'] + 0.01))

# Lissage par régression
x_reg = sm.add_constant(df_known.groupby('bracket')['new_score'].mean().values)
y_reg = parcel_stats['log_odds'].values
inf_model = sm.OLS(y_reg, x_reg).fit()

# Inférence sur toute la base
all_scores = sm.add_constant(df['new_score'].values)
df['inferred_risk'] = 1 / (1 + np.exp(-inf_model.predict(all_scores)))
df['final_target_analysis'] = df['target'].fillna(df['inferred_risk'])

# 6. OUTPUT DES RÉSULTATS (GLOBAL SWITCH TABLE)
print(f"--- Global Switch Table Analysis ---")
print(f"New Cut-off: {new_cutoff:.0f}")
print(f"Risk Pop A (Discarded): {df[df['swap_type'].str.contains('a:')]['final_target_analysis'].mean():.2%}")
print(f"Risk Pop B (Added):     {df[df['swap_type'].str.contains('b:')]['final_target_analysis'].mean():.2%}")