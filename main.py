import os
import csv
from datetime import datetime
from data_fetcher import IFindDataFetcher
from calculator import CCFCalculator

# 获取环境变量中的 token (供 GitHub Actions 运行使用)
# 如果本地测试，可以退化为硬编码或在此处填入测试 token
REFRESH_TOKEN = os.environ.get("IFIND_REFRESH_TOKEN", "YOUR_TEST_TOKEN_HERE")
DATA_FILE = "ccf_data.csv"

def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Date", "USDCNY_MID", "USDCNY_SPOT", "USDCNH", "DXY", 
                "Basket_Impact", "DXY_Impact", "CNH_Impact", "CCF_Value", "Strength"
            ])

def main():
    print(f"[{datetime.now()}] 启动逆周期因子计算流水线...")
    
    if REFRESH_TOKEN == "YOUR_TEST_TOKEN_HERE":
        print("警告：未使用真实的环境变量 IFIND_REFRESH_TOKEN。如果是本地运行，请在代码中替换或配置环境变量。")
    
    fetcher = IFindDataFetcher(REFRESH_TOKEN)
    
    try:
        print("1. 正在抓取 iFind 数据...")
        data = fetcher.get_fx_data_for_ccf()
        print(f"   成功获取外汇数据: {data}")
    except Exception as e:
        print(f"数据拉取失败: {e}")
        return

    print("2. 正在计算逆周期因子...")
    calculator = CCFCalculator(data)
    result = calculator.calculate()
    print(f"   计算完成，结果强度为: {result['Strength']}")
    
    print("3. 保存数据到 CSV...")
    init_csv()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            today_str,
            result["USDCNY_MID"],
            result["USDCNY_SPOT"],
            result["USDCNH"],
            result["DXY"],
            result["Basket_Impact"],
            result["DXY_Impact"],
            result["CNH_Impact"],
            result["CCF_Value"],
            result["Strength"]
        ])
    print(f"   成功写入 {DATA_FILE}")
    print(f"[{datetime.now()}] 任务结束。")

if __name__ == "__main__":
    main()
