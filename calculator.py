import pandas as pd

class CCFCalculator:
    def __init__(self, data: dict):
        self.data = data

    def calculate(self):
        """
        计算逆周期因子。
        公式简化示意：
        逆周期因子 = 中间价 - (前日收盘价 + 篮子货币影响 + 美元指数影响 + 离岸人民币影响)
        注意：此处采用简化权重模型。实际央行模型为黑盒，需您根据具体研究调整权重。
        """
        # 提取数据，需根据 iFind 实际代码对应
        cny_mid = self.data.get("USDCNY.EX", 7.1000) # 假设中间价
        cny_spot = self.data.get("USDCNY.FX", 7.1050) # 假设即期收盘
        cnh = self.data.get("USDCNH.FX", 7.1100)
        dxy = self.data.get("UDI.FX", 104.00)
        
        # 简化计算：前日收盘与中间价的价差作为基准
        # 假设：篮子影响和美元影响等简化为一个调整值
        basket_impact = 0.0050 # 示例值
        dxy_impact = 0.0020    # 示例值
        cnh_impact = (cnh - cny_spot) * 0.1 # 离岸价差影响的 10%

        # 计算逆周期因子
        ccf_value = cny_mid - (cny_spot + basket_impact + dxy_impact + cnh_impact)
        
        # 评级
        strength = self.evaluate_strength(ccf_value)
        
        return {
            "USDCNY_MID": cny_mid,
            "USDCNY_SPOT": cny_spot,
            "USDCNH": cnh,
            "DXY": dxy,
            "Basket_Impact": basket_impact,
            "DXY_Impact": dxy_impact,
            "CNH_Impact": cnh_impact,
            "CCF_Value": ccf_value,
            "Strength": strength
        }

    def evaluate_strength(self, ccf_value: float) -> str:
        """评估强度"""
        if abs(ccf_value) > 0.0200:
            return "强"
        elif abs(ccf_value) > 0.0050:
            return "中"
        else:
            return "弱"
