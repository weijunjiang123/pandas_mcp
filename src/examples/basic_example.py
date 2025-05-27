import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)


from src.models.data_model import DataModel
from src.models.schema_model import SchemaModel
from src.controllers.data_controller import DataController
from src.controllers.pipeline_controller import PipelineController
from src.processors.clean_processor import CleanProcessor
from src.processors.transform_processor import TransformProcessor
from src.processors.analysis_processor import AnalysisProcessor
from src.processors.visualization_processor import VisualizationProcessor

def run_example():
    """
    运行示例，展示pandas_mcp框架的主要功能
    """
    # 创建示例数据
    data = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, np.nan, 55, 60, 65, 70],
        'income': [30000, 45000, 50000, 60000, 70000, 80000, np.nan, 100000, 110000, 120000],
        'education': ['高中', '大专', '本科', '硕士', '博士', '本科', '硕士', '博士', '本科', '硕士'],
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'score': [85, 90, 75, 95, 80, 85, 70, 90, 85, 95]
    })
    
    # 创建数据控制器
    controller = DataController()
    controller.data_model.set_data(data)
    
    # 注册处理器
    controller.register_processor('clean', CleanProcessor())
    controller.register_processor('transform', TransformProcessor())
    controller.register_processor('analyze', AnalysisProcessor())
    controller.register_processor('visualize', VisualizationProcessor())
    
    # 定义数据模式
    schema = {
        'age': {
            'type': float,
            'required': True,
            'range': (0, 120)
        },
        'income': {
            'type': float,
            'required': True,
            'range': (0, 1000000)
        },
        'education': {
            'type': str,
            'required': True,
            'values': ['高中', '大专', '本科', '硕士', '博士']
        },
        'category': {
            'type': str,
            'required': True,
            'values': ['A', 'B']
        },
        'score': {
            'type': float,
            'required': True,
            'range': (0, 100)
        }
    }
    
    schema_model = SchemaModel(schema)
    validation_results = schema_model.validate(controller.data_model)
    print("数据验证结果:", validation_results)
    
    # 使用流水线处理数据
    pipeline = PipelineController()
    pipeline.data_controller.data_model.set_data(data)
    
    # 注册处理器
    for name, processor in controller.processors.items():
        pipeline.register_processor(name, processor)
    
    # 添加处理步骤
    pipeline.add_step('clean', dropna={'subset': ['age', 'income']})
    pipeline.add_step('transform', 
        normalize={'age': 'standard', 'income': 'minmax'},
        encode_categorical=['education']
    )
    
    # 分析步骤
    pipeline.add_step('analyze',
        describe=True,
        corr={'method': 'pearson'},
        groupby_analysis={
            'columns': ['category'],
            'metrics': ['mean', 'std'],
            'numeric_only': True  # 只对数值列进行统计
        }
    )
    
    # 可视化步骤
    pipeline.add_step('visualize',
        plots=[
            {
                'type': 'distribution',
                'x': 'age',
                'title': 'Age Distribution',
                'kde': True
            },
            {
                'type': 'scatter',
                'x': 'age',
                'y': 'income',
                'title': 'Age vs Income'
            },
            {
                'type': 'box',
                'x': 'category',
                'y': 'score',
                'title': 'Score by Category'
            }
        ]
    )
    
    # 执行流水线
    try:
        results = pipeline.run()
        print("\n=== 处理结果 ===")
        
        # 输出分析结果
        analysis_result = pipeline.get_step_result(2)
        if analysis_result['status'] == 'success':
            print("\n描述性统计:")
            print(analysis_result['result']['describe'])
            
            print("\n相关性分析:")
            print(analysis_result['result']['correlation'])
            
            print("\n分组分析:")
            print(analysis_result['result']['groupby'])
        
        # 保存可视化结果
        visualization_result = pipeline.get_step_result(3)
        if visualization_result['status'] == 'success':
            figures = visualization_result['result']
            vis_processor = pipeline.data_controller.processors['visualize']
            os.makedirs('output/figures', exist_ok=True)
            vis_processor.save_figures(figures, 'output/figures')
            print("\n图表已保存到 output/figures 目录")
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
    
if __name__ == '__main__':
    run_example()
