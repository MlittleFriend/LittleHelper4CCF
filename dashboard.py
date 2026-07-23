import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 页面基本设置
st.set_page_config(
    page_title="逆周期因子分析小帮手 | CCF TERMINAL",
    layout="wide",
    page_icon=None,
    initial_sidebar_state="expanded",
)

# 注入赛博朋克 / 科技风 HUD CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

    /* 全局深色科技风背景 */
    .stApp {
        background-color: #070b12;
        color: #e2e8f0;
        font-family: 'Noto Sans SC', 'Inter', sans-serif;
    }

    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background-color: #0d121f !important;
        border-right: 1px solid rgba(0, 240, 255, 0.15);
    }

    /* 主标题 HUD 风格 */
    .cyber-header {
        position: relative;
        padding: 22px 26px;
        background: linear-gradient(135deg, rgba(13, 18, 31, 0.9) 0%, rgba(7, 11, 18, 0.95) 100%);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-left: 5px solid #00f0ff;
        border-radius: 6px;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.08);
        margin-bottom: 25px;
    }

    .cyber-title {
        font-family: 'Orbitron', 'Noto Sans SC', sans-serif;
        font-size: 2.1rem;
        font-weight: 900;
        letter-spacing: 1px;
        color: #00f0ff;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.35);
        margin: 0;
    }

    .cyber-subtitle {
        font-family: 'Noto Sans SC', 'Rajdhani', sans-serif;
        font-size: 0.98rem;
        color: #94a3b8;
        letter-spacing: 0.5px;
        margin-top: 8px;
    }

    /* 实时数据闪烁指示灯 */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00ff66;
        box-shadow: 0 0 10px #00ff66;
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(0, 255, 102, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0); }
    }

    /* 小标题 HUD 风格 */
    .section-label {
        font-family: 'Noto Sans SC', 'Orbitron', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #00f0ff;
        letter-spacing: 1px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }

    .section-label::before {
        content: "//";
        color: #ff0055;
        margin-right: 10px;
        font-weight: 900;
        font-family: 'Orbitron';
    }

    /* 评级 Cyber Badges */
    .badge-cyber {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 4px;
        font-family: 'Orbitron', 'Noto Sans SC', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .badge-strong {
        background: rgba(255, 0, 85, 0.15);
        color: #ff0055;
        border: 1px solid #ff0055;
        box-shadow: 0 0 12px rgba(255, 0, 85, 0.4);
    }

    .badge-medium {
        background: rgba(252, 238, 10, 0.15);
        color: #fcee0a;
        border: 1px solid #fcee0a;
        box-shadow: 0 0 12px rgba(252, 238, 10, 0.4);
    }

    .badge-weak {
        background: rgba(0, 240, 255, 0.15);
        color: #00f0ff;
        border: 1px solid #00f0ff;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
    }

    /* 自定义按钮风格 */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, rgba(0, 240, 255, 0.12) 0%, rgba(168, 85, 247, 0.2) 100%) !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 4px !important;
        font-family: 'Noto Sans SC', 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: #00f0ff !important;
        color: #070b12 !important;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.6) !important;
    }

    /* Streamlit Metric 组件暗色重置 */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #ffffff !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Noto Sans SC', 'Rajdhani', sans-serif !important;
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px;
    }

    /* 分割线 */
    hr {
        border-color: rgba(0, 240, 255, 0.15) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = "ccf_data.csv"


@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


df_raw = load_data()

if df_raw.empty:
    st.error("严重错误：未找到数据文件。请先运行 main.py 生成 ccf_data.csv")
    st.stop()

# 侧边栏：控制台
with st.sidebar:
    st.markdown('<div class="section-label">控制面板</div>', unsafe_allow_html=True)

    st.markdown("<p style='font-family: Noto Sans SC; color: #94a3b8; font-size: 0.9rem;'>时间范围筛选</p>", unsafe_allow_html=True)
    time_preset = st.radio(
        "快捷选择区间",
        ["近1个月", "近3个月", "近1年", "全部", "自定义"],
        index=3,
        label_visibility="collapsed",
    )

    max_date = df_raw["Date"].max().date()
    min_date = df_raw["Date"].min().date()

    if time_preset == "近1个月":
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    elif time_preset == "近3个月":
        start_date = max_date - timedelta(days=90)
        end_date = max_date
    elif time_preset == "近1年":
        start_date = max_date - timedelta(days=365)
        end_date = max_date
    elif time_preset == "全部":
        start_date = min_date
        end_date = max_date
    else:
        date_range = st.date_input(
            "选择自定义区间",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

    st.divider()
    st.markdown('<div class="section-label">数据导出</div>', unsafe_allow_html=True)
    csv_data = df_raw.to_csv(index=False, float_format="%.6f").encode("utf-8")
    st.download_button(
        label="导出全量 CSV 数据集",
        data=csv_data,
        file_name="ccf_data_export.csv",
        mime="text/csv",
    )

# 过滤数据
mask = (df_raw["Date"].dt.date >= start_date) & (df_raw["Date"].dt.date <= end_date)
df = df_raw.loc[mask].copy()

if df.empty:
    st.info("选定时间范围内暂无有效数据。")
    st.stop()

# 页面头部（HUD 科技界面）
st.markdown(
    f"""
    <div class="cyber-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="cyber-title">逆周期因子定量分析终端</div>
            <div style="font-family: Orbitron, Noto Sans SC; font-size: 0.85rem; color: #00ff66;">
                <span class="pulse-dot"></span>实时行情流
            </div>
        </div>
        <div class="cyber-subtitle">自动追踪人民币汇率每日中间价、计算逆周期因子力度，并对多维驱动成分进行定量归因拆解</div>
    </div>
    """,
    unsafe_allow_html=True,
)

latest_row = df_raw.iloc[-1]
prev_row = df_raw.iloc[-2] if len(df_raw) > 1 else latest_row

# 统一 Plotly 暗色 Cyber 主题布局参数
CYBER_PLOT_LAYOUT = dict(
    paper_bgcolor="#070b12",
    plot_bgcolor="#0d121f",
    font=dict(family="Noto Sans SC, Rajdhani, sans-serif", color="#cbd5e1", size=13),
    xaxis=dict(
        gridcolor="rgba(0, 240, 255, 0.08)",
        zerolinecolor="rgba(0, 240, 255, 0.2)",
        linecolor="rgba(0, 240, 255, 0.3)",
    ),
    yaxis=dict(
        gridcolor="rgba(0, 240, 255, 0.08)",
        zerolinecolor="rgba(0, 240, 255, 0.2)",
        linecolor="rgba(0, 240, 255, 0.3)",
    ),
    legend=dict(
        bgcolor="rgba(13, 18, 31, 0.8)",
        bordercolor="rgba(0, 240, 255, 0.3)",
        borderwidth=1,
    ),
    margin=dict(l=30, r=30, t=50, b=30),
)

# ================= 核心指标区 =================
st.markdown(f'<div class="section-label">今日行情概览 [{latest_row["Date"].strftime("%Y-%m-%d")}]</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="中间价 (USDCNY_MID)",
        value=f"{latest_row['USDCNY_MID']:.4f}",
        delta=f"{latest_row['USDCNY_MID'] - prev_row['USDCNY_MID']:.4f}",
    )
with col2:
    st.metric(
        label="逆周期因子 (CCF)",
        value=f"{latest_row['CCF_Value']:.4f}",
        delta=f"{latest_row['CCF_Value'] - prev_row['CCF_Value']:.4f}",
    )
with col3:
    strength_val = latest_row["Strength"]
    badge_cls = "badge-strong" if strength_val == "强" else ("badge-medium" if strength_val == "中" else "badge-weak")
    st.markdown(
        f"""
        <div style="padding-top: 4px;">
            <div style="font-family: Noto Sans SC; color: #94a3b8; font-size: 0.95rem; letter-spacing: 0.5px;">干预强度评级</div>
            <div style="margin-top: 10px;"><span class="badge-cyber {badge_cls}">{strength_val} 评级 / LEVEL {strength_val}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.metric(
        label="美元指数 (DXY)",
        value=f"{latest_row['DXY']:.2f}",
        delta=f"{latest_row['DXY'] - prev_row['DXY']:.2f}",
    )

st.divider()

# ================= 历史趋势区 =================
st.markdown('<div class="section-label">逆周期因子历史趋势分析</div>', unsafe_allow_html=True)

fig_trend = px.line(
    df,
    x="Date",
    y="CCF_Value",
    markers=True,
    line_shape="spline",
)
fig_trend.update_traces(line_color="#00f0ff", line_width=2.5, marker=dict(size=5, color="#ff0055"))
fig_trend.add_hline(y=0, line_dash="dash", line_color="#ff0055", annotation_text="0 轴中性基准", annotation_font_color="#ff0055")
fig_trend.update_layout(**CYBER_PLOT_LAYOUT, title="逆周期因子 (CCF) 时间序列动态走势", hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="section-label">人民币汇率走势对比</div>', unsafe_allow_html=True)
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_MID"], name="中间价", mode="lines", line=dict(color="#00f0ff", width=2)))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_SPOT"], name="在岸即期", mode="lines", line=dict(color="#ff0055", width=2)))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNH"], name="离岸 CNH", mode="lines", line=dict(color="#00ff66", width=2)))
    fig_fx.update_layout(**CYBER_PLOT_LAYOUT, title="USDCNY 中间价 / 在岸即期 / 离岸 CNH 综合对比", hovermode="x unified")
    st.plotly_chart(fig_fx, use_container_width=True)

with col_chart2:
    st.markdown('<div class="section-label">美元指数走势分析</div>', unsafe_allow_html=True)
    fig_dxy = px.line(df, x="Date", y="DXY")
    fig_dxy.update_traces(line_color="#fcee0a", line_width=2)
    fig_dxy.update_layout(**CYBER_PLOT_LAYOUT, title="美元指数 (DXY) 历史时间序列", hovermode="x unified")
    st.plotly_chart(fig_dxy, use_container_width=True)

# ================= 归因分解区 =================
st.markdown('<div class="section-label">驱动成分定量归因拆解</div>', unsafe_allow_html=True)
col_attr1, col_attr2 = st.columns(2)

with col_attr1:
    st.markdown("<p style='font-family: Noto Sans SC; color: #00f0ff; font-weight: 700;'>驱动成分历史变动趋势 (单位: 点/BP)</p>", unsafe_allow_html=True)
    fig_impact = go.Figure()
    color_map = {"Basket_Impact": "#00f0ff", "DXY_Impact": "#fcee0a", "CNH_Impact": "#ff0055"}
    label_map = {"Basket_Impact": "一篮子货币影响", "DXY_Impact": "美元指数直接影响", "CNH_Impact": "离岸价差影响"}

    for col_name in ["Basket_Impact", "DXY_Impact", "CNH_Impact"]:
        if col_name in df.columns:
            # 乘以 10000 转换为外汇交易常用的点子/基点 (Pips / BP)
            bp_series = df[col_name] * 10000
            fig_impact.add_trace(go.Bar(x=df["Date"], y=bp_series, name=label_map.get(col_name, col_name), marker_color=color_map.get(col_name, "#00f0ff")))
    fig_impact.update_layout(**CYBER_PLOT_LAYOUT, barmode="relative", hovermode="x unified", title="篮子 / 美元 / 离岸影响历史时间序列 (点/BP)")
    st.plotly_chart(fig_impact, use_container_width=True)

with col_attr2:
    st.markdown(f"<p style='font-family: Noto Sans SC; color: #00f0ff; font-weight: 700;'>最新一期因子贡献对比 [{latest_row['Date'].strftime('%Y-%m-%d')}]</p>", unsafe_allow_html=True)

    # 将最新一期影响幅度转换为点数 (BP, 1BP = 0.0001)
    basket_bp = latest_row["Basket_Impact"] * 10000
    dxy_bp = latest_row["DXY_Impact"] * 10000
    cnh_bp = latest_row["CNH_Impact"] * 10000
    ccf_bp = latest_row["CCF_Value"] * 10000

    attr_names = ["一篮子货币影响", "美元指数直接影响", "离岸价差影响", "逆周期因子 (CCF)"]
    attr_bps = [basket_bp, dxy_bp, cnh_bp, ccf_bp]
    attr_raws = [latest_row["Basket_Impact"], latest_row["DXY_Impact"], latest_row["CNH_Impact"], latest_row["CCF_Value"]]

    # 条形颜色：正值量子绿 #00ff66（贬值/调升方向），负值赛博红 #ff0055（升值/调降方向），CCF用电光青 #00f0ff / 亮紫 #a855f7
    colors = []
    for name, bp in zip(attr_names, attr_bps):
        if "CCF" in name:
            colors.append("#00f0ff" if bp >= 0 else "#a855f7")
        else:
            colors.append("#00ff66" if bp >= 0 else "#ff0055")

    text_labels = [f"{bp:+.1f} 点 ({raw:+.4f})" for bp, raw in zip(attr_bps, attr_raws)]

    fig_attr_bar = go.Figure(
        go.Bar(
            y=attr_names,
            x=attr_bps,
            orientation="h",
            text=text_labels,
            textposition="auto",
            marker=dict(color=colors, line=dict(color="rgba(0, 240, 255, 0.4)", width=1)),
        )
    )

    fig_attr_bar.add_vline(x=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.4)")
    fig_attr_bar.update_layout(
        **CYBER_PLOT_LAYOUT,
        title="各因子对中间价影响力度对比 (单位: 点/BP)",
        xaxis_title="影响力度 (正向: 上调/贬值方向 | 负向: 下调/升值对冲)",
    )
    fig_attr_bar.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_attr_bar, use_container_width=True)

# 形成机制数学推演 HUD 说明卡片
prev_spot_val = latest_row["USDCNY_SPOT"]
mid_val = latest_row["USDCNY_MID"]
theory_mid = prev_spot_val + latest_row["Basket_Impact"] + latest_row["DXY_Impact"] + latest_row["CNH_Impact"]

st.markdown(
    f"""
    <div style="background: rgba(13, 18, 31, 0.85); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 6px; padding: 14px 20px; margin-bottom: 25px;">
        <div style="font-family: Orbitron, Noto Sans SC; font-size: 0.95rem; color: #00f0ff; font-weight: 700; margin-bottom: 6px;">
            // 中间价形成机制公式推演 ({latest_row['Date'].strftime('%Y-%m-%d')})
        </div>
        <div style="font-family: Noto Sans SC; font-size: 0.9rem; color: #cbd5e1; line-height: 1.6;">
            前日收盘价 (<b>{prev_spot_val:.4f}</b>) 
            + 篮子影响 (<b>{basket_bp:+.1f} 点</b>) 
            + 美元影响 (<b>{dxy_bp:+.1f} 点</b>) 
            + 离岸影响 (<b>{cnh_bp:+.1f} 点</b>) 
            = 理论中间价 (<b>{theory_mid:.4f}</b>)<br>
            实际中间价 (<b>{mid_val:.4f}</b>) - 理论中间价 (<b>{theory_mid:.4f}</b>) 
            = <span style="color: #00f0ff; font-weight: 700;">逆周期因子 CCF 为 {ccf_bp:+.1f} 点 ({latest_row['CCF_Value']:+.4f})</span> 
            [干预强度: <span style="color: #fcee0a; font-weight: 700;">{latest_row['Strength']}</span>]
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ================= 数据明细 =================
st.markdown('<div class="section-label">历史行情数据明细矩阵</div>', unsafe_allow_html=True)

format_map = {
    "USDCNY_MID": "{:.4f}",
    "USDCNY_SPOT": "{:.4f}",
    "USDCNH": "{:.4f}",
    "DXY": "{:.2f}",
    "EURUSD": "{:.4f}",
    "USDJPY": "{:.2f}",
    "GBPUSD": "{:.4f}",
    "USDCAD": "{:.4f}",
    "USDSEK": "{:.4f}",
    "USDCHF": "{:.4f}",
    "CFETS": "{:.2f}",
    "CCF_Value": "{:.4f}",
    "Basket_Impact": "{:.4f}",
    "DXY_Impact": "{:.4f}",
    "CNH_Impact": "{:.4f}",
}
format_map = {k: v for k, v in format_map.items() if k in df.columns}

st.dataframe(
    df.sort_values(by="Date", ascending=False).style.format(format_map),
    use_container_width=True,
)



