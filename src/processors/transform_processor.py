from typing import Any, Dict, List, Union, Callable, Optional
import pandas as pd
import numpy as np
from .base_processor import BaseProcessor

class TransformProcessor(BaseProcessor):
    """
    数据转换处理器，处理特征工程、数据类型转换、聚合等操作
    """
    def process(self, data_model: Any, **kwargs) -> pd.DataFrame:
        """
        执行数据转换
        
        Args:
            data_model: DataModel实例
            **kwargs: 转换参数，支持：
                - select_columns (list): 选择的列
                - drop_columns (list): 要删除的列
                - apply_funcs (dict): 应用函数，格式为 {'column': func}
                - astype (dict): 类型转换，格式为 {'column': dtype}
                - groupby (dict): 分组配置，包含：
                    - columns: 分组列
                    - agg: 聚合配置
                - one_hot (list): 需要one-hot编码的列
                - bins (dict): 数值分箱配置，格式为 {'column': num_bins}
                - normalize (list/dict): 标准化配置
                - encode_categorical (list): 需要标签编码的列
                
        Returns:
            pd.DataFrame: 转换后的数据
            
        Examples:
            >>> processor = TransformProcessor()
            >>> df = processor.process(data_model,
            ...     select_columns=['age', 'income'],
            ...     apply_funcs={'age': lambda x: x + 1},
            ...     groupby={
            ...         'columns': ['category'],
            ...         'agg': {'amount': 'sum'}
            ...     }
            ... )
        """
        df = data_model.get_data()
        
        # 选择列
        if 'select_columns' in kwargs:
            columns = [col for col in kwargs['select_columns'] if col in df.columns]
            if columns:
                df = df[columns]
        
        # 删除列
        if 'drop_columns' in kwargs:
            columns_to_drop = [col for col in kwargs['drop_columns'] if col in df.columns]
            if columns_to_drop:
                df = df.drop(columns=columns_to_drop)
        
        # 应用函数
        if 'apply_funcs' in kwargs:
            for column, func in kwargs['apply_funcs'].items():
                if column in df.columns:
                    df[column] = df[column].apply(func)
        
        # 类型转换
        if 'astype' in kwargs:
            for column, dtype in kwargs['astype'].items():
                if column in df.columns:
                    try:
                        df[column] = df[column].astype(dtype)
                    except Exception as e:
                        raise ValueError(f"列 '{column}' 类型转换失败: {str(e)}")
        
        # 分组聚合
        if 'groupby' in kwargs:
            groupby_config = kwargs['groupby']
            if isinstance(groupby_config, dict):
                columns = groupby_config.get('columns', [])
                agg = groupby_config.get('agg', {})
                if columns and agg:
                    df = df.groupby(columns).agg(agg).reset_index()
        
        # One-Hot编码
        if 'one_hot' in kwargs:
            columns = [col for col in kwargs['one_hot'] if col in df.columns]
            if columns:
                encoded = pd.get_dummies(df[columns], prefix=columns)
                df = pd.concat([df.drop(columns=columns), encoded], axis=1)
        
        # 数值分箱
        if 'bins' in kwargs:
            for column, num_bins in kwargs['bins'].items():
                if column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
                    df[f'{column}_binned'] = pd.qcut(df[column], q=num_bins, labels=False)
        
        # 标准化/归一化
        if 'normalize' in kwargs:
            norm_config = kwargs['normalize']
            if isinstance(norm_config, list):
                columns = [col for col in norm_config if col in df.columns]
                if columns:
                    df = df.copy()
                    df.loc[:, columns] = (df[columns] - df[columns].mean()) / df[columns].std()
            elif isinstance(norm_config, dict):
                for column, method in norm_config.items():
                    if column not in df.columns:
                        continue
                    df = df.copy()
                    if method == 'minmax':
                        df.loc[:, column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
                    elif method == 'standard':
                        df.loc[:, column] = (df[column] - df[column].mean()) / df[column].std()
        
        # 类别编码
        if 'encode_categorical' in kwargs:
            columns = [col for col in kwargs['encode_categorical'] if col in df.columns]
            if columns:
                from sklearn.preprocessing import LabelEncoder
                for column in columns:
                    le = LabelEncoder()
                    df = df.copy()
                    df.loc[:, column] = le.fit_transform(df[column].astype(str))
        
        # 更新数据
        data_model.set_data(df)
        return df
    
    def create_time_features(self, data_model: Any, date_column: str) -> pd.DataFrame:
        """
        创建时间特征
        
        Args:
            data_model: DataModel实例
            date_column: 日期列名
            
        Returns:
            pd.DataFrame: 添加时间特征后的数据
        """
        df = data_model.get_data()
        if date_column not in df.columns:
            raise ValueError(f"列 '{date_column}' 不存在")
            
        try:
            df[date_column] = pd.to_datetime(df[date_column])
        except Exception as e:
            raise ValueError(f"日期转换失败: {str(e)}")
            
        df[f'{date_column}_year'] = df[date_column].dt.year
        df[f'{date_column}_month'] = df[date_column].dt.month
        df[f'{date_column}_day'] = df[date_column].dt.day
        df[f'{date_column}_dayofweek'] = df[date_column].dt.dayofweek
        df[f'{date_column}_quarter'] = df[date_column].dt.quarter
        df[f'{date_column}_is_weekend'] = df[date_column].dt.dayofweek.isin([5, 6]).astype(int)
        
        data_model.set_data(df)
        return df
    
    def create_polynomial_features(self, data_model: Any, columns: List[str], 
                                 degree: int = 2) -> pd.DataFrame:
        """
        创建多项式特征
        
        Args:
            data_model: DataModel实例
            columns: 要处理的列
            degree: 多项式次数
            
        Returns:
            pd.DataFrame: 添加多项式特征后的数据
        """
        df = data_model.get_data()
        columns = [col for col in columns if col in df.columns]
        
        if not columns:
            raise ValueError("未找到指定的列")
            
        from sklearn.preprocessing import PolynomialFeatures
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        poly_features = poly.fit_transform(df[columns])
        
        feature_names = poly.get_feature_names_out(columns)
        poly_df = pd.DataFrame(poly_features, columns=feature_names, index=df.index)
        
        # 只添加新的多项式特征列
        new_features = poly_df.iloc[:, len(columns):]
        df = pd.concat([df, new_features], axis=1)
        
        data_model.set_data(df)
        return df
