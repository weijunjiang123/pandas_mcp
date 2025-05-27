from fastmcp import FastMCP
import uvicorn
from src.controllers.data_controller import DataController
import pandas as pd
from typing import Dict, Any, Optional, List
import json

# 创建MCP服务器实例
server = FastMCP(
    name="Pandas MCP",
    port=8081  # 使用8081端口
    )

# 导入所需的处理器
from src.processors import (
    CleanProcessor,
    TransformProcessor,
    AnalysisProcessor,
    VisualizationProcessor
)

# 全局数据控制器实例
data_controller = DataController()

# 注册处理器
data_controller.register_processor('clean', CleanProcessor())
data_controller.register_processor('transform', TransformProcessor())
data_controller.register_processor('analyze', AnalysisProcessor())
data_controller.register_processor('visualize', VisualizationProcessor())

@server.tool(name="load_data")
def load_data(source: str, encoding: str = 'utf-8', sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """加载数据文件并返回基本信息
    
    Args:
        source (str): 数据文件路径，支持csv、excel等格式
        encoding (str, optional): 文件编码格式. 默认为'utf-8'
        sheet_name (Optional[str], optional): Excel文件的工作表名称. 默认为None
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - info (Dict): 成功时返回数据基本信息，包含行数、列数、数据类型等
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> result = load_data('data.csv')
        >>> result = load_data('data.xlsx', sheet_name='Sheet1')
    """
    try:
        kwargs = {'encoding': encoding}
        if sheet_name is not None and (source.endswith('.xls') or source.endswith('.xlsx')):
            kwargs['sheet_name'] = sheet_name
            
        data_controller.load_data(source, **kwargs)
        return {
            "status": "success",
            "info": data_controller.get_info()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="save_data")
def save_data(path: str, encoding: str = 'utf-8', index: bool = False) -> Dict[str, str]:
    """保存当前数据到指定文件
    
    Args:
        path (str): 保存文件的路径
        encoding (str, optional): 文件编码格式. 默认为'utf-8'
        index (bool, optional): 是否保存行索引. 默认为False
        
    Returns:
        Dict[str, str]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - message (str): 操作结果说明或错误信息
            
    Examples:
        >>> result = save_data('output.csv')
        >>> result = save_data('output.xlsx', index=True)
    """
    try:
        data_controller.save_data(path, encoding=encoding, index=index)
        return {
            "status": "success",
            "message": f"数据已保存到 {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="get_data_info")
def get_data_info() -> Dict[str, Any]:
    """获取当前加载数据的基本信息
    
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - info (Dict): 成功时返回数据信息，包含:
                - shape: 数据形状 (行数, 列数)
                - columns: 列名列表
                - dtypes: 每列的数据类型
                - memory_usage: 内存使用情况
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> info = get_data_info()
        >>> print(f"数据大小: {info['info']['shape']}")
    """
    try:
        return {
            "status": "success",
            "info": data_controller.get_info()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="clean_data")
def clean_data(data: Optional[List[Dict]] = None, dropna: bool = True, drop_duplicates: bool = True, 
              fillna_value: Optional[str] = None) -> Dict[str, Any]:
    """清洗数据，包括处理缺失值和重复值
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        dropna (bool, optional): 是否删除包含缺失值的行. 默认为True
        drop_duplicates (bool, optional): 是否删除重复行. 默认为True
        fillna_value (str, optional): 用于填充缺失值的值. 如果提供则使用填充而不是删除
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result (Dict): 清洗结果统计信息
            - data (List[Dict]): 处理后的数据，JSON格式
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> result = clean_data(data=[{"col1": 1, "col2": null}])
        >>> result = clean_data(data=[{"col1": 1}], fillna_value='unknown')
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        params = {
            'dropna': dropna and fillna_value is None,
            'drop_duplicates': drop_duplicates
        }
        if fillna_value is not None:
            params['fillna'] = {'value': fillna_value}
            
        result = data_controller.run_process('clean', **params)
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="normalize_columns")
def normalize_columns(data: Optional[List[Dict]] = None, columns: List[str] = None, 
                     method: str = 'standard') -> Dict[str, Any]:
    """对指定列进行数值标准化
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        columns (List[str]): 需要标准化的列名列表
        method (str, optional): 标准化方法，可选值: 'standard'或'minmax'. 默认为'standard'
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result (Dict): 标准化后的统计信息
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"age": 25, "income": 50000}, {"age": 30, "income": 60000}]
        >>> result = normalize_columns(data=data, columns=['age', 'income'])
        >>> result = normalize_columns(data=data, columns=['income'], method='minmax')
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        result = data_controller.run_process('transform', normalize={
            col: method for col in columns
        })
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="encode_categorical")
def encode_categorical(data: Optional[List[Dict]] = None, columns: List[str] = None, 
                      method: str = 'onehot') -> Dict[str, Any]:
    """对分类列进行编码
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        columns (List[str]): 需要编码的分类列名列表
        method (str, optional): 编码方法，可选值: 'onehot'或'label'. 默认为'onehot'
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result (Dict): 编码后的信息，包含新增的列名等
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"category": "A", "color": "red"}, {"category": "B", "color": "blue"}]
        >>> result = encode_categorical(data=data, columns=['category', 'color'])
        >>> result = encode_categorical(data=data, columns=['category'], method='label')
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        result = data_controller.run_process('transform', encode_categorical={
            'columns': columns,
            'method': method
        })
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="describe_data")
def describe_data(data: Optional[List[Dict]] = None, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """生成数据的描述性统计信息
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        columns (List[str], optional): 需要分析的列名列表. 默认为None，分析所有数值列
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result (Dict): 描述性统计结果，包含count、mean、std等
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"age": 25, "income": 50000}, {"age": 30, "income": 60000}]
        >>> result = describe_data(data=data)  # 分析所有数值列
        >>> result = describe_data(data=data, columns=['age'])  # 分析指定列
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        params = {}
        if columns:
            params['columns'] = columns
            
        result = data_controller.run_process('analyze', describe=True, **params)
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="correlation_analysis")
def correlation_analysis(data: Optional[List[Dict]] = None, columns: Optional[List[str]] = None, 
                       method: str = 'pearson') -> Dict[str, Any]:
    """计算数据列之间的相关性
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        columns (List[str], optional): 需要分析的列名列表. 默认为None，分析所有数值列
        method (str, optional): 相关性计算方法，可选值: 'pearson'、'spearman'、'kendall'. 默认为'pearson'
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result (Dict): 相关性矩阵
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"age": 25, "income": 50000}, {"age": 30, "income": 60000}]
        >>> result = correlation_analysis(data=data)  # 分析所有数值列
        >>> result = correlation_analysis(data=data, columns=['age', 'income'], method='spearman')
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        params = {'method': method}
        if columns:
            params['columns'] = columns
            
        result = data_controller.run_process('analyze', corr=params)
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="plot_distribution")
def plot_distribution(data: Optional[List[Dict]] = None, column: str = None, 
                     bins: int = 30) -> Dict[str, Any]:
    """绘制单个列的分布图
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        column (str): 需要绘制分布图的列名
        bins (int, optional): 直方图的箱数. 默认为30
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result: 图表保存路径或Base64编码的图像数据
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"age": 25}, {"age": 30}, {"age": 35}]
        >>> result = plot_distribution(data=data, column='age')
        >>> result = plot_distribution(data=data, column='age', bins=50)
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        result = data_controller.run_process('visualize', plots=[{
            'type': 'distribution',
            'x': column,
            'bins': bins
        }])
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(name="plot_scatter")
def plot_scatter(data: Optional[List[Dict]] = None, x: str = None, y: str = None, 
                color: Optional[str] = None) -> Dict[str, Any]:
    """绘制散点图
    
    Args:
        data (List[Dict], optional): JSON格式的数据列表. 如果提供则使用此数据，否则使用已加载的数据
        x (str): X轴列名
        y (str): Y轴列名
        color (str, optional): 用于分组着色的列名. 默认为None
        
    Returns:
        Dict[str, Any]: 包含以下字段的字典:
            - status (str): 操作状态，'success'或'error'
            - result: 图表保存路径或Base64编码的图像数据
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> data = [{"age": 25, "income": 50000, "category": "A"},
        ...         {"age": 30, "income": 60000, "category": "B"}]
        >>> result = plot_scatter(data=data, x='age', y='income')
        >>> result = plot_scatter(data=data, x='age', y='income', color='category')
    """
    try:
        if data is not None:
            data_controller.load_data(data)
            
        plot_params = {
            'type': 'scatter',
            'x': x,
            'y': y
        }
        if color:
            plot_params['color'] = color
            
        result = data_controller.run_process('visualize', plots=[plot_params])
        df = data_controller.get_data()
        return {
            "status": "success",
            "result": result,
            "data": json.loads(df.to_json(orient='records'))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@server.resource(name="data_preview",uri="resource://data-preview")
def get_data_preview() -> str:
    """获取当前数据的预览信息
    
    Returns:
        str: JSON格式字符串，包含以下字段:
            - status (str): 操作状态，'success'或'error'
            - preview (List[Dict]): 成功时返回数据前5行的记录
            - message (str): 错误时返回错误信息
            
    Examples:
        >>> preview = json.loads(get_data_preview())
        >>> for record in preview['preview']:
        ...     print(record)
    """
    try:
        df = data_controller.get_data()
        preview = df.head().to_json(orient='records')
        return json.dumps({
            "status": "success",
            "preview": json.loads(preview)
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    server.run(transport="streamable-http")
    # http_app = server.http_app()
    # uvicorn.run(http_app, host="0.0.0.0", port=8000)
