# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 10:01:01 2020

@author: X196406
"""

import numpy as np
import pandas as pd
import pickle
from sas7bdat import SAS7BDAT
import seaborn as sns
import matplotlib.pyplot as plt

pd.__version__

datamart_path="C:/Users/X196406/OneDrive - GROUP DIGITAL WORKPLACE/Documents/Score/SGMA"
vars_meta=pd.read_csv(datamart_path+"/vars_metadata_sgma.csv",delimiter=";",encoding='utf8')

#score_data=SAS7BDAT(datamart_path+"/pna_cli_datamart_soft.sas7bdat").to_data_frame()
#
#
#with open(datamart_path+"/score_datamart.pkl", 'wb') as score_datamart_file:
#    pickle.dump(score_data, score_datamart_file)



with open(datamart_path+"/score_datamart.pkl", 'rb') as score_datamart_file:
    datamart=pickle.load(score_datamart_file)
datamart.shape
datamart.describe()


#some values are zero_length charcaters so convert them into Na
datamart=datamart.applymap(lambda t: np.NAN if str(t).strip()=='' else t)

datamart.shape

LIST_VAR_NUM=list(vars_meta.loc[(vars_meta['COLTYPE']=='num') & (vars_meta['VARS_CATEGORY']=='POTENTIAL_PREDICTOR') ,'COLNAME'])
LIST_VAR_CHAR=list(vars_meta.loc[(vars_meta['COLTYPE']=='char') & (vars_meta['VARS_CATEGORY']=='POTENTIAL_PREDICTOR') ,'COLNAME'])
BINNED_VARS=[x for x in LIST_VAR_CHAR if x[:2]=='X_']
LIST_VAR_CHAR=[x for x in LIST_VAR_CHAR if x[:2]!='X_']
QUAL='VHRMAX_12'

#graphics qual

fig, ax=plt.subplots( nrows=2, figsize=(12,10),     )

datamart['QUAL']=datamart[QUAL].apply(lambda x: 'AVAILABLE QUAL' if pd.notna(x) else 'MISSING QUAL')
pd.crosstab(datamart.TIMEUNIT_APPLICATION_QUARTER,datamart.QUAL).plot(kind='bar',stacked=True,ax=ax[0])
pd.crosstab(datamart.TIMEUNIT_APPLICATION_QUARTER,datamart[QUAL]).plot(kind='bar',stacked=True,ax=ax[1], alpha=0.5)
pd.crosstab(datamart.TIMEUNIT_APPLICATION_QUARTER,datamart[QUAL],normalize='index')[1].plot(ax=ax[1].twinx(),color="black",marker='.', linestyle='dashed')
ax[0].set_title('Nombre de demandes QUAL/MISSING QUAL')
ax[1].set_title('Nombre de demandes good/bad + taux de mauvais')

# discard old observations

#cumulative number of applications 
cumul_dem=pd.crosstab(datamart.TIMEUNIT_APPLICATION_QUARTER,datamart[QUAL]).sort_index(ascending=False).cumsum() 
cumul_dem['total']=cumul_dem[0]+cumul_dem[1]
print(cumul_dem)

#data to be kept : 2015Q1==>2019Q4 : 65 893 applications (64 531 good and 1362 bad)

datamart2=datamart.loc[datamart.TIMEUNIT_APPLICATION_QUARTER>='2015Q1',LIST_VAR_NUM+LIST_VAR_CHAR+[QUAL]]
datamart2.shape



# divide the dataset into 2 parts : with and without qual
data_Nqual=datamart2[datamart[QUAL].isna()] #data with missing qual
data_qual=datamart2[datamart[QUAL].notna()] #data with available qual
data_qual.shape
data_qual[QUAL].value_counts(normalize=True)

#keep only potential predictors, drop technical variables
data_qual=data_qual[LIST_VAR_NUM+LIST_VAR_CHAR+[QUAL]]
data_qual.shape
#missing data analysis 
def report(df):  
    missing_val_report=pd.DataFrame()
    missing_val_report['Dtypes']=df.dtypes
    missing_val_report['NB_RECORDS']=df.isna().count()
    missing_val_report['NB_NULL']=df.isna().sum()
    missing_val_report['PROP_NULL']=missing_val_report['NB_NULL']/missing_val_report['NB_RECORDS']
    missing_val_report['MODE']=df.mode().iloc[0].T
    missing_val_report['FREQ_MODE']=df.apply(lambda x: (sum(x==x.mode().iloc[0]) if len(x.mode() )>0 else np.NaN))
    missing_val_report['FREQ_MODE']=missing_val_report['FREQ_MODE']/df.count()
    missing_val_report.sort_values(    by=['PROP_NULL','FREQ_MODE'], ascending=[False,False], inplace=True   )
    return(missing_val_report)

missing_data_report=report(data_qual)
print(missing_data_report)

#we keep only variables with enough available data and with acceptable variablility

to_keep=missing_data_report[(missing_data_report['PROP_NULL']<0.05) & (missing_data_report['FREQ_MODE']<=0.90)]
to_keep_vars=list(to_keep.index)

print(missing_data_report.Dtypes.value_counts()) #Initially
print(to_keep.Dtypes.value_counts())             # after discarding variables

data_qual2=data_qual[to_keep_vars+[QUAL]]
LIST_VAR_NUM2=np.intersect1d(LIST_VAR_NUM,data_qual2.columns)
LIST_VAR_CHAR2=np.intersect1d(LIST_VAR_CHAR,data_qual2.columns)

print(data_qual2.shape)

#drop variables with too many modalities
modality_count=data_qual2[LIST_VAR_CHAR2].apply(lambda x: len(x.unique())).sort_values()
too_many_modalities_vars= list(modality_count[modality_count>10].index)

data_qual3=data_qual2.drop(too_many_modalities_vars,axis=1)#warning : AE_SECTACTIV and AE_PROF are dropped at this step
data_qual3['AE_SECTACTIV']=data_qual3.AE_SECTACTIV_SCL #replace AE_SECTACTIV by its discretized version, already exits in the dataset

#drop duplicated columns
data_qual3=data_qual3.drop(['EMP_AGE','EMP_AGE_','ENAV_TOT_REV1'],axis=1)

data_qual3.shape
LIST_VAR_CHAR3=np.intersect1d(LIST_VAR_CHAR,data_qual3.columns)
LIST_VAR_NUM3=LIST_VAR_NUM2

X.STRATEGY_VERSION_NB[(X.STRATEGY_VERSION_NB=='0095') | (X.STRATEGY_VERSION_NB=='0091')]='0099'
#check if there is missing values after discaring variables
report(data_qual3).iloc[:,range(4)].sort_values(by='NB_NULL', ascending=False)


#training and test datasets

X=data_qual3.drop(QUAL,axis=1)
y=data_qual3[QUAL]
X.shape,y.shape

with open(datamart_path+"/prepared_dataset.pkl", 'wb') as file:
    pickle.dump((X,y,LIST_VAR_CHAR3,LIST_VAR_NUM2),file)
    







#feature selection:

data_qual2[LIST_VAR_CHAR2].apply(lambda x: len(x.unique())).sort_values()
too_many_modalities_vars=['AE_SECTACTIV','AE_PROF','AS_NBIMPMAX','AE_PROFDET']
LIST_VAR_CHAR3=list(set(LIST_VAR_CHAR2)-set(too_many_modalities_vars)) 
LIST_VAR_NUM3=LIST_VAR_NUM2
qual_data3=qual_data2.drop(too_many_modalities_vars,axis=1)
print(qual_data3.shape)

#binning numeric features
binned_num_data=qual_data3[LIST_VAR_NUM3].apply(lambda x:pd.qcut(x,5,duplicates='drop'))

#dataset with only categorical features
qual_data3_categ=pd.concat([qual_data3[LIST_VAR_CHAR3],binned_num_data,qual_data3[['HR_12']]],axis=1)

feature_names=qual_data3_categ.drop('HR_12',axis=1).columns


X=qual_data2.drop('HR_12',axis=1).values
y=qual_data2.HR_12.values
X.shape
y.shape


from sklearn.feature_selection import chi2, SelectKBest
selector=SelectKBest(chi2)



qual_data.shape


