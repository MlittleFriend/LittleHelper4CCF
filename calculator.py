import numpy as np
import pandas as pd

# ICE 美元指数成分权重（用于在缺少真实美元指数代码时近似合成 DXY）
ICE_DXY_BASE = 50.14348112
ICE_DXY_WEIGHTS = {
    "EURUSD": -0.576,
    "USDJPY": 0.136,
    "GBPUSD": -0.119,
    "USDCAD": 0.091,
    "USDSEK": 0.042,
    "USDCHF": 0.036,
}


class CCFCalculator:
    """
    基于历史日线序列计算逆周期因子（向量化）。

    简化模型（央行真实模型为黑盒，权重可按研究需要调整）：
        理论中间价 = 前日收盘价 + 篮子货币影响 + 美元指数影响 + 离岸人民币影响
        逆周期因子 = 实际中间价 - 理论中间价
    """

    # 模型权重
    BASKET_BETA = 0.5  # 篮子货币影响弹性
    DXY_BETA = 0.2     # 美元指数直接影响弹性
    CNH_BETA = 0.1     # 离岸价差影响弹性

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def synthesize_dxy(self, df: pd.DataFrame) -> pd.Series:
        """按 ICE 权重用 6 个成分货币近似合成美元指数"""
        dxy = pd.Series(ICE_DXY_BASE, index=df.index, dtype=float)
        for col, weight in ICE_DXY_WEIGHTS.items():
            if col in df.columns and df[col].notna().any():
                dxy = dxy * (df[col].astype(float) ** weight)
        return dxy

    def calculate(self) -> pd.DataFrame:
        """
        计算全历史区间的逆周期因子。
        :return: DataFrame，含 Date、原始行情、各影响成分、CCF_Value、Strength
        """
        df = self.df.dropna(subset=["USDCNY_MID", "USDCNY_SPOT"]).copy()

        # 美元指数：优先使用真实数据列，否则用 ICE 权重近似合成
        if "DXY" in df.columns and df["DXY"].notna().any():
            df["DXY"] = df["DXY"].astype(float)
        else:
            df["DXY"] = self.synthesize_dxy(df)

        mid = df["USDCNY_MID"].astype(float)
        spot = df["USDCNY_SPOT"].astype(float)
        cnh = df["USDCNH"].astype(float)

        prev_spot = spot.shift(1)
        dxy_chg = df["DXY"].pct_change()

        # 篮子货币影响：优先用 CFETS 指数变动，缺失时回退为美元指数变动代理。
        # 注意：CFETS 指数为周频数据，非周五交易日为空，需先做 ffill 前向填充
        if "CFETS" in df.columns and df["CFETS"].notna().any():
            cfets_series = df["CFETS"].astype(float).ffill()
            basket_chg = cfets_series.pct_change()
            df["Basket_Impact"] = -self.BASKET_BETA * basket_chg * prev_spot
        else:
            df["Basket_Impact"] = self.BASKET_BETA * dxy_chg * prev_spot

        # 美元指数直接影响
        df["DXY_Impact"] = self.DXY_BETA * dxy_chg * prev_spot

        # 离岸价差影响
        df["CNH_Impact"] = (cnh - spot) * self.CNH_BETA

        # 逆周期因子 = 实际中间价 - 理论中间价
        df["CCF_Value"] = mid - (prev_spot + df["Basket_Impact"] + df["DXY_Impact"] + df["CNH_Impact"])

        # 强度评级（向量化计算）
        abs_ccf = df["CCF_Value"].abs()
        conditions = [abs_ccf > 0.0200, abs_ccf > 0.0050]
        choices = ["强", "中"]
        df["Strength"] = np.select(conditions, choices, default="弱")
        df.loc[df["CCF_Value"].isna(), "Strength"] = ""

        # 仅保留可计算出 CCF 的交易日
        df = df.dropna(subset=["CCF_Value"]).reset_index(drop=True)
        return df

    @staticmethod
    def evaluate_strength(ccf_value: float) -> str:
        """评估强度（单值计算辅助函数）"""
        if pd.isna(ccf_value):
            return ""
        abs_val = abs(ccf_value)
        if abs_val > 0.0200:
            return "强"
        elif abs_val > 0.0050:
            return "中"
        else:
            return "弱"

