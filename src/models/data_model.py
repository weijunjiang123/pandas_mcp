import pandas as pd

class DataModel:
    """
    数据模型层，负责封装DataFrame的基础操作
    """
    def __init__(self, data=None):
        """
        初始化数据模型
        
        Args:
            data: 可以是DataFrame或可转换为DataFrame的数据
        """
        self.df = pd.DataFrame(data) if data is not None else pd.DataFrame()
    
    def get_data(self):
        """
        获取DataFrame数据
        
        Returns:
            pd.DataFrame: 当前的DataFrame对象
        """
        return self.df
    
    def set_data(self, df):
        """
        设置DataFrame数据
        
        Args:
            df: DataFrame对象或可转换为DataFrame的数据
        """
        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            self.df = pd.DataFrame(df)
    
    def get_info(self):
        """
        获取数据基本信息
        
        Returns:
            dict: 包含数据形状、列名和数据类型的字典
        """
        return {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict()
        }
    
    def validate_columns(self, required_columns):
        """
        验证是否包含必需的列
        
        Args:
            required_columns (list): 必需的列名列表
            
        Returns:
            bool: 是否包含所有必需的列
        """
        return all(col in self.df.columns for col in required_columns)
    
    def head(self, n=5):
        """
        获取前n行数据
        
        Args:
            n (int): 返回的行数
            
        Returns:
            pd.DataFrame: 前n行数据
        """
        return self.df.head(n)
    
    def tail(self, n=5):
        """
        获取后n行数据
        
        Args:
            n (int): 返回的行数
            
        Returns:
            pd.DataFrame: 后n行数据
        """
        return self.df.tail(n)
    
    def sample(self, n=None, frac=None, random_state=None):
        """
        随机抽样
        
        Args:
            n (int, optional): 抽样数量
            frac (float, optional): 抽样比例
            random_state (int, optional): 随机种子
            
        Returns:
            pd.DataFrame: 抽样结果
        """
        return self.df.sample(n=n, frac=frac, random_state=random_state)
