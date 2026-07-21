import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="逆周期因子云端看板", layout="wide", page_icon="📈")

st.title("📈 逆周期因子 (CCF) 自动测算看板")
st.markdown("自动追踪人民币汇率每日中间价、计算逆周期因子，并对汇率影响成分进行归因拆解。")

DATA_FILE = "ccf_data.csv"


@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


df = load_data()

if df.empty:
    st.warning("暂无数据。请确保 `main.py` 已运行并生成了 `ccf_data.csv`。")
    st.stop()

# 最新的数据
latest_row = df.iloc[-1]
prev_row = df.iloc[-2] if len(df) > 1 else latest_row

# ================= 核心指标区 =================
st.subheader("📊 今日概览")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="中间价 (USDCNY_MID)",
              value=f"{latest_row['USDCNY_MID']:.4f}",
              delta=f"{latest_row['USDCNY_MID'] - prev_row['USDCNY_MID']:.4f}")
with col2:
    st.metric(label="逆周期因子 (CCF)",
              value=f"{latest_row['CCF_Value']:.4f}",
              delta=f"{latest_row['CCF_Value'] - prev_row['CCF_Value']:.4f}")
with col3:
    st.metric(label="强度评级", value=latest_row['Strength'])
with col4:
    st.metric(label="美元指数 (DXY)",
              value=f"{latest_row['DXY']:.2f}",
              delta=f"{latest_row['DXY'] - prev_row['DXY']:.2f}")

st.divider()

# ================= 历史趋势区 =================
st.subheader("📈 逆周期因子历史趋势")
fig_trend = px.line(df, x="Date", y="CCF_Value",
                    title="逆周期因子 (CCF) 时间序列",
                    markers=True, line_shape="spline")
fig_trend.add_hline(y=0, line_dash="dash", line_color="red")
st.plotly_chart(fig_trend, use_container_width=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("💱 人民币汇率走势")
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_MID"],
                                name="中间价", mode="lines"))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNY_SPOT"],
                                name="在岸即期", mode="lines"))
    fig_fx.add_trace(go.Scatter(x=df["Date"], y=df["USDCNH"],
                                name="离岸 CNH", mode="lines"))
    fig_fx.update_layout(title="USDCNY 中间价 / 在岸 / 离岸", hovermode="x unified")
    st.plotly_chart(fig_fx, use_container_width=True)

with col_chart2:
    st.subheader("🌐 美元指数走势")
    fig_dxy = px.line(df, x="Date", y="DXY", title="美元指数 (DXY) 时间序列")
    st.plotly_chart(fig_dxy, use_container_width=True)

# ================= 归因分解区 =================
st.subheader("🧩 归因分解")
col_attr1, col_attr2 = st.columns(2)

with col_attr1:
    st.markdown("**影响成分历史趋势**")
    fig_impact = go.Figure()
    for col_name in ["Basket_Impact", "DXY_Impact", "CNH_Impact"]:
        fig_impact.add_trace(go.Bar(x=df["Date"], y=df[col_name], name=col_name))
    fig_impact.update_layout(barmode="relative", hovermode="x unified",
                             title="篮子 / 美元 / 离岸影响（按交易日堆叠）")
    st.plotly_chart(fig_impact, use_container_width=True)

with col_attr2:
    st.markdown("**最新一期拆解**")
    categories = ['前日收盘基准', '篮子影响', '美元影响', '离岸影响', '逆周期因子']
    values = [
        latest_row['USDCNY_SPOT'],  # 基准以即期收盘为起点
        latest_row['Basket_Impact'],
        latest_row['DXY_Impact'],
        latest_row['CNH_Impact'],
        latest_row['CCF_Value']
    ]

    fig_waterfall = go.Figure(go.Waterfall(
        name="CCF Breakdown",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=categories,
        textposition="outside",
        text=[f"{v:.4f}" for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig_waterfall.update_layout(title="中间价形成机制归因拆解")
    st.plotly_chart(fig_waterfall, use_container_width=True)

# ================= 数据明细 =================
st.subheader("📋 历史数据明细")

format_map = {
    'USDCNY_MID': '{:.4f}',
    'USDCNY_SPOT': '{:.4f}',
    'USDCNH': '{:.4f}',
    'DXY': '{:.2f}',
    'EURUSD': '{:.4f}',
    'USDJPY': '{:.2f}',
    'GBPUSD': '{:.4f}',
    'USDCAD': '{:.4f}',
    'USDSEK': '{:.4f}',
    'USDCHF': '{:.4f}',
    'CFETS': '{:.2f}',
    'CCF_Value': '{:.4f}',
    'Basket_Impact': '{:.4f}',
    'DXY_Impact': '{:.4f}',
    'CNH_Impact': '{:.4f}',
}
# 仅对实际存在的列应用格式
format_map = {k: v for k, v in format_map.items() if k in df.columns}

st.dataframe(df.sort_values(by="Date", ascending=False).style.format(format_map),
             use_container_width=True)
