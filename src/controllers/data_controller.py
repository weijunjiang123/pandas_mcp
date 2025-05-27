import pandas as pd
from typing import Dict, Any, Optional
from ..models.data_model import DataModel

class DataController:
    """
    数据控制器，负责协调数据操作和处理器管理
    """
    def __init__(self):
        """
        初始化数据控制器
        """
        self.data_model = DataModel()
        self.processors = {}
        self._processor_results = {}
    
    def load_data(self, source: Any, json_kwargs: Dict = None, **kwargs) -> 'DataController':
        """
        从不同来源加载数据
        
        Args:
            source: 数据源，可以是文件路径、DataFrame对象或JSON字符串
            json_kwargs: JSON特定的加载参数，支持：
                - orient: JSON数据的格式('split'/'records'/'index'/'columns'/'values'/'table')
                - typ: 返回的对象类型('frame'/'series')
                - convert_dates: 是否转换日期
                - convert_axes: 是否转换轴标签
                - encoding: 文件编码
                - lines: 是否按行读取JSON
                - chunksize: 分块读取的大小
                - nrows: 读取的行数
            **kwargs: 加载数据时的额外参数
            
        Returns:
            DataController: 当前实例，支持链式调用
            
        Raises:
            ValueError: 当文件格式不支持时
            TypeError: 当数据源类型不支持时
            JSONDecodeError: 当JSON解析失败时
        """
        json_kwargs = json_kwargs or {}
        
        if isinstance(source, str):
            try:
                if source.endswith('.csv'):
                    df = pd.read_csv(source, **kwargs)
                elif source.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(source, **kwargs)
                elif source.endswith('.json'):
                    df = pd.read_json(source, **{**kwargs, **json_kwargs})
                elif source.endswith('.parquet'):
                    df = pd.read_parquet(source, **kwargs)
                elif source.endswith('.pickle'):
                    df = pd.read_pickle(source, **kwargs)
                else:
                    # 尝试解析为JSON字符串
                    try:
                        df = pd.read_json(source, **{**kwargs, **json_kwargs})
                    except Exception:
                        raise ValueError(f"不支持的文件格式或无效的JSON字符串: {source}")
            except Exception as e:
                raise ValueError(f"数据加载失败: {str(e)}")
        elif isinstance(source, pd.DataFrame):
            df = source.copy()
        elif isinstance(source, (dict, list)):
            # 支持字典和列表类型的JSON数据
            try:
                df = pd.DataFrame(source)
            except Exception as e:
                raise ValueError(f"无法将数据转换为DataFrame: {str(e)}")
        else:
            raise TypeError(f"不支持的数据源类型: {type(source)}")
            
        self.data_model.set_data(df)
        return self
    
    def save_data(self, path: str, **kwargs) -> None:
        """
        保存数据到文件
        
        Args:
            path: 保存路径
            **kwargs: 保存时的额外参数
            
        Raises:
            ValueError: 当文件格式不支持时
        """
        df = self.data_model.get_data()
        
        if path.endswith('.csv'):
            df.to_csv(path, **kwargs)
        elif path.endswith(('.xls', '.xlsx')):
            df.to_excel(path, **kwargs)
        elif path.endswith('.json'):
            df.to_json(path, **kwargs)
        elif path.endswith('.parquet'):
            df.to_parquet(path, **kwargs)
        elif path.endswith('.pickle'):
            df.to_pickle(path, **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {path}")
    
    def register_processor(self, name: str, processor: Any) -> 'DataController':
        """
        注册数据处理器
        
        Args:
            name: 处理器名称
            processor: 处理器实例
            
        Returns:
            DataController: 当前实例，支持链式调用
        """
        self.processors[name] = processor
        return self
    
    def run_process(self, process_name: str, store_result: bool = True, **kwargs) -> Any:
        """
        执行数据处理
        
        Args:
            process_name: 处理器名称
            store_result: 是否存储处理结果
            **kwargs: 处理器的参数
            
        Returns:
            处理结果
            
        Raises:
            ValueError: 当处理器未注册时
        """
        if process_name not in self.processors:
            raise ValueError(f"处理器 {process_name} 未注册")
            
        processor = self.processors[process_name]
        result = processor.process(self.data_model, **kwargs)
        
        if store_result:
            self._processor_results[process_name] = result
            
        return result
    
    def get_process_result(self, process_name: str) -> Optional[Any]:
        """
        获取处理结果
        
        Args:
            process_name: 处理器名称
            
        Returns:
            处理结果，如果不存在则返回None
        """
        return self._processor_results.get(process_name)
    
    def get_data(self) -> pd.DataFrame:
        """
        获取当前数据
        
        Returns:
            pd.DataFrame: 当前的DataFrame对象
        """
        return self.data_model.get_data()
    
    def get_info(self) -> Dict:
        """
        获取数据信息
        
        Returns:
            Dict: 数据基本信息
        """
        return self.data_model.get_info()
