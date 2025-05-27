from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseProcessor(ABC):
    """
    基础处理器抽象类，定义所有处理器的通用接口
    """
    @abstractmethod
    def process(self, data_model: Any, **kwargs) -> Any:
        """
        处理数据的抽象方法
        
        Args:
            data_model: DataModel实例
            **kwargs: 处理参数
            
        Returns:
            处理结果
        """
        pass
    
    def validate_params(self, params: Dict, required_params: Dict) -> None:
        """
        验证处理参数
        
        Args:
            params: 实际传入的参数
            required_params: 必需的参数及其类型
            
        Raises:
            ValueError: 当参数验证失败时
        """
        for param_name, param_type in required_params.items():
            if param_name not in params:
                raise ValueError(f"缺少必需参数: {param_name}")
            if not isinstance(params[param_name], param_type):
                raise ValueError(f"参数 {param_name} 类型错误，应为 {param_type.__name__}")
    
    def get_name(self) -> str:
        """
        获取处理器名称
        
        Returns:
            str: 处理器名称
        """
        return self.__class__.__name__
