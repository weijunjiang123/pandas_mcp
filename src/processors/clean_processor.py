from typing import Any, Dict, List, Union, Optional
import pandas as pd
import numpy as np
from .base_processor import BaseProcessor

class CleanProcessor(BaseProcessor):
    """
    数据清洗处理器，处理缺失值、重复值、异常值等
    """
    def process(self, data_model: Any, **kwargs) -> pd.DataFrame:
        """
        执行数据清洗
        
        Args:
            data_model: DataModel实例
            **kwargs: 清洗参数，支持：
                - dropna (bool/dict): 是否删除缺失值，可以是布尔值或参数字典
                - fillna (dict): 填充缺失值的配置，格式为 {'column': value}
                - drop_duplicates (bool/dict): 是否删除重复行，可以是布尔值或参数字典
                - drop_columns (list): 要删除的列名列表
                - rename_columns (dict): 列重命名映射
                - replace_values (dict): 值替换映射，格式为 {'column': {old_value: new_value}}
                - filter_condition (str): 过滤条件表达式
                - value_range (dict): 数值范围过滤，格式为 {'column': (min, max)}
                
        Returns:
            pd.DataFrame: 清洗后的数据
            
        Examples:
            >>> processor = CleanProcessor()
            >>> df = processor.process(data_model,
            ...     dropna={'subset': ['age', 'income']},
            ...     fillna={'name': 'Unknown'},
            ...     drop_duplicates=True,
            ...     rename_columns={'old_name': 'new_name'},
            ...     value_range={'age': (0, 120)}
            ... )
        """
        df = data_model.get_data()
        
        # 处理缺失值
        if 'dropna' in kwargs:
            dropna_args = kwargs['dropna']
            if isinstance(dropna_args, bool) and dropna_args:
                df = df.dropna()
            elif isinstance(dropna_args, dict):
                subset = dropna_args.get('subset')
                if isinstance(subset, (list, tuple)):
                    df = df.dropna(subset=subset)
                else:
                    df = df.dropna(**dropna_args)
        
        if 'fillna' in kwargs:
            fillna_args = kwargs['fillna']
            for column, value in fillna_args.items():
                if column in df.columns:
                    df[column] = df[column].fillna(value)
        
        # 处理重复值
        if 'drop_duplicates' in kwargs:
            dup_args = kwargs['drop_duplicates']
            if isinstance(dup_args, bool):
                if dup_args:
                    df = df.drop_duplicates()
            elif isinstance(dup_args, dict):
                df = df.drop_duplicates(**dup_args)
        
        # 删除列
        if 'drop_columns' in kwargs:
            columns_to_drop = [col for col in kwargs['drop_columns'] if col in df.columns]
            if columns_to_drop:
                df = df.drop(columns=columns_to_drop)
        
        # 重命名列
        if 'rename_columns' in kwargs:
            rename_dict = {old: new for old, new in kwargs['rename_columns'].items() if old in df.columns}
            if rename_dict:
                df = df.rename(columns=rename_dict)
        
        # 替换值
        if 'replace_values' in kwargs:
            for column, replacements in kwargs['replace_values'].items():
                if column in df.columns:
                    df[column] = df[column].replace(replacements)
        
        # 条件过滤
        if 'filter_condition' in kwargs:
            try:
                df = df.query(kwargs['filter_condition'])
            except Exception as e:
                raise ValueError(f"过滤条件无效: {str(e)}")
        
        # 数值范围过滤
        if 'value_range' in kwargs:
            for column, (min_val, max_val) in kwargs['value_range'].items():
                if column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
                    df = df[df[column].between(min_val, max_val)]
        
        # 更新数据
        data_model.set_data(df)
        return df
    
    def detect_outliers(self, data_model: Any, method: str = 'zscore', 
                       columns: Optional[List[str]] = None, threshold: float = 3) -> Dict[str, List[int]]:
        """
        检测异常值
        
        Args:
            data_model: DataModel实例
            method: 检测方法，支持 'zscore', 'iqr'
            columns: 要检测的列，默认为所有数值列
            threshold: 阈值，z-score方法使用
            
        Returns:
            Dict[str, List[int]]: 每列的异常值索引
        """
        df = data_model.get_data()
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        outliers = {}
        for column in columns:
            if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
                continue
                
            if method == 'zscore':
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                outliers[column] = df[z_scores > threshold].index.tolist()
            
            elif method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                outliers[column] = df[
                    (df[column] < Q1 - 1.5 * IQR) | 
                    (df[column] > Q3 + 1.5 * IQR)
                ].index.tolist()
        
        return outliers
    
    def remove_outliers(self, data_model: Any, outliers: Dict[str, List[int]]) -> pd.DataFrame:
        """
        移除异常值
        
        Args:
            data_model: DataModel实例
            outliers: 异常值索引字典
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        df = data_model.get_data()
        all_outliers = set().union(*outliers.values())
        df = df.drop(index=all_outliers)
        data_model.set_data(df)
        return df
