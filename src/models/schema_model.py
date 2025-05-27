import pandas as pd
from typing import Dict, List, Optional, Union

class SchemaModel:
    """
    数据结构模型，负责数据结构定义和验证
    """
    def __init__(self, schema: Optional[Dict] = None):
        """
        初始化模式模型
        
        Args:
            schema (Dict, optional): 数据结构定义，格式为:
                {
                    'column_name': {
                        'type': str/int/float/etc,
                        'required': bool,
                        'unique': bool,
                        'range': (min, max),  # 可选
                        'values': list,  # 可选，允许的值列表
                        'regex': str,  # 可选，正则表达式模式
                    }
                }
        """
        self.schema = schema or {}
    
    def set_schema(self, schema: Dict) -> None:
        """
        设置数据结构定义
        
        Args:
            schema (Dict): 数据结构定义
        """
        self.schema = schema
    
    def validate(self, data_model) -> Dict[str, List[str]]:
        """
        验证数据是否符合schema定义
        
        Args:
            data_model: DataModel实例
            
        Returns:
            Dict[str, List[str]]: 验证结果，键为列名，值为错误信息列表
        """
        df = data_model.get_data()
        errors = {}
        
        for col_name, rules in self.schema.items():
            col_errors = []
            
            # 检查必需列是否存在
            if rules.get('required', False) and col_name not in df.columns:
                col_errors.append(f"必需的列 '{col_name}' 不存在")
                errors[col_name] = col_errors
                continue
            
            if col_name in df.columns:
                # 检查数据类型
                expected_type = rules.get('type')
                if expected_type:
                    try:
                        df[col_name].astype(expected_type)
                    except:
                        col_errors.append(f"列 '{col_name}' 包含无效的 {expected_type.__name__} 类型数据")
                
                # 检查唯一性
                if rules.get('unique', False) and not df[col_name].is_unique:
                    col_errors.append(f"列 '{col_name}' 包含重复值")
                
                # 检查值范围
                if 'range' in rules:
                    min_val, max_val = rules['range']
                    invalid_range = df[col_name][(df[col_name] < min_val) | (df[col_name] > max_val)]
                    if not invalid_range.empty:
                        col_errors.append(f"列 '{col_name}' 包含超出范围 [{min_val}, {max_val}] 的值")
                
                # 检查允许的值
                if 'values' in rules:
                    invalid_values = df[col_name][~df[col_name].isin(rules['values'])]
                    if not invalid_values.empty:
                        col_errors.append(f"列 '{col_name}' 包含不允许的值")
                
                # 检查正则表达式模式
                if 'regex' in rules and df[col_name].dtype == 'object':
                    import re
                    pattern = re.compile(rules['regex'])
                    invalid_pattern = df[col_name][~df[col_name].str.match(pattern)]
                    if not invalid_pattern.empty:
                        col_errors.append(f"列 '{col_name}' 包含不匹配正则表达式 '{rules['regex']}' 的值")
            
            if col_errors:
                errors[col_name] = col_errors
        
        return errors
    
    def infer_schema(self, data_model) -> Dict:
        """
        从数据推断schema定义
        
        Args:
            data_model: DataModel实例
            
        Returns:
            Dict: 推断的schema定义
        """
        df = data_model.get_data()
        inferred_schema = {}
        
        for column in df.columns:
            column_info = {
                'type': df[column].dtype,
                'required': True,  # 默认所有列都是必需的
                'unique': df[column].is_unique,
            }
            
            # 对数值类型列推断范围
            if pd.api.types.is_numeric_dtype(df[column]):
                column_info['range'] = (float(df[column].min()), float(df[column].max()))
            
            # 对分类数据推断可能的值
            elif pd.api.types.is_categorical_dtype(df[column]) or df[column].nunique() / len(df) < 0.1:
                column_info['values'] = list(df[column].unique())
            
            inferred_schema[column] = column_info
        
        return inferred_schema
    
    def get_schema(self) -> Dict:
        """
        获取当前的schema定义
        
        Returns:
            Dict: 当前的schema定义
        """
        return self.schema
