# data_fetcher.py
import psycopg2
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_crsp_data(ticker, start_date, end_date, wrds_username, wrds_password):
    """
    从WRDS CRSP数据库获取指定股票代码的日度数据
    需要传入用户的 WRDS 用户名和密码
    """
    try:
        conn = psycopg2.connect(
            host="wrds-pgdata.wharton.upenn.edu",
            port=9737,
            database="wrds",
            user=wrds_username,
            password=wrds_password
        )
        
        # 根据ticker找permno
        query_permno = f"""
            SELECT permno, ticker, comnam 
            FROM crsp.stocknames 
            WHERE ticker = '{ticker}'
        """
        permno_df = pd.read_sql(query_permno, conn)
        
        if permno_df.empty:
            st.error(f"未找到股票代码 {ticker}")
            conn.close()
            return pd.DataFrame()
        
        permno = permno_df.iloc[0]['permno']
        company_name = permno_df.iloc[0]['comnam']
        
        # 获取日度数据
        query_data = f"""
            SELECT date, prc, ret, vol
            FROM crsp.dsf
            WHERE permno = {permno}
              AND date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY date
        """
        df = pd.read_sql(query_data, conn, parse_dates=['date'])
        conn.close()
        
        if df.empty:
            st.warning(f"{ticker} 在所选日期范围内无数据")
            return pd.DataFrame()
        
        df['prc'] = df['prc'].abs()
        df['ret'] = df['ret'].astype(float).fillna(0)
        df.attrs['company_name'] = company_name
        return df
    
    except Exception as e:
        st.error(f"数据获取失败: {e}")
        return pd.DataFrame()