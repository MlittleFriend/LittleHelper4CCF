import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://quantapi.51ifind.com/api/v1"

class IFindDataFetcher:
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.access_token = None

    def get_access_token(self):
        """获取 iFind API access_token"""
        resp = requests.post(
            f"{BASE_URL}/get_access_token",
            headers={"Content-Type": "application/json", "refresh_token": self.refresh_token},
            timeout=10,
        )
        data = resp.json()
        if data.get("errorcode") != 0:
            raise RuntimeError(f"获取access_token失败: {data}")
        self.access_token = data["data"]["access_token"]
        return self.access_token

    def fetch_realtime_data(self, codes: str, indicators: str):
        """获取实时行情数据"""
        if not self.access_token:
            self.get_access_token()
        resp = requests.post(
            f"{BASE_URL}/real_time_quotation",
            headers={"Content-Type": "application/json", "access_token": self.access_token},
            json={"codes": codes, "indicators": indicators},
            timeout=10,
        )
        return resp.json()

    def fetch_historical_data(self, codes: str, indicators: str, start_date: str, end_date: str):
        """获取历史日线数据"""
        if not self.access_token:
            self.get_access_token()
        resp = requests.post(
            f"{BASE_URL}/high_frequency", # 或 history 接口，根据 iFind 实际可用接口
            headers={"Content-Type": "application/json", "access_token": self.access_token},
            json={
                "codes": codes, 
                "indicators": indicators, 
                "starttime": start_date, 
                "endtime": end_date
            },
            timeout=15,
        )
        return resp.json()

    def get_fx_data_for_ccf(self):
        """
        抓取计算逆周期因子所需的外汇数据。
        注意：这里的 thscode 均为常用占位符，若执行报错请根据您的账号权限修改。
        """
        # 美元指数 (DXY), 离岸人民币 (USDCNH), 欧元 (EURUSD), 日元 (USDJPY), CFETS
        # 这里用实时行情接口简化，或者使用最近的一个收盘价。
        codes = "UDI.FX,USDCNY.EX,USDCNY.FX,USDCNH.FX,EURUSD.FX,USDJPY.FX,CFETS.EX"
        indicators = "close,open,latest"
        
        data = self.fetch_realtime_data(codes, indicators)
        if data.get("errorcode") != 0:
             raise RuntimeError(f"获取行情数据失败: {data}")
        
        # 解析返回的数据为方便计算的字典
        result = {}
        tables = data.get("tables", [])
        for tbl in tables:
            thscode = tbl.get("thscode")
            latest_val = tbl.get("table", {}).get("latest", [None])[0]
            result[thscode] = latest_val
            
        return result
