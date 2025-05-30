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
#     """
#     运行示例，展示pandas_mcp框架的主要功能
#     """
#     # 创建示例数据
#     def generate_random_data(n_rows=50, random_state=None):
#         np.random.seed(random_state)
#         # 年龄范围：20 ~ 110，随机插入部分NaN
#         age = np.random.choice(np.append(np.arange(20, 121, 5), [np.nan]), size=n_rows)
#         # 收入范围：3万 ~ 21万，步长1万，随机插入部分NaN
#         income = np.random.choice(np.append(np.arange(30000, 210001, 10000), [np.nan]), size=n_rows)
#         # 教育程度
#         education_levels = ['高中', '大专', '本科', '硕士', '博士']
#         education = np.random.choice(education_levels, size=n_rows)
#         # 分类A/B/C
#         categories = ['A', 'B']
#         category = np.random.choice(categories, size=n_rows)
#         # 分数 0~100
#         score = np.random.randint(60, 101, size=n_rows)

#         data = pd.DataFrame({
#             'age': age,
#             'income': income,
#             'education': education,
#             'category': category,
#             'score': score
#         })
#         return data

#     # 用法示例
#     data = generate_random_data(n_rows=20, random_state=42)
#     data = pd.DataFrame({
#         'age': [25, 30, 35, 40, 45, np.nan, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115],
#         'income': [30000, 45000, 50000, 60000, 70000, 80000, np.nan, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000, 200000, 210000],
#         'education': ['高中', '大专', '本科', '硕士', '博士', '本科', '硕士', '博士', '本科', '硕士', '博士', '本科', '大专', '硕士', '博士', '本科', '大专', '硕士', '博士'],
#         'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
#         'score': [85, 90, 75, 95, 80, 85, 70, 90, 85, 95, 64, 23, 88, 78, 92, 81, 89, 77, 93, 82]
#     })
    def infer_schema(df):
        schema = {}
        for col in df.columns:
            dtype = df[col].dtype
            sch = {}            # 推断类型
            if pd.api.types.is_numeric_dtype(dtype):
                sch['type'] = float
                sch['required'] = df[col].isnull().sum() == 0
                sch['range'] = (df[col].min(), df[col].max())
            elif pd.api.types.is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
                sch['type'] = str
                sch['required'] = df[col].isnull().sum() == 0
                sch['values'] = sorted(df[col].dropna().unique().tolist())
            else:
                sch['type'] = str
                sch['required'] = df[col].isnull().sum() == 0
            schema[col] = sch
        return schema

    data = pd.read_json("", orient='records', encoding='utf-8')
    # 创建数据控制器
    controller = DataController()
    controller.data_model.set_data(data)
    
    # 注册处理器
    controller.register_processor('clean', CleanProcessor())
    controller.register_processor('transform', TransformProcessor())
    controller.register_processor('analyze', AnalysisProcessor())
    controller.register_processor('visualize', VisualizationProcessor())
    
    # 定义数据模式
    schema = infer_schema(data)
       
    
    schema_model = SchemaModel(schema)
    validation_results = schema_model.validate(controller.data_model)
    print("数据验证结果:", validation_results)
    
    # 使用流水线处理数据
    pipeline = PipelineController()
    pipeline.data_controller.data_model.set_data(data)
    
    # 注册处理器
    for name, processor in controller.processors.items():
        pipeline.register_processor(name, processor)
      # 添加处理步骤 - 使用实际存在的列
    pipeline.add_step('clean', dropna={'subset': ['pay_price', 'list_price']})
    pipeline.add_step('transform', 
        normalize={'pay_price': 'standard', 'list_price': 'minmax'},
        encode_categorical=['order_chn_l1', 'gender', 'prd_line']
    )
    
    # 分析步骤
    pipeline.add_step('analyze',
        describe=True,
        corr={'method': 'pearson'},
        groupby_analysis={
            'columns': ['order_chn_l1'],
            'metrics': ['mean', 'std'],
            'numeric_only': True  # 只对数值列进行统计
        }
    )
      # 可视化步骤
    pipeline.add_step('visualize',
        plots=[
            {
                'type': 'distribution',
                'x': 'pay_price',
                'title': 'Pay Price Distribution',
                'kde': True
            },
            {
                'type': 'scatter',
                'x': 'pay_price',
                'y': 'list_price',
                'title': 'Pay Price vs List Price'
            },
            {
                'type': 'box',
                'x': 'order_chn_l1',
                'y': 'pay_price',
                'title': 'Pay Price by Order Channel'
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
