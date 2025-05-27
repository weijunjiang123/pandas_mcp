import json
from typing import Dict, Any, Optional
from urllib import request, parse
import urllib.error

class PandasMCPClient:
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        """初始化MCP客户端"""
        self.server_url = server_url

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """发送HTTP请求"""
        url = f"{self.server_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if data:
                data = json.dumps(data).encode('utf-8')
            
            req = request.Request(
                url, 
                data=data, 
                headers=headers, 
                method=method
            )
            
            with request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            print(f"服务器连接错误: {str(e)}")
            return {"status": "error", "message": f"服务器连接错误: {str(e)}"}
        except Exception as e:
            print(f"请求错误: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def load_data(self, source: str, encoding: str = 'utf-8', sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """测试加载数据功能"""
        try:
            args = {
                "source": source,
                "encoding": encoding
            }
            if sheet_name:
                args["sheet_name"] = sheet_name
                
            result = self._make_request("tool/load_data", "POST", args)
            print("\n=== 测试 load_data ===")
            print(f"输入参数: {json.dumps(args, ensure_ascii=False, indent=2)}")
            print(f"返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except Exception as e:
            print(f"错误: {str(e)}")
            return {"status": "error", "message": str(e)}

    def save_data(self, path: str, encoding: str = 'utf-8', index: bool = False) -> Dict[str, str]:
        """测试保存数据功能"""
        try:
            args = {
                "path": path,
                "encoding": encoding,
                "index": index
            }
            result = self._make_request("tool/save_data", "POST", args)
            print("\n=== 测试 save_data ===")
            print(f"输入参数: {json.dumps(args, ensure_ascii=False, indent=2)}")
            print(f"返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except Exception as e:
            print(f"错误: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_data_info(self) -> Dict[str, Any]:
        """测试获取数据信息功能"""
        try:
            result = self._make_request("tool/get_data_info", "POST", {})
            print("\n=== 测试 get_data_info ===")
            print(f"返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except Exception as e:
            print(f"错误: {str(e)}")
            return {"status": "error", "message": str(e)}

    def run_process(self, process_name: str, process_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """测试数据处理功能"""
        try:
            args = {
                "process_name": process_name,
                "process_params": process_params or {}
            }
            result = self._make_request("tool/run_process", "POST", args)
            print("\n=== 测试 run_process ===")
            print(f"输入参数: {json.dumps(args, ensure_ascii=False, indent=2)}")
            print(f"返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except Exception as e:
            print(f"错误: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_data_preview(self) -> Dict[str, Any]:
        """测试数据预览功能"""
        try:
            result = self._make_request("resource/data-preview")
            print("\n=== 测试 data_preview ===")
            print(f"返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except Exception as e:
            print(f"错误: {str(e)}")
            return {"status": "error", "message": str(e)}

def run_tests():
    """运行所有测试"""
    client = PandasMCPClient()
    
    # 1. 测试加载数据
    client.load_data("example_data.csv")
    
    # 2. 测试获取数据信息
    client.get_data_info()
    
    # 3. 测试数据预览
    client.get_data_preview()
    
    # 4. 测试数据处理
    # 假设有一个clean_missing的处理器
    client.run_process("clean_missing", {"columns": ["Age", "Income"]})
    
    # 5. 测试保存数据
    client.save_data("output/processed_data.csv")

if __name__ == "__main__":
    run_tests()
