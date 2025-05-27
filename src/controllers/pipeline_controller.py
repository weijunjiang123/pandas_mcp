from typing import Dict, List, Any, Tuple
from .data_controller import DataController

class PipelineController:
    """
    流水线控制器，负责管理和执行数据处理流程
    """
    def __init__(self):
        """
        初始化流水线控制器
        """
        self.pipeline = []
        self.data_controller = DataController()
        self._step_results = []
    
    def add_step(self, processor_name: str, **kwargs) -> 'PipelineController':
        """
        添加处理步骤到流水线
        
        Args:
            processor_name: 处理器名称
            **kwargs: 处理器参数
            
        Returns:
            PipelineController: 当前实例，支持链式调用
        """
        self.pipeline.append((processor_name, kwargs))
        return self
    
    def insert_step(self, index: int, processor_name: str, **kwargs) -> 'PipelineController':
        """
        在指定位置插入处理步骤
        
        Args:
            index: 插入位置
            processor_name: 处理器名称
            **kwargs: 处理器参数
            
        Returns:
            PipelineController: 当前实例，支持链式调用
        """
        self.pipeline.insert(index, (processor_name, kwargs))
        return self
    
    def remove_step(self, index: int) -> 'PipelineController':
        """
        移除指定位置的处理步骤
        
        Args:
            index: 步骤索引
            
        Returns:
            PipelineController: 当前实例，支持链式调用
        """
        if 0 <= index < len(self.pipeline):
            self.pipeline.pop(index)
        return self
    
    def clear_pipeline(self) -> 'PipelineController':
        """
        清空流水线
        
        Returns:
            PipelineController: 当前实例，支持链式调用
        """
        self.pipeline = []
        return self
    
    def get_pipeline(self) -> List[Tuple[str, Dict]]:
        """
        获取当前流水线配置
        
        Returns:
            List[Tuple[str, Dict]]: 处理步骤列表
        """
        return self.pipeline.copy()
    
    def run(self, data: Any = None, start_step: int = 0, end_step: int = None) -> List[Any]:
        """
        执行流水线处理
        
        Args:
            data: 输入数据，可以是文件路径或DataFrame对象
            start_step: 起始步骤索引
            end_step: 结束步骤索引（不包含）
            
        Returns:
            List[Any]: 每个步骤的处理结果列表
        """
        if data is not None:
            self.data_controller.load_data(data)
            
        end_step = len(self.pipeline) if end_step is None else end_step
        self._step_results = []
        
        for i, (processor_name, kwargs) in enumerate(self.pipeline[start_step:end_step]):
            try:
                step_index = start_step + i
                result = self.data_controller.run_process(processor_name, **kwargs)
                self._step_results.append({
                    'step': step_index,
                    'processor': processor_name,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                self._step_results.append({
                    'step': step_index,
                    'processor': processor_name,
                    'status': 'error',
                    'error': str(e)
                })
                raise Exception(f"步骤 {step_index} ({processor_name}) 执行失败: {str(e)}")
                
        return self._step_results
    
    def get_results(self) -> List[Dict]:
        """
        获取流水线执行结果
        
        Returns:
            List[Dict]: 处理结果列表
        """
        return self._step_results
    
    def get_step_result(self, step_index: int) -> Dict:
        """
        获取指定步骤的执行结果
        
        Args:
            step_index: 步骤索引
            
        Returns:
            Dict: 步骤执行结果
        """
        if 0 <= step_index < len(self._step_results):
            return self._step_results[step_index]
        raise IndexError(f"步骤索引 {step_index} 超出范围")
    
    def register_processor(self, name: str, processor: Any) -> 'PipelineController':
        """
        注册数据处理器
        
        Args:
            name: 处理器名称
            processor: 处理器实例
            
        Returns:
            PipelineController: 当前实例，支持链式调用
        """
        self.data_controller.register_processor(name, processor)
        return self
    
    def get_data(self) -> Any:
        """
        获取当前数据
        
        Returns:
            当前的DataFrame对象
        """
        return self.data_controller.get_data()
    
    def save_data(self, path: str, **kwargs) -> None:
        """
        保存数据到文件
        
        Args:
            path: 文件路径
            **kwargs: 保存参数
        """
        self.data_controller.save_data(path, **kwargs)
