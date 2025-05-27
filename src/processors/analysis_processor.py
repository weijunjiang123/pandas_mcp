from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
from sklearn.metrics import *
from .base_processor import BaseProcessor

class AnalysisProcessor(BaseProcessor):
    """
    数据分析处理器，处理统计分析、相关性分析和基础机器学习任务
    """
    def process(self, data_model: Any, **kwargs) -> Dict:
        """
        执行数据分析
        
        Args:
            data_model: DataModel实例
            **kwargs: 分析参数，支持：
                - describe (bool/dict): 是否进行描述性统计
                - corr (bool/dict): 是否进行相关性分析
                - groupby_analysis (dict): 分组分析配置
                - columns (list): 要分析的列，默认全部
                - custom_funcs (dict): 自定义分析函数
                
        Returns:
            Dict: 分析结果
            
        Examples:
            >>> processor = AnalysisProcessor()
            >>> results = processor.process(data_model,
            ...     describe=True,
            ...     corr={'method': 'pearson'},
            ...     groupby_analysis={
            ...         'columns': ['category'],
            ...         'metrics': ['mean', 'sum']
            ...     }
            ... )
        """
        results = {}
        df = data_model.get_data()
        
        # 获取要分析的列
        columns = kwargs.get('columns', df.columns)
        columns = [col for col in columns if col in df.columns]
        
        # 描述性统计
        if kwargs.get('describe'):
            if isinstance(kwargs['describe'], dict):
                results['describe'] = df[columns].describe(**kwargs['describe'])
            else:
                results['describe'] = df[columns].describe()
        
        # 相关性分析
        if kwargs.get('corr'):
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            if isinstance(kwargs['corr'], dict):
                results['correlation'] = df[numeric_cols].corr(**kwargs['corr'])
            else:
                results['correlation'] = df[numeric_cols].corr()
        
        # 分组分析
        if 'groupby_analysis' in kwargs:
            config = kwargs['groupby_analysis']
            groupby_cols = config.get('columns', [])
            metrics = config.get('metrics', ['mean'])
            
            if groupby_cols:
                # 如果指定了numeric_only，只选择数值列
                if config.get('numeric_only', False):
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    columns = [col for col in columns if col in numeric_cols]
                
                grouped = df.groupby(groupby_cols)
                if isinstance(metrics, list):
                    results['groupby'] = grouped[columns].agg(metrics)
                elif isinstance(metrics, dict):
                    results['groupby'] = grouped.agg(metrics)
        
        # 自定义分析函数
        if 'custom_funcs' in kwargs:
            custom_results = {}
            for name, func in kwargs['custom_funcs'].items():
                try:
                    custom_results[name] = func(df[columns])
                except Exception as e:
                    custom_results[name] = f"分析错误: {str(e)}"
            results['custom'] = custom_results
        
        return results
    
    def statistical_tests(self, data_model: Any, test_type: str, **kwargs) -> Dict:
        """
        执行统计检验
        
        Args:
            data_model: DataModel实例
            test_type: 检验类型，支持：
                - ttest: t检验
                - anova: 方差分析
                - chi2: 卡方检验
                - ks: KS检验
            **kwargs: 检验参数
            
        Returns:
            Dict: 检验结果
        """
        from scipy import stats
        df = data_model.get_data()
        results = {}
        
        try:
            if test_type == 'ttest':
                column = kwargs.get('column')
                group_column = kwargs.get('group_column')
                if not all([column, group_column]):
                    raise ValueError("t检验需要指定column和group_column")
                    
                groups = df.groupby(group_column)[column].apply(list)
                if len(groups) != 2:
                    raise ValueError("t检验需要恰好两组数据")
                    
                stat, pvalue = stats.ttest_ind(*groups)
                results = {
                    'statistic': stat,
                    'p_value': pvalue,
                    'test_type': 't-test'
                }
            
            elif test_type == 'anova':
                column = kwargs.get('column')
                group_column = kwargs.get('group_column')
                if not all([column, group_column]):
                    raise ValueError("方差分析需要指定column和group_column")
                    
                groups = df.groupby(group_column)[column].apply(list)
                stat, pvalue = stats.f_oneway(*groups)
                results = {
                    'statistic': stat,
                    'p_value': pvalue,
                    'test_type': 'ANOVA'
                }
            
            elif test_type == 'chi2':
                table = pd.crosstab(
                    df[kwargs.get('column1')],
                    df[kwargs.get('column2')]
                )
                stat, pvalue, dof, expected = stats.chi2_contingency(table)
                results = {
                    'statistic': stat,
                    'p_value': pvalue,
                    'dof': dof,
                    'test_type': 'Chi-square'
                }
            
            elif test_type == 'ks':
                data1 = df[kwargs.get('column1')]
                data2 = df[kwargs.get('column2')]
                stat, pvalue = stats.ks_2samp(data1, data2)
                results = {
                    'statistic': stat,
                    'p_value': pvalue,
                    'test_type': 'Kolmogorov-Smirnov'
                }
            
            else:
                raise ValueError(f"不支持的检验类型: {test_type}")
                
        except Exception as e:
            results = {
                'error': f"检验失败: {str(e)}",
                'test_type': test_type
            }
            
        return results
    
    def train_test_model(self, data_model: Any, model: Any, features: List[str], 
                        target: str, test_size: float = 0.2, 
                        random_state: Optional[int] = None) -> Dict:
        """
        训练和评估机器学习模型
        
        Args:
            data_model: DataModel实例
            model: sklearn模型实例
            features: 特征列
            target: 目标列
            test_size: 测试集比例
            random_state: 随机种子
            
        Returns:
            Dict: 模型训练和评估结果
        """
        from sklearn.model_selection import train_test_split
        
        df = data_model.get_data()
        results = {}
        
        try:
            # 准备数据
            X = df[features]
            y = df[target]
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            
            # 评估结果
            results = {
                'model_type': model.__class__.__name__,
                'feature_importance': dict(zip(features, model.feature_importances_))
                if hasattr(model, 'feature_importances_') else None,
                'metrics': {}
            }
            
            # 根据任务类型计算不同的评估指标
            if len(np.unique(y)) == 2:  # 二分类
                results['metrics'].update({
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred),
                    'recall': recall_score(y_test, y_pred),
                    'f1': f1_score(y_test, y_pred),
                    'auc_roc': roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
                })
            elif len(np.unique(y)) > 2:  # 多分类
                results['metrics'].update({
                    'accuracy': accuracy_score(y_test, y_pred),
                    'macro_f1': f1_score(y_test, y_pred, average='macro'),
                    'weighted_f1': f1_score(y_test, y_pred, average='weighted')
                })
            else:  # 回归
                results['metrics'].update({
                    'mse': mean_squared_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mae': mean_absolute_error(y_test, y_pred),
                    'r2': r2_score(y_test, y_pred)
                })
                
        except Exception as e:
            results = {'error': f"模型训练失败: {str(e)}"}
            
        return results
