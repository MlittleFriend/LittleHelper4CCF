import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 页面基本设置
st.set_page_config(
    page_title="COUNTER-CYCLICAL FACTOR | TERMINAL",
    layout="wide",
    page_icon=None,
    initial_sidebar_state="expanded",
)

# 注入赛博朋克 / 科技风 HUD CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@400;600&display=swap');

    /* 全局深色科技风背景 */
    .stApp {
        background-color: #070b12;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background-color: #0d121f !important;
        border-right: 1px solid rgba(0, 240, 255, 0.15);
    }

    /* 主标题 HUD 风格 */
    .cyber-header {
        position: relative;
        padding: 20px 24px;
        background: linear-gradient(135deg, rgba(13, 18, 31, 0.9) 0%, rgba(7, 11, 18, 0.95) 100%);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-left: 4px solid #00f0ff;
        border-radius: 6px;
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.08);
        margin-bottom: 25px;
    }

    .cyber-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00f0ff 0%, #7000ff 50%, #ff0055 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        margin: 0;
    }

    .cyber-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.05rem;
        color: #94a3b8;
        letter-spacing: 1px;
        margin-top: 6px;
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
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #00f0ff;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }

    .section-label::before {
        content: "//";
        color: #ff0055;
        margin-right: 8px;
        font-weight: 900;
    }

    /* 评级 Cyber Badges */
    .badge-cyber {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 4px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .badge-strong {
        background: rgba(255, 0, 85, 0.15);
        color: #ff0055;
        border: 1px solid #ff0055;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
    }

    .badge-medium {
        background: rgba(252, 238, 10, 0.15);
        color: #fcee0a;
        border: 1px solid #fcee0a;
        box-shadow: 0 0 10px rgba(252, 238, 10, 0.4);
    }

    .badge-weak {
        background: rgba(0, 240, 255, 0.15);
        color: #00f0ff;
        border: 1px solid #00f0ff;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
    }

    /* 自定义按钮风格 */
    div.stButton > button {
        background: linear-gradient(90deg, rgba(0, 240, 255, 0.1) 0%, rgba(112, 0, 255, 0.2) 100%) !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 4px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover {
        background: #00f0ff !important;
        color: #070b12 !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
    }

    /* Streamlit Metric 组件暗色重置 */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #ffffff !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif !important;
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    st.error("CRITICAL ERROR: NO DATA SOURCE FOUND. RUN main.py TO GENERATE ccf_data.csv")
    st.stop()

# 侧边栏：HUD 级控制台
with st.sidebar:
    st.markdown('<div class="section-label">SYSTEM CONTROLS</div>', unsafe_allow_html=True)

    st.markdown("<p style='font-family: Rajdhani; color: #94a3b8;'>TIME HORIZON FILTER</p>", unsafe_allow_html=True)
    time_preset = st.radio(
        "RANGE SELECTION",
        ["1M", "3M", "1Y", "ALL", "CUSTOM"],
        index=3,
        label_visibility="collapsed",
    )

    max_date = df_raw["Date"].max().date()
    min_date = df_raw["Date"].min().date()

    if time_preset == "1M":
        start_date = max_date - timedelta(days=30)
        end_date = max_date
    elif time_preset == "3M":
        start_date = max_date - timedelta(days=90)
        end_date = max_date
    elif time_preset == "1Y":
        start_date = max_date - timedelta(days=365)
        end_date = max_date
    elif time_preset == "ALL":
        start_date = min_date
        end_date = max_date
    else:
        date_range = st.date_input(
            "CUSTOM RANGE",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

    st.divider()
    st.markdown('<div class="section-label">DATA EXPORT</div>', unsafe_allow_html=True)
    csv_data = df_raw.to_csv(index=False, float_format="%.6f").encode("utf-8")
    st.download_button(
        label="EXPORT CSV DATASTREAM",
        data=csv_data,
        file_name="ccf_data_export.csv",
        mime="text/csv",
    )

# 过滤数据
mask = (df_raw["Date"].dt.date >= start_date) & (df_raw["Date"].dt.date <= end_date)
df = df_raw.loc[mask].copy()

if df.empty:
    st.info("NO DATA AVAILABLE FOR SELECTED TIMEFRAME.")
    st.stop()

# 页面头部（HUD Terminal 界面）
st.markdown(
    f"""
    <div class="cyber-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="cyber-title">CCF TERMINAL v1.0</div>
            <div style="font-family: Orbitron; font-size: 0.85rem; color: #00ff66;">
                <span class="pulse-dot"></span>LIVE FEED STREAM
            </div>
        </div>
        <div class="cyber-subtitle">COUNTER-CYCLICAL FACTOR QUANTITATIVE MODEL & ATTRIBUTION SYSTEM</div>
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
    font=dict(family="Rajdhani, sans-serif", color="#cbd5e1", size=13),
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
st.markdown(f'<div class="section-label">LATEST METRICS HUD [{latest_row["Date"].strftime("%Y-%m-%d")}]</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="USDCNY MID RATE",
        value=f"{latest_row['USDCNY_MID']:.4f}",
        delta=f"{latest_row['USDCNY_MID'] - prev_row['USDCNY_MID']:.4f}",
    )
with col2:
    st.metric(
        label="CCF VALUE (BP)",
        value=f"{latest_row['CCF_Value']:.4f}",
        delta=f"{latest_row['CCF_Value'] - prev_row['CCF_Value']:.4f}",
    )
with col3:
    strength_val = latest_row["Strength"]
    badge_cls = "badge-strong" if strength_val == "强" else ("badge-medium" if strength_val == "中" else "badge-weak")
    st.markdown(
        f"""
        <div style="padding-top: 4px;">
            <div style="font-family: Rajdhani; color: #94a3b8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px;">STRENGTH RATING</div>
            <div style="margin-top: 10px;"><span class="badge-cyber {badge_cls}">{strength_val} / {strength_val.upper()} LEVEL</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.metric(
        label="DXY INDEX",
        value=f"{latest_row['DXY']:.2f}",
        delta=f"{latest_row['DXY'] - prev_row['DXY']:.2f}",
    )

st.divider()

# ================= 历史趋势区 =================
st.markdown('<div class="section-label">CCF TIME SERIES ANALYSIS</div>', unsafe_allow_html=True)

fig_trend = px.line(
    df,
    x="Date",
    y="CCF_Value",
    markers=True,
    line_shape="spline",
)
fig_trend.update_traces(line_color="#00f0ff", line_width=2.5, marker=dict(size=5, color="#ff0055"))
fig_trend.add_hline(y=0, line_dash="dash", line_color="#ff0055", annotation_text="ZERO BASELINE", annotation_font_color="#ff0055")
fig_trend.update_layout(**CYBER_PLOT_LAYOUT, title="COUNTER-CYCLICAL FACTOR HISTORICAL DYNAMICS", hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="section-label">EXCHANGE RATE DYNAMICS</div>', unsafe_allow_html=True)
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_MID"], name="MID RATE", mode="lines", line=dict(color="#00f0ff", width=2)))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_SPOT"], name="ONSHORE SPOT", mode="lines", line=dict(color="#ff0055", width=2)))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNH"], name="OFFSHORE CNH", mode="lines", line=dict(color="#00ff66", width=2)))
    fig_fx.update_layout(**CYBER_PLOT_LAYOUT, title="USDCNY MID / SPOT / CNH COMPREHENSIVE VIEW", hovermode="x unified")
    st.plotly_chart(fig_fx, use_container_width=True)

with col_chart2:
    st.markdown('<div class="section-label">DOLLAR INDEX DYNAMICS</div>', unsafe_allow_html=True)
    fig_dxy = px.line(df, x="Date", y="DXY")
    fig_dxy.update_traces(line_color="#fcee0a", line_width=2)
    fig_dxy.update_layout(**CYBER_PLOT_LAYOUT, title="US DOLLAR INDEX (DXY) DYNAMICS", hovermode="x unified")
    st.plotly_chart(fig_dxy, use_container_width=True)

# ================= 归因分解区 =================
st.markdown('<div class="section-label">QUANTITATIVE ATTRIBUTION BREAKDOWN</div>', unsafe_allow_html=True)
col_attr1, col_attr2 = st.columns(2)

with col_attr1:
    st.markdown("<p style='font-family: Rajdhani; color: #00f0ff; font-weight: 700;'>STACKED IMPACT COMPONENTS</p>", unsafe_allow_html=True)
    fig_impact = go.Figure()
    color_map = {"Basket_Impact": "#00f0ff", "DXY_Impact": "#fcee0a", "CNH_Impact": "#ff0055"}
    label_map = {"Basket_Impact": "BASKET IMPACT", "DXY_Impact": "DXY IMPACT", "CNH_Impact": "CNH SPREAD IMPACT"}

    for col_name in ["Basket_Impact", "DXY_Impact", "CNH_Impact"]:
        if col_name in df.columns:
            fig_impact.add_trace(go.Bar(x=df["Date"], y=df[col_name], name=label_map.get(col_name, col_name), marker_color=color_map.get(col_name, "#00f0ff")))
    fig_impact.update_layout(**CYBER_PLOT_LAYOUT, barmode="relative", hovermode="x unified", title="HISTORICAL DRIVER COMPONENTS")
    st.plotly_chart(fig_impact, use_container_width=True)

with col_attr2:
    st.markdown(f"<p style='font-family: Rajdhani; color: #00f0ff; font-weight: 700;'>LATEST WATERFALL DISSECTION [{latest_row['Date'].strftime('%Y-%m-%d')}]</p>", unsafe_allow_html=True)
    categories = ["PREV SPOT BASE", "BASKET IMPACT", "DXY IMPACT", "CNH IMPACT", "CCF VALUE"]
    values = [
        latest_row["USDCNY_SPOT"],
        latest_row["Basket_Impact"],
        latest_row["DXY_Impact"],
        latest_row["CNH_Impact"],
        latest_row["CCF_Value"],
    ]

    fig_waterfall = go.Figure(
        go.Waterfall(
            name="ATTRIBUTION",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=categories,
            textposition="outside",
            text=[f"{v:.4f}" for v in values],
            y=values,
            connector={"line": {"color": "rgba(0, 240, 255, 0.5)", "width": 1.5}},
            increasing={"marker": {"color": "#00ff66"}},
            decreasing={"marker": {"color": "#ff0055"}},
            totals={"marker": {"color": "#00f0ff"}},
        )
    )
    fig_waterfall.update_layout(**CYBER_PLOT_LAYOUT, title="MID RATE FORMATION WATERFALL MECHANISM")
    st.plotly_chart(fig_waterfall, use_container_width=True)

# ================= 数据明细 =================
st.markdown('<div class="section-label">HISTORICAL DATASTREAM MATRIX</div>', unsafe_allow_html=True)

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


