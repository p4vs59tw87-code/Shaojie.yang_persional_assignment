# app.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from data_fetcher import fetch_crsp_data
from volatility_calculator import calculate_volatility

st.set_page_config(layout="wide")
st.title("📊 个股波动率与风险分析看板")
st.markdown("数据来源：WRDS CRSP 数据库")

with st.sidebar:
    st.header("参数设置")
    
    # 添加 WRDS 账户输入（放在最上面，因为必须先有账户才能取数据）
    st.subheader("🔐 WRDS 账户")
    wrds_user = st.text_input("WRDS 用户名 (邮箱)", type="default")
    wrds_pass = st.text_input("WRDS 密码", type="password")
    
    st.subheader("📈 股票参数")
    ticker = st.text_input("股票代码", "AAPL").upper()
    start_date = st.date_input("开始日期", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("结束日期", value=pd.to_datetime("2024-12-31"))
    window = st.slider("滚动波动率窗口（天）", 10, 60, 30)
    load_button = st.button("🚀 加载数据")

if load_button:
    # 检查是否输入了 WRDS 账户
    if not wrds_user or not wrds_pass:
        st.error("请先在左侧输入您的 WRDS 用户名和密码")
        st.stop()
    
    with st.spinner(f"正在从WRDS获取 {ticker} 数据..."):
        raw_data = fetch_crsp_data(ticker, start_date, end_date, wrds_user, wrds_pass)
    
    if raw_data.empty:
        st.stop()
    
    # 后续代码不变（计算波动率、绘图等）...
    analyzed_data = calculate_volatility(raw_data, window)
    company_name = analyzed_data.attrs.get('company_name', ticker)
    
    st.header(f"{company_name} ({ticker}) 风险分析报告")
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("最新价格", f"${analyzed_data['prc'].iloc[-1]:.2f}")
    with col2:
        latest_vol = analyzed_data['rolling_volatility'].dropna().iloc[-1]
        st.metric("最新年化波动率", f"{latest_vol:.2%}")
    with col3:
        sharpe = analyzed_data.attrs.get('sharpe_ratio', np.nan)
        st.metric("年化夏普比率", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")
    with col4:
        mdd = analyzed_data.attrs.get('overall_max_drawdown', np.nan)
        st.metric("历史最大回撤", f"{mdd:.2%}")
    
    # 价格走势
    st.subheader("📈 历史收盘价")
    fig_price = px.line(analyzed_data, x='date', y='prc', 
                        title=f"{ticker} 收盘价走势",
                        labels={'date': '日期', 'prc': '价格 (USD)'})
    st.plotly_chart(fig_price, width='stretch')
    
    # 波动率走势
    st.subheader("📉 滚动年化波动率")
    fig_vol = px.line(analyzed_data, x='date', y='rolling_volatility',
                      title=f"{window}天滚动年化波动率",
                      labels={'date': '日期', 'rolling_volatility': '年化波动率'})
    fig_vol.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_vol, width='stretch')
    
    # 日收益率分布
    st.subheader("📊 日收益率分布")
    fig_hist = px.histogram(analyzed_data, x='daily_return', nbins=50,
                            title="日收益率直方图",
                            labels={'daily_return': '日收益率'})
    fig_hist.update_xaxis(tickformat=".1%")
    st.plotly_chart(fig_hist, width='stretch')
    
    # 数据表格
    with st.expander("查看原始数据"):
        st.dataframe(analyzed_data[['date', 'prc', 'daily_return', 'rolling_volatility']].round(4))

else:
    st.info("👈 请在左侧输入您的 WRDS 账户和股票参数，然后点击「加载数据」")