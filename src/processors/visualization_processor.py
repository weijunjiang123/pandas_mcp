from typing import Any, Dict, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from .base_processor import BaseProcessor

class VisualizationProcessor(BaseProcessor):
    """
    数据可视化处理器，使用matplotlib和seaborn创建各类图表
    """
    def __init__(self):
        """
        初始化可视化处理器
        """
        # 设置默认样式
        plt.style.use('seaborn-v0_8')
        self.default_figsize = (10, 6)
    
    def process(self, data_model: Any, **kwargs) -> Dict[str, plt.Figure]:
        """
        执行数据可视化
        
        Args:
            data_model: DataModel实例
            **kwargs: 可视化参数，支持：
                - plots (list): 要创建的图表列表，每个元素是包含以下键的字典：
                    - type: 图表类型
                    - x: x轴数据
                    - y: y轴数据（可选）
                    - kind: 图表具体类型
                    - title: 标题
                    - figsize: 图表大小
                    - other_params: 其他参数
                
        Returns:
            Dict[str, plt.Figure]: 图表字典，键为图表标题
            
        Examples:
            >>> processor = VisualizationProcessor()
            >>> figs = processor.process(data_model,
            ...     plots=[
            ...         {
            ...             'type': 'distribution',
            ...             'x': 'age',
            ...             'title': 'Age Distribution'
            ...         },
            ...         {
            ...             'type': 'scatter',
            ...             'x': 'age',
            ...             'y': 'income',
            ...             'title': 'Age vs Income'
            ...         }
            ...     ]
            ... )
        """
        df = data_model.get_data()
        figures = {}
        
        for plot_config in kwargs.get('plots', []):
            fig = self._create_plot(df, plot_config)
            if fig:
                title = plot_config.get('title', f"Plot_{len(figures)}")
                figures[title] = fig
        
        return figures
    
    def _create_plot(self, df: pd.DataFrame, config: Dict) -> Optional[plt.Figure]:
        """
        创建单个图表
        
        Args:
            df: DataFrame数据
            config: 图表配置
            
        Returns:
            Optional[plt.Figure]: matplotlib图表对象
        """
        plot_type = config.get('type', '').lower()
        if not plot_type:
            return None
            
        try:
            figsize = config.get('figsize', self.default_figsize)
            fig, ax = plt.subplots(figsize=figsize)
            
            if plot_type == 'distribution':
                self._plot_distribution(df, ax, config)
            elif plot_type == 'scatter':
                self._plot_scatter(df, ax, config)
            elif plot_type == 'line':
                self._plot_line(df, ax, config)
            elif plot_type == 'bar':
                self._plot_bar(df, ax, config)
            elif plot_type == 'box':
                self._plot_box(df, ax, config)
            elif plot_type == 'heatmap':
                self._plot_heatmap(df, ax, config)
            elif plot_type == 'pie':
                self._plot_pie(df, ax, config)
            else:
                plt.close(fig)
                return None
                
            title = config.get('title')
            if title:
                ax.set_title(title)
                
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"创建图表失败: {str(e)}")
            return None
    
    def _plot_distribution(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制分布图"""
        x = config.get('x')
        if x not in df.columns:
            raise ValueError(f"列 '{x}' 不存在")
            
        sns.histplot(data=df, x=x, ax=ax, **config.get('other_params', {}))
        
        if config.get('kde', True):
            sns.kdeplot(data=df, x=x, ax=ax, color='red', **config.get('kde_params', {}))
            
    def _plot_scatter(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制散点图"""
        x, y = config.get('x'), config.get('y')
        if not all([x in df.columns, y in df.columns]):
            raise ValueError("x和y列必须存在")
            
        sns.scatterplot(data=df, x=x, y=y, ax=ax, **config.get('other_params', {}))
        
    def _plot_line(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制线图"""
        x, y = config.get('x'), config.get('y')
        if not all([x in df.columns, y in df.columns]):
            raise ValueError("x和y列必须存在")
            
        sns.lineplot(data=df, x=x, y=y, ax=ax, **config.get('other_params', {}))
        
    def _plot_bar(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制柱状图"""
        x = config.get('x')
        y = config.get('y')
        
        if y is None:  # 单变量柱状图
            df[x].value_counts().plot(kind='bar', ax=ax)
        else:  # 双变量柱状图
            if not all([x in df.columns, y in df.columns]):
                raise ValueError("x和y列必须存在")
            sns.barplot(data=df, x=x, y=y, ax=ax, **config.get('other_params', {}))
        
    def _plot_box(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制箱线图"""
        x = config.get('x')
        y = config.get('y')
        
        if y is None:  # 单变量箱线图
            sns.boxplot(data=df, x=x, ax=ax, **config.get('other_params', {}))
        else:  # 分组箱线图
            if not all([x in df.columns, y in df.columns]):
                raise ValueError("x和y列必须存在")
            sns.boxplot(data=df, x=x, y=y, ax=ax, **config.get('other_params', {}))
        
    def _plot_heatmap(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制热力图"""
        data = df.corr() if config.get('correlation', True) else df
        sns.heatmap(data, ax=ax, annot=True, **config.get('other_params', {}))
        
    def _plot_pie(self, df: pd.DataFrame, ax: plt.Axes, config: Dict) -> None:
        """绘制饼图"""
        column = config.get('x')
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
            
        data = df[column].value_counts()
        ax.pie(data.values, labels=data.index, autopct='%1.1f%%', 
               **config.get('other_params', {}))
    
    def create_subplot_figure(self, data_model: Any, plots: List[Dict], 
                            layout: Tuple[int, int], figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        创建子图组合
        
        Args:
            data_model: DataModel实例
            plots: 图表配置列表
            layout: 子图布局，如(2, 2)表示2行2列
            figsize: 图表大小
            
        Returns:
            plt.Figure: matplotlib图表对象
        """
        df = data_model.get_data()
        rows, cols = layout
        n_plots = len(plots)
        
        if n_plots > rows * cols:
            raise ValueError(f"图表数量({n_plots})超过布局容量({rows*cols})")
            
        fig = plt.figure(figsize=figsize or (cols*6, rows*4))
        
        for i, plot_config in enumerate(plots, 1):
            ax = fig.add_subplot(rows, cols, i)
            try:
                plot_type = plot_config.get('type', '').lower()
                
                if plot_type == 'distribution':
                    self._plot_distribution(df, ax, plot_config)
                elif plot_type == 'scatter':
                    self._plot_scatter(df, ax, plot_config)
                elif plot_type == 'line':
                    self._plot_line(df, ax, plot_config)
                elif plot_type == 'bar':
                    self._plot_bar(df, ax, plot_config)
                elif plot_type == 'box':
                    self._plot_box(df, ax, plot_config)
                elif plot_type == 'heatmap':
                    self._plot_heatmap(df, ax, plot_config)
                elif plot_type == 'pie':
                    self._plot_pie(df, ax, plot_config)
                    
                title = plot_config.get('title')
                if title:
                    ax.set_title(title)
                    
            except Exception as e:
                print(f"创建子图 {i} 失败: {str(e)}")
                
        plt.tight_layout()
        return fig
    
    def save_figures(self, figures: Dict[str, plt.Figure], 
                    directory: str, format: str = 'png', dpi: int = 300) -> None:
        """
        保存图表
        
        Args:
            figures: 图表字典
            directory: 保存目录
            format: 文件格式
            dpi: 分辨率
        """
        import os
        os.makedirs(directory, exist_ok=True)
        
        for title, fig in figures.items():
            filename = f"{title}.{format}"
            path = os.path.join(directory, filename)
            fig.savefig(path, format=format, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
