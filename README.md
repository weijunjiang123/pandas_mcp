# Pandas MCP

一个基于MCP (Model-Controller-Processor) 架构的pandas扩展框架，提供更简洁、统一和功能化的数据处理接口。

## 特性

- **MCP架构**: 采用Model-Controller-Processor架构，实现关注点分离
- **模块化设计**: 每个组件都是独立的，可以根据需要组合使用
- **流水线处理**: 支持构建数据处理流水线，简化复杂的数据处理流程
- **灵活扩展**: 易于添加新的处理器和自定义功能
- **完整功能**: 内置数据清洗、转换、分析和可视化等常用功能

## 安装

```bash
pip install pandas-mcp
```

## 快速开始

```python
from pandas_mcp import DataController, PipelineController
from pandas_mcp.processors import CleanProcessor, TransformProcessor, AnalysisProcessor

# 创建控制器
controller = DataController()

# 加载数据
controller.load_data("data.csv")

# 注册处理器
controller.register_processor('clean', CleanProcessor())
controller.register_processor('transform', TransformProcessor())
controller.register_processor('analyze', AnalysisProcessor())

# 使用流水线处理数据
pipeline = PipelineController()
pipeline.register_processor('clean', controller.processors['clean'])
pipeline.register_processor('transform', controller.processors['transform'])
pipeline.register_processor('analyze', controller.processors['analyze'])

# 添加处理步骤
pipeline.add_step('clean', dropna=True)
pipeline.add_step('transform', 
    normalize={'age': 'standard', 'income': 'minmax'},
    encode_categorical=['education']
)
pipeline.add_step('analyze',
    describe=True,
    corr={'method': 'pearson'}
)

# 执行流水线
results = pipeline.run()

# 获取结果
analysis_result = pipeline.get_step_result(2)
print(analysis_result['result']['describe'])
```

## 详细功能

### 数据模型层 (Model)

- **DataModel**: 封装DataFrame的基础操作
- **SchemaModel**: 数据结构定义和验证

### 控制层 (Controller)

- **DataController**: 协调数据流转
- **PipelineController**: 管理处理流程

### 处理器层 (Processor)

- **CleanProcessor**: 数据清洗
  - 处理缺失值
  - 删除重复值
  - 异常值检测与处理
  - 数据过滤

- **TransformProcessor**: 数据转换
  - 特征工程
  - 数据类型转换
  - 标准化/归一化
  - 编码转换

- **AnalysisProcessor**: 数据分析
  - 描述性统计
  - 相关性分析
  - 统计检验
  - 机器学习支持

- **VisualizationProcessor**: 数据可视化
  - 统计图表
  - 分布可视化
  - 关系可视化
  - 比较可视化

## 使用示例

### 基础数据清洗

```python
from pandas_mcp import DataController
from pandas_mcp.processors import CleanProcessor

controller = DataController()
controller.load_data("data.csv")
controller.register_processor('clean', CleanProcessor())

# 执行清洗
result = controller.run_process('clean',
    dropna={'subset': ['age', 'income']},
    fillna={'name': 'Unknown'},
    drop_duplicates=True
)
```

### 数据转换和特征工程

```python
from pandas_mcp.processors import TransformProcessor

processor = TransformProcessor()
controller.register_processor('transform', processor)

# 执行转换
result = controller.run_process('transform',
    normalize={'age': 'standard', 'income': 'minmax'},
    encode_categorical=['education', 'occupation'],
    create_polynomial_features=['age', 'income']
)
```

### 数据分析

```python
from pandas_mcp.processors import AnalysisProcessor

processor = AnalysisProcessor()
controller.register_processor('analyze', processor)

# 执行分析
result = controller.run_process('analyze',
    describe=True,
    corr={'method': 'pearson'},
    groupby_analysis={
        'columns': ['category'],
        'metrics': ['mean', 'std']
    }
)
```

### 数据可视化

```python
from pandas_mcp.processors import VisualizationProcessor

processor = VisualizationProcessor()
controller.register_processor('visualize', processor)

# 创建可视化
result = controller.run_process('visualize',
    plots=[
        {
            'type': 'distribution',
            'x': 'age',
            'title': 'Age Distribution'
        },
        {
            'type': 'scatter',
            'x': 'age',
            'y': 'income',
            'title': 'Age vs Income'
        }
    ]
)
```

## 项目结构

```
pandas_mcp/
├── src/
│   ├── models/
│   │   ├── data_model.py
│   │   └── schema_model.py
│   ├── controllers/
│   │   ├── data_controller.py
│   │   └── pipeline_controller.py
│   └── processors/
│       ├── base_processor.py
│       ├── clean_processor.py
│       ├── transform_processor.py
│       ├── analysis_processor.py
│       └── visualization_processor.py
```

## MCP 调用

### 服务端配置

```python
from mcp_server import MCPServer

# 创建并启动MCP服务器
server = MCPServer()

# 注册工具
@server.tool("analyze_data")
def analyze_data(data_path: str, metrics: list):
    # 实现数据分析逻辑
    return {...}  # 返回分析结果

# 注册资源
@server.resource("data_schema")
def get_data_schema():
    return {...}  # 返回数据schema

# 启动服务器
server.start()
```

### 客户端使用

```python
from mcp_client import MCPClient

# 连接到MCP服务器
client = MCPClient()

# 调用工具
result = client.use_tool(
    server_name="analysis_server",
    tool_name="analyze_data",
    arguments={
        "data_path": "data.csv",
        "metrics": ["mean", "std"]
    }
)

# 访问资源
schema = client.access_resource(
    server_name="analysis_server",
    uri="data_schema"
)
```

### 支持的功能

1. **工具调用**
   - 支持同步和异步调用
   - 参数类型验证
   - 错误处理和重试机制

2. **资源访问**
   - 缓存支持
   - 版本管理
   - 访问控制

3. **服务发现**
   - 自动服务注册
   - 健康检查
   - 负载均衡

4. **数据序列化**
   - JSON格式支持
   - 二进制数据传输
   - 压缩选项

## 开发计划

1. **配置管理**
   - 添加配置系统
   - 支持从YAML/JSON加载处理步骤

2. **插件系统**
   - 支持动态加载自定义处理器
   - 提供插件开发指南

3. **分布式处理**
   - 整合Dask或Spark
   - 支持大数据处理

4. **缓存系统**
   - 为中间结果提供缓存机制
   - 提高执行效率

5. **日志与监控**
   - 集成日志系统
   - 追踪数据处理过程

## 贡献指南

1. Fork 该仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
