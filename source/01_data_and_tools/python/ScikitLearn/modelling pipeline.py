# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import pandas as pd
import numpy as np
import pickle

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,LabelEncoder, OneHotEncoder, OrdinalEncoder,KBinsDiscretizer
from sklearn.feature_selection import SelectKBest, chi2, SelectFromModel
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV,RandomizedSearchCV,StratifiedKFold
from sklearn.compose import make_column_transformer
import time
from sklearn.metrics import roc_auc_score,roc_curve,precision_recall_curve, auc
import matplotlib.pyplot as plt
#models

from sklearn.linear_model import LogisticRegression,\
                                 RidgeClassifier,\
                                 SGDClassifier,\
                                 PassiveAggressiveClassifier
                                 
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA,\
                                          QuadraticDiscriminantAnalysis as QDA


from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier,\
                             BaggingClassifier,\
                             RandomForestClassifier,\
                             ExtraTreesClassifier,\
                             GradientBoostingClassifier

#load datasets
datamart_path="C:/Users/X196406/OneDrive - GROUP DIGITAL WORKPLACE/Documents/Score/SGMA"
with open(datamart_path+"/prepared_dataset.pkl", 'rb') as file:
    X,y,LIST_VAR_CHAR,LIST_VAR_NUM=pickle.load(file)

already_discretized_cols=[x for x in X.columns if (x[-3:]=='SPR') | (x[-3:]=='SCL')]
X=X.drop(already_discretized_cols,axis=1)
LIST_VAR_CHAR=np.intersect1d(LIST_VAR_CHAR,X.columns)
LIST_VAR_NUM=np.intersect1d(LIST_VAR_NUM,X.columns)

X.shape,y.shape

#split data into training and test datsets  
seed=2020
X_train, X_test, y_train,y_test=train_test_split(X,y, train_size=0.75,stratify=y,random_state=seed)

X.STRATEGY_VERSION_NB[(X.STRATEGY_VERSION_NB=='0095') | (X.STRATEGY_VERSION_NB=='0091')]='0099'


#Models

models=[
          {'name':'LogisticRegression','type':'Linear','model':LogisticRegression(),'hyp_param_grid':{'model__penalty':['l1','l2'],'model__C':[0.1,1.0,10]}},
          {'name':'RidgeClassifier','type':'Linear','model':RidgeClassifier(),'hyp_param_grid':{'model__alpha':[0.1,1.0,10],'model__fit_intercept':[True,False]}},
          {'name':'SGDClassifier','type':'Linear','model':SGDClassifier(),'hyp_param_grid':{}},
          {'name':'PassiveAggressiveClassifier','type':'Linear','model':PassiveAggressiveClassifier(),'hyp_param_grid':{}},
          {'name':'LDA','type':'Linear','model':LDA(),'hyp_param_grid':{}},
          {'name':'QDA','type':'Quadratic','model':QDA(),'hyp_param_grid':{}},
          {'name':'KNN','type':'NonLinear','model':KNeighborsClassifier(),'hyp_param_grid':{'model__n_neighbors':[5,10,15,20,25],'model__p':[1,2]}},
          {'name':'SVC','model':SVC(),'type':'NonLinear','hyp_param_grid':{'model__C':[0.1,1,10]}},
          {'name':'GaussianNB','type':'NonLinear','model':GaussianNB(),'hyp_param_grid':{}},
          {'name':'AdaBoost','type':'Ensemble','model':AdaBoostClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200],'model__learning_rate':[0.5,0.7,1]}},
          {'name':'BaggingClassifier','type':'Ensemble','model':BaggingClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200]}},
          {'name':'RandomForest','type':'Ensemble','model':RandomForestClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200],'model__max_depth':[5,10,20,30,None],'model__min_samples_split':[2,5,10,20,100],'model__min_samples_leaf':[2,5,10],'model__max_features':['log2','sqrt',None]}},
          {'name':'ExtraTreesClassifier','type':'Ensemble','model':ExtraTreesClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200],'model__max_depth':[5,10,20,30,None],'model__min_samples_split':[2,5,10,20,100],'model__min_samples_leaf':[2,5,10],'model__max_features':['log2','sqrt',None]}},
          {'name':'GBClassifer','type':'Ensemble','model':GradientBoostingClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200],'model__max_depth':[5,10,20,30,None],'model__min_samples_split':[2,5,10,20,100],'model__min_samples_leaf':[1,2,5,10],'model__max_features':['log2','sqrt',None]}}
      ]





