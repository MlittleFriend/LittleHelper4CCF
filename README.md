# 逆周期因子自动计算与云端看板 (CCF Auto-Dashboard)

本项目通过 iFind API 自动拉取每日外汇行情数据，计算人民币逆周期因子 (Counter-Cyclical Factor)，并通过 GitHub Actions 实现每日自动化运行，最终在 Streamlit 看板上进行可视化呈现。

## 🚀 功能特性
1. **自动获取数据**：基于 iFind API 获取 DXY、USDCNY、USDCNH 等外汇行情。
2. **归因计算**：自动剥离隔夜美元波动和一篮子货币的影响，估算央行逆周期因子力度。
3. **完全自动化**：借助 GitHub Actions，每天北京时间 9:15 自动更新数据并存入 GitHub 仓库。
4. **精美云端看板**：使用 Streamlit 展示因子走势和归因瀑布图。

## 📁 目录结构
- `data_fetcher.py`: iFind HTTP API 的封装模块。
- `calculator.py`: 逆周期因子算法与强度评估模块。
- `main.py`: 数据抓取 -> 计算 -> 写入 `ccf_data.csv` 的调度入口。
- `dashboard.py`: Streamlit 可视化应用。
- `.github/workflows/daily.yml`: GitHub Actions 自动更新配置。

## 🛠️ 如何部署到云端

### 第 1 步：上传至 GitHub 并在 Repository 中设置 Secret
1. 将所有文件（包括 `.github` 隐藏文件夹）上传到您自己的 GitHub 仓库。
2. 在该仓库的网页中点击 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。
3. **Name** 填入：`IFIND_REFRESH_TOKEN`
4. **Secret** 填入您获取到的 iFind refresh_token。
> *如此配置后，GitHub Actions 每天早盘会自动运行 `main.py`，并将最新的一条记录追加到 CSV 文件中。*

### 第 2 步：部署 Streamlit 看板
1. 访问 [Streamlit Community Cloud](https://share.streamlit.io/) 并用您的 GitHub 账号登录。
2. 点击 **New app**。
3. 选择刚才创建的 GitHub Repository，Branch 选 `main`，Main file path 填入 `dashboard.py`。
4. 点击 **Deploy**，系统将自动安装 `requirements.txt` 并发布在线实时看板。您的链接即可分享给全团队！

## ⚠️ 注意事项
- 在 `data_fetcher.py` 中，资产的代码(如 `USDCNY.EX`, `UDI.FX` 等)为示例代码。若 iFind 的权限或代码不同，请根据您账号的实际终端指标(thscode)进行微调。
- 本项目中的归因算法采用固定基准的简化估算，供参考，可进入 `calculator.py` 内部自行精调权重系数。
