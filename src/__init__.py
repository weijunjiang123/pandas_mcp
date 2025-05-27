"""
pandas_mcp - 一个基于MCP架构的pandas扩展框架
"""

from .models.data_model import DataModel
from .models.schema_model import SchemaModel
from .controllers.data_controller import DataController
from .controllers.pipeline_controller import PipelineController
from .processors.base_processor import BaseProcessor
from .processors.clean_processor import CleanProcessor
from .processors.transform_processor import TransformProcessor
from .processors.analysis_processor import AnalysisProcessor
from .processors.visualization_processor import VisualizationProcessor

__all__ = [
    'DataModel',
    'SchemaModel',
    'DataController',
    'PipelineController',
    'BaseProcessor',
    'CleanProcessor',
    'TransformProcessor',
    'AnalysisProcessor',
    'VisualizationProcessor'
]

__version__ = '0.1.0'