#feature importance

pipe0=make_column_transformer((make_pipeline(SimpleImputer(strategy='most_frequent'),OrdinalEncoder()),LIST_VAR_CHAR),
                                  (make_pipeline(SimpleImputer(strategy='median'),KBinsDiscretizer(encode='ordinal')),LIST_VAR_NUM))    
    
#Chi2_scores
    
Selector=SelectKBest(chi2,k='all' )
Selector.fit(pipe0.fit_transform(X_train),y_train)
chi2_scores=pd.Series(Selector.scores_,index=LIST_VAR_CHAR.tolist()+LIST_VAR_NUM.tolist()).sort_values(ascending=False)
fig, ax=plt.subplots(figsize=(12,10))
chi2_scores.plot(kind='bar',ax=ax)

#using ColumnTransformer
train_report=pd.DataFrame()

models=[
#          {'name':'LogisticRegression','type':'Linear','model':LogisticRegression(),'hyp_param_grid':{'model__penalty':['l1','l2'],'model__C':[0.1,1.0,10]}},
#          {'name':'LDA','type':'Linear','model':LDA(),'hyp_param_grid':{}},
#          {'name':'QDA','type':'Quadratic','model':QDA(),'hyp_param_grid':{}},
#          {'name':'KNN','type':'NonLinear','model':KNeighborsClassifier(),'hyp_param_grid':{'model__n_neighbors':[5,10,15,20,25],'model__p':[1,2]}}
          {'name':'RandomForest','type':'Ensemble','model':RandomForestClassifier(),'hyp_param_grid':{'model__n_estimators':[50,100,150,200],'model__max_depth':[5,10,20,30,None],'model__min_samples_split':[2,5,10,20,100],'model__min_samples_leaf':[2,5,10],'model__max_features':['log2','sqrt',None]}}


      ]


c=0

for m in models:
    
    t_start=time.time()
    c+=1
    print('Training model %i / %i :'%(c,len(models)) + m['name'])
    
    pipe0=make_column_transformer((make_pipeline(SimpleImputer(strategy='most_frequent'),OrdinalEncoder( )),LIST_VAR_CHAR),
                                  (make_pipeline(SimpleImputer(strategy='median'),KBinsDiscretizer(encode='ordinal')),LIST_VAR_NUM))    
      
    
    pipe=Pipeline([('step1',pipe0),
                   ('selector',SelectKBest(chi2,k=10 )),
                   ('OneHotencoder',OneHotEncoder(sparse=False,handle_unknown='ignore')),
                   ('Scaler',StandardScaler()),
                   ('model',m['model'])
                 ])

    hyper_params={'step1__pipeline-2__simpleimputer__strategy':['mean','median'],'selector__k':list(range(6,14)),'step1__pipeline-2__kbinsdiscretizer__strategy':['quantile','uniform']}
    hyper_params.update(m['hyp_param_grid'])
    #grid=GridSearchCV(pipe,param_grid=hyper_params,cv=StratifiedKFold(3), scoring='average_precision', verbose=10, n_jobs=2)
    grid=RandomizedSearchCV(pipe,param_distributions=hyper_params,n_iter=500, cv=StratifiedKFold(3), scoring='average_precision', verbose=10, n_jobs=2,random_state=seed)
    
    from sklearn.utils import parallel_backend
    with parallel_backend('threading'):
        grid.fit(X_train,y_train)
    t_end=time.time()
    training_time=round((t_end-t_start)/60,2)
    cv_scores_best_model=[v[grid.best_index_] for k,v in grid.cv_results_.items() if k[:5] =='split']
    train_report=train_report.append({'model':m['name'],
                                      'type':m['type'],
                                      'scoring':'roc_auc',
                                      'best_score':grid.best_score_,
                                      'cv_scores_best_estimator':cv_scores_best_model,
                                      'tr_time_min':training_time,
                                      'best_params':grid.best_params_,
                                      'best_estimator':grid.best_estimator_},ignore_index=True)
    
train_report.sort_values(by=['best_score'],ascending=False,inplace=True)



