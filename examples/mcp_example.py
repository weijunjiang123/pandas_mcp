"""
演示如何使用pandas-mcp的MCP服务器功能
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)


import pandas as pd
from src.processors.clean_processor import CleanProcessor
from src.processors.analysis_processor import AnalysisProcessor
from src.controllers.data_controller import DataController

def main():
    # 准备示例数据
    df = pd.DataFrame({
        'id': range(1, 6),
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, None, 35, 28],
        'score': [85.5, 92.0, 78.5, None, 88.0]
    })
    df.to_csv('example_data.csv', index=False)
    
    # 启动MCP服务器
    print("启动MCP服务器...")
    print("服务器运行在 http://localhost:8000")
    print("\n示例MCP工具使用:")
    print("1. 加载数据:")
    print('   use_mcp_tool("localhost:8000", "load_data", {"source": "example_data.csv", "encoding": "utf-8"})')
    print("\n2. 获取数据信息:")
    print('   use_mcp_tool("localhost:8000", "get_data_info", {})')
    print("\n3. 查看数据预览:")
    print('   access_mcp_resource("localhost:8000", "data_preview")')
    print("\n4. 执行数据清洗:")
    print('   use_mcp_tool("localhost:8000", "run_process", {')
    print('       "process_name": "CleanProcessor",')
    print('       "process_params": {"fillna": "mean"}')
    print('   })')
    print("\n5. 保存处理后的数据:")
    print('   use_mcp_tool("localhost:8000", "save_data", {"path": "cleaned_data.csv", "encoding": "utf-8", "index": false})')

if __name__ == "__main__":
    main()
