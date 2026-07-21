import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://quantapi.51ifind.com/api/v1"

# 默认抓取起始日期
DEFAULT_START_DATE = "2026-01-01"

# 已实测可用的 iFind 外汇日线代码（cmd_history_quotation 验证通过）
FX_CODES = {
    "USDCNY_MID": "USDCNY.EX",   # 美元兑人民币中间价
    "USDCNY_SPOT": "USDCNY.FX",  # 在岸即期收盘价
    "USDCNH": "USDCNH.FX",       # 离岸人民币
    "EURUSD": "EURUSD.FX",       # 欧元兑美元（ICE 美元指数成分）
    "USDJPY": "USDJPY.FX",       # 美元兑日元（ICE 美元指数成分）
    "GBPUSD": "GBPUSD.FX",       # 英镑兑美元（ICE 美元指数成分）
    "USDCAD": "USDCAD.FX",       # 美元兑加元（ICE 美元指数成分）
    "USDSEK": "USDSEK.FX",       # 美元兑瑞典克朗（ICE 美元指数成分）
    "USDCHF": "USDCHF.FX",       # 美元兑瑞郎（ICE 美元指数成分）
}

# 占位：在 iFind 终端确认真实 thscode 后填入，即自动纳入抓取与计算。
# 未配置时，美元指数由 calculator 按 ICE 权重用上述 6 个成分货币近似合成；
# CFETS 不参与篮子影响计算（回退为美元指数代理）。
DXY_CODE = None    # 美元指数 thscode，例如 "XXXX.XX"
CFETS_CODE = None  # CFETS 人民币汇率指数 thscode，例如 "XXXX.XX"


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

    def fetch_historical_data(self, codes: str, indicators: str, start_date: str, end_date: str):
        """
        获取历史日线数据（cmd_history_quotation 接口）。
        :param codes: 逗号分隔的 thscode
        :param indicators: 逗号分隔的指标，如 "close"
        :param start_date: YYYY-MM-DD
        :param end_date: YYYY-MM-DD
        :return: 接口原始 JSON
        """
        if not self.access_token:
            self.get_access_token()
        resp = requests.post(
            f"{BASE_URL}/cmd_history_quotation",
            headers={"Content-Type": "application/json", "access_token": self.access_token},
            json={
                "codes": codes,
                "indicators": indicators,
                "startdate": start_date,
                "enddate": end_date,
                "functionpara": {"Fill": "Blank"},
            },
            timeout=30,
        )
        data = resp.json()
        if data.get("errorcode") != 0:
            raise RuntimeError(f"获取历史行情失败: {data}")
        return data

    def fetch_history_dataframe(self, code_map: dict, start_date: str, end_date: str,
                                indicator: str = "close") -> pd.DataFrame:
        """
        抓取多个代码的日线数据并合并为宽表 DataFrame（含 Date 列）。
        :param code_map: {列名: thscode}
        :return: DataFrame，列为 Date + code_map 的各键，按日期升序
        """
        data = self.fetch_historical_data(
            ",".join(code_map.values()), indicator, start_date, end_date
        )

        # thscode -> 列名 的反查表
        code_to_name = {v: k for k, v in code_map.items()}
        df = pd.DataFrame()
        for tbl in data.get("tables", []):
            name = code_to_name.get(tbl.get("thscode"))
            if name is None:
                continue
            values = tbl.get("table", {}).get(indicator) or []
            part = pd.DataFrame({"Date": tbl.get("time", []), name: values})
            df = part if df.empty else df.merge(part, on="Date", how="outer")

        if df.empty:
            raise RuntimeError("历史行情接口未返回任何有效数据")

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        return df

    def get_fx_data_for_ccf(self, start_date: str = DEFAULT_START_DATE,
                            end_date: str = None) -> pd.DataFrame:
        """
        抓取计算逆周期因子所需的全部外汇日线数据。
        包含：USDCNY 中间价/即期、USDCNH、ICE 美元指数 6 个成分货币，
        以及（若已配置真实代码）美元指数与 CFETS 指数。
        :return: 宽表 DataFrame，含 Date 列，按日期升序
        """
        end_date = end_date or datetime.now().strftime("%Y-%m-%d")

        code_map = dict(FX_CODES)
        if DXY_CODE:
            code_map["DXY"] = DXY_CODE
        if CFETS_CODE:
            code_map["CFETS"] = CFETS_CODE

        return self.fetch_history_dataframe(code_map, start_date, end_date)
