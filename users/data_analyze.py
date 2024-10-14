import pandas as pd
class Stat_Methods:
    def __init__(self, dataframe):
        self.dataframe = dataframe
    def null_count(self):
        data=self.dataframe.isnull().sum()
        return data.to_frame().T
    def info(self):
        col_names = self.dataframe.columns.tolist()
        data_types = self.dataframe.dtypes.to_dict()
        dict1={}
        Dtype=[]
        Count=[]
        for a,b in data_types.items():
            Dtype.append(b)
        for a in col_names:
            Count.append(self.dataframe[a].notnull().sum())
        dict1['columns']=col_names
        dict1['datatype']=Dtype
        dict1['not_null_count']=Count
        dict1=pd.DataFrame(dict1)
        return dict1
    
    def description(self):
        return self.dataframe.describe()
    def describe_obj(self):
        return self.dataframe.describe(include=['object'])
    
    def sort_data(self,col_nm):
        return self.dataframe.sort_values(by=col_nm)
        
    def see_null_data(self):
        return self.dataframe[self.dataframe.isnull().any(axis=1)]
    
    def unique_values(self,col_nm):
        unique_val = self.dataframe[col_nm].value_counts()
        return unique_val.to_frame().T
    
    def size_data(self):
        data=self.dataframe.shape
        data=pd.DataFrame({'rows':data[0],'columns':data[1]},index=['count'])
        return data

class Descriptive:
    def __init__(self,dataframe):
        self.dataframe = dataframe
    def describe(self):
        return self.dataframe.describe()
    def describe_obj(self):
        return self.dataframe.describe(include=['object'])
    def unique_count(self):
        unique_counts = self.dataframe.nunique()
        return unique_counts.to_frame(name='Unique Count')
    def correlation_matrix(self):
        numeric_df = self.dataframe.select_dtypes(include=['number'])
        correlation_matrix = numeric_df.corr()
        correlation_matrix=correlation_matrix.round(2)
        return correlation_matrix
    def unique_values(self,col_nm):
        unique_val = self.dataframe[col_nm].value_counts()
        return unique_val.to_frame().T
    def size_data(self):
        data=self.dataframe.shape
        data=pd.DataFrame({'rows':data[0],'columns':data[1]},index=['count'])
        return data
    def info(self):
        col_names = self.dataframe.columns.tolist()
        data_types = self.dataframe.dtypes.to_dict()
        dict1={}
        data_type=[]
        Count=[]
        for a,b in data_types.items():
            data_type.append(b)
        for a in col_names:
            Count.append(self.dataframe[a].notnull().sum())
        dict1['columns']=col_names
        dict1['datatype']=data_type
        dict1['not_null_count']=Count
        dict1=pd.DataFrame(dict1)
        return dict1