#Assess best models on test dataset using roc curve
test_auc=[]
for i in [0,1,2,4,5]:
    m=train_report.loc[i,'best_estimator']
    model_name=train_report.loc[i,'model']
    y_pred=m.predict_proba(X_test)
    test_auc.append((model_name,roc_auc_score(y_test,y_pred[:,1])))
    tpr,fpr,threholds=roc_curve(y_test,y_pred[:,1])
    plt.plot(fpr,tpr, linestyle='-',label=model_name)
test_auc=sorted(test_auc,key=lambda x:x[1],reverse=True)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()

#Assess best models on test dataset using precision_recall curve
precision_recall_auc=[]
for i in [0,1,2]:
    m=train_report.iloc[i,0]
    model_name=train_report.iloc[i,4]
    y_pred=m.predict_proba(X_test)
    precision,recall,threholds=precision_recall_curve(y_test,y_pred[:,1])
    precision_recall_auc.append((model_name,auc(recall,precision)))
    plt.plot(recall,precision, linestyle='-',label=model_name)
precision_recall_auc=sorted(precision_recall_auc,key=lambda x:x[1],reverse=True)

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.legend()




















class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self,features_to_select):
        self.features=features_to_select
     
    def fit(self,X,y=None):
        return(self)
    
    def transform(self,X,y=None):
        return(X[self.features].values)

class OrdinalEncoderBis(BaseEstimator, TransformerMixin):  
    
    def fit(self,X, y=None):
        if type(X)==pd.DataFrame:
            X=X.values
        labEncoders=[]
        for f in range(X.shape[1]):
            labelencoder=LabelEncoder()
            labEncoders.append(labelencoder.fit(X[:,f].tolist()))
            self.Encoders=labEncoders
        return(self)
    
    def transform(self, X,y=None):
        
        if type(X)==pd.DataFrame:
            X=X.values
        for f in range(X.shape[1]):
            if f==0 :
                transformed_X=np.array([self.Encoders[f].transform(X[:,f]).tolist()]).T
            else:
                transformed_X=np.insert(transformed_X,transformed_X.shape[1],self.Encoders[f].transform(X[:,f]),axis=1)
        return transformed_X
# Pipe 1
cat_pipe=Pipeline([('feature_selector',FeatureSelector(cat_vars)),
                   ('cat_imputer',SimpleImputer(strategy='most_frequent')),
                   ('Ordinal_encoder', OrdinalEncoder())                                     
                   ])


    

num_pipe=Pipeline([('feature_selector',FeatureSelector(num_vars)),
                   ('num_imputer',SimpleImputer(strategy='median')),
                   ('discitizer_Ordinal_encoder', KBinsDiscretizer(encode='ordinal'))                                     
                   ])
    
union_pipe=FeatureUnion( transformer_list=[('categorical_pipe',cat_pipe),('numerical_pipe',num_pipe)])
       
pipe2=Pipeline([('feature_selector',FeatureSelector(cat_vars)),
                ('cat_imputer',SimpleImputer(strategy='most_frequent')),
                ('Ordinal_encoder', OrdinalEncoder()) ,
                ('selector',SelectKBest(chi2,k=2 )),
                ('OneHotencoder',OneHotEncoder(sparse=False)),
                ('RFC',RandomForestClassifier(n_estimators=100))
                ])

hyper_params={'selector__k':[1,2]}

my_grid=GridSearchCV(pipe2,param_grid=hyper_params,cv=3, scoring='roc_auc')

my_grid.fit(X_train,y_train)

    

# Pipe 2
cat_pipe=Pipeline([('feature_selector',FeatureSelector(cat_vars)),
                   ('cat_imputer',SimpleImputer(strategy='most_frequent')),
                   ('Ordinal_encoder', OrdinalEncoder())                                     
                   ])


    

num_pipe=Pipeline([('feature_selector',FeatureSelector(num_vars)),
                   ('num_imputer',SimpleImputer(strategy='median'))
                   ])
    
union_pipe=FeatureUnion( transformer_list=[('categorical_pipe',cat_pipe),('numerical_pipe',num_pipe)])
 

      
pipe2=Pipeline([('union_pipe',union_pipe),
                ('selector',SelectFromModel()),
                ('OneHotencoder',OneHotEncoder(sparse=False)),
                ('RFC',RandomForestClassifier(n_estimators=100))
                ])

    
    
    
    
    
  