import argparse
import logging
import os
import sys
from datetime import datetime
from data_fetcher import IFindDataFetcher, DEFAULT_START_DATE
from calculator import CCFCalculator

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CCF_Main")

REFRESH_TOKEN = os.environ.get("IFIND_REFRESH_TOKEN", "YOUR_TEST_TOKEN_HERE")
DEFAULT_DATA_FILE = "ccf_data.csv"

# 输出到 CSV 的列（CFETS 等可选列存在时才包含）
BASE_COLUMNS = [
    "Date", "USDCNY_MID", "USDCNY_SPOT", "USDCNH", "DXY",
    "EURUSD", "USDJPY", "Basket_Impact", "DXY_Impact", "CNH_Impact",
    "CCF_Value", "Strength",
]
OPTIONAL_COLUMNS = ["CFETS", "GBPUSD", "USDCAD", "USDSEK", "USDCHF"]


def parse_args():
    parser = argparse.ArgumentParser(description="逆周期因子 (CCF) 自动计算流水线")
    parser.add_argument("--start-date", type=str, default=DEFAULT_START_DATE, help="抓取起始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None, help="抓取截止日期 (YYYY-MM-DD)，默认为今天")
    parser.add_argument("--output", type=str, default=DEFAULT_DATA_FILE, help="输出 CSV 文件路径")
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("启动逆周期因子计算流水线...")

    if REFRESH_TOKEN == "YOUR_TEST_TOKEN_HERE":
        logger.error("未配置环境变量 IFIND_REFRESH_TOKEN，无法运行。")
        sys.exit(1)

    fetcher = IFindDataFetcher(REFRESH_TOKEN)

    try:
        logger.info(f"1. 正在抓取 iFind 历史日线数据（{args.start_date} 至 {args.end_date or '最新'}）...")
        fx_df = fetcher.get_fx_data_for_ccf(start_date=args.start_date, end_date=args.end_date)
        logger.info(f"   成功获取 {len(fx_df)} 个交易日的外汇数据")
    except Exception as e:
        logger.error(f"数据拉取失败: {e}")
        sys.exit(1)

    logger.info("2. 正在计算逆周期因子...")
    calculator = CCFCalculator(fx_df)
    result_df = calculator.calculate()

    if result_df.empty:
        logger.warning("计算结果为空，请检查输入行情数据")
        sys.exit(1)

    latest = result_df.iloc[-1]
    logger.info(
        f"   计算完成，共 {len(result_df)} 期，最新一期 {latest['Date'].strftime('%Y-%m-%d')} "
        f"CCF={latest['CCF_Value']:.4f}（{latest['Strength']}）"
    )

    logger.info(f"3. 保存数据到 CSV 文件: {args.output}...")
    columns = list(BASE_COLUMNS)
    for col in OPTIONAL_COLUMNS:
        if col in result_df.columns and result_df[col].notna().any():
            columns.insert(5, col)  # 紧跟在 DXY 之后，保持行情列聚在一起

    out_df = result_df[columns].copy()
    out_df["Date"] = out_df["Date"].dt.strftime("%Y-%m-%d")
    out_df.to_csv(args.output, index=False, encoding="utf-8", float_format="%.6f")
    logger.info(f"   成功写入 {args.output}（全量覆盖，幂等）")
    logger.info("任务结束。")


if __name__ == "__main__":
    main()

