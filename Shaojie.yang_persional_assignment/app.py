# app.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from data_fetcher import fetch_crsp_data
from volatility_calculator import calculate_volatility

st.set_page_config(layout="wide")
st.title("📊 Individual stock volatility and risk analysis board")
st.markdown("Data source: WRDS CRSP database")

with st.sidebar:
    st.header("Parameter settings")
    ticker = st.text_input("Stock code", "AAPL").upper()
    start_date = st.date_input("Start date", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("End date", value=pd.to_datetime("2024-12-31"))
    window = st.slider("Scrolling window (days)", 10, 60, 30)
    load_button = st.button("🚀 Load data")

if load_button:
    with st.spinner(f"Getting wrds data from {ticker} ..."):
        raw_data = fetch_crsp_data(ticker, start_date, end_date)
    
    if raw_data.empty:
        st.stop()
    
    analyzed_data = calculate_volatility(raw_data, window)
    company_name = analyzed_data.attrs.get('company_name', ticker)
    
    st.header(f"{company_name} ({ticker}) Risk Analysis Report")
    
    # Indicators
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Latest Price", f"${analyzed_data['prc'].iloc[-1]:.2f}")
    with col2:
        latest_vol = analyzed_data['rolling_volatility'].dropna().iloc[-1]
        st.metric("Latest Annualized Volatility", f"{latest_vol:.2%}")
    with col3:
        sharpe = analyzed_data.attrs.get('sharpe_ratio', np.nan)
        st.metric("Annualized Sharpe Ratio", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")
    with col4:
        mdd = analyzed_data.attrs.get('overall_max_drawdown', np.nan)
        st.metric("Historical Maximum Drawdown", f"{mdd:.2%}")
    
    # Price trend
    st.subheader("📈 Historical closing prices")
    fig_price = px.line(analyzed_data, x='date', y='prc', 
                        title=f"{ticker} Closing price trend",
                        labels={'date': 'Date', 'prc': 'Price (USD)'})
    st.plotly_chart(fig_price, width='stretch')
    
    # Rolling volatility
    st.subheader("📉 Rolling Annualized Volatility")
    fig_vol = px.line(analyzed_data, x='date', y='rolling_volatility',
                      title=f"{window}Daily rolling annualized volatility",
                      labels={'date': 'Date', 'rolling_volatility': 'Annualized Volatility'})
    fig_vol.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_vol, width='stretch')
    
    # Daily return distribution
    st.subheader("📊 Daily Return Distribution")
    fig_hist = px.histogram(analyzed_data, x='daily_return', nbins=50,
                            title="Daily return distribution",
                            labels={'daily_return': 'Daily Return'})
    fig_hist.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig_hist, width='stretch')
    
    # Dataframe
    with st.expander("View detailed data"):
        st.dataframe(analyzed_data[['date', 'prc', 'daily_return', 'rolling_volatility']].round(4))

else:
    st.info("👈 Please enter a stock code and date range, then click 'Load data'")