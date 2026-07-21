import os
import sys

# 获取当前文件目录
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 关键：把 bin 文件夹加到 PATH，让 Python 能找到 DLL
# 改成你的 bin 文件夹实际路径
bin_path = r"C:\Users\cccz\AppData\Local\Temp\MicrosoftEdgeDownloads\457cc65c-1710-4480-90f7-1d87c8bd84dd\THSDataInterface_Windows_20260529.zip\THSDataInterface_Windows\bin\x86"  # 或 x64，看你系统
os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH', '')

import iFinDPy

print("导入成功")

api = iFinDPy.iFinDPy()
result = api.login("hfzqsh509", "U0GeB40e")
print(f"登录结果: {result}")

try:
    data = api.get_history_data("G0000007", "20240701", "20240721", "1D")
    print(f"数据: {data}")
except Exception as e:
    print(f"查询错误: {e}")