import os
from datetime import datetime
from data_fetcher import IFindDataFetcher, DEFAULT_START_DATE
from calculator import CCFCalculator

# 获取环境变量中的 token (供 GitHub Actions 运行使用)
# 如果本地测试，可以退化为硬编码或在此处填入测试 token
REFRESH_TOKEN = os.environ.get("IFIND_REFRESH_TOKEN", "YOUR_TEST_TOKEN_HERE")
DATA_FILE = "ccf_data.csv"

# 输出到 CSV 的列（CFETS 等可选列存在时才包含）
BASE_COLUMNS = [
    "Date", "USDCNY_MID", "USDCNY_SPOT", "USDCNH", "DXY",
    "EURUSD", "USDJPY", "Basket_Impact", "DXY_Impact", "CNH_Impact",
    "CCF_Value", "Strength",
]
OPTIONAL_COLUMNS = ["CFETS", "GBPUSD", "USDCAD", "USDSEK", "USDCHF"]


def main():
    print(f"[{datetime.now()}] 启动逆周期因子计算流水线...")

    if REFRESH_TOKEN == "YOUR_TEST_TOKEN_HERE":
        print("警告：未使用真实的环境变量 IFIND_REFRESH_TOKEN。如果是本地运行，请在代码中替换或配置环境变量。")

    fetcher = IFindDataFetcher(REFRESH_TOKEN)

    try:
        print(f"1. 正在抓取 iFind 历史日线数据（{DEFAULT_START_DATE} 至今）...")
        fx_df = fetcher.get_fx_data_for_ccf(start_date=DEFAULT_START_DATE)
        print(f"   成功获取 {len(fx_df)} 个交易日的外汇数据")
    except Exception as e:
        print(f"数据拉取失败: {e}")
        return

    print("2. 正在计算逆周期因子...")
    calculator = CCFCalculator(fx_df)
    result_df = calculator.calculate()
    latest = result_df.iloc[-1]
    print(f"   计算完成，共 {len(result_df)} 期，最新一期 {latest['Date'].strftime('%Y-%m-%d')} "
          f"CCF={latest['CCF_Value']:.4f}（{latest['Strength']}）")

    print("3. 保存数据到 CSV...")
    columns = list(BASE_COLUMNS)
    for col in OPTIONAL_COLUMNS:
        if col in result_df.columns and result_df[col].notna().any():
            columns.insert(5, col)  # 紧跟在 DXY 之后，保持行情列聚在一起

    out_df = result_df[columns].copy()
    out_df["Date"] = out_df["Date"].dt.strftime("%Y-%m-%d")
    out_df.to_csv(DATA_FILE, index=False, encoding="utf-8", float_format="%.6f")
    print(f"   成功写入 {DATA_FILE}（全量覆盖，幂等）")
    print(f"[{datetime.now()}] 任务结束。")


if __name__ == "__main__":
    main()
