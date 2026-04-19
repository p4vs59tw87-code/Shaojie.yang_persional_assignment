# data_fetcher.py
import psycopg2
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_crsp_data(ticker, start_date, end_date):
    """
    Obtain daily stock data from WRDS CRSP database for a given ticker and date range.
    Returns a DataFrame with columns: date, prc (price), ret (return), vol (volume).
    """
    try:
        # 1. Get WRDS credentials from Streamlit secrets
        wrds_username = st.secrets["wrds"]["username"]
        wrds_password = st.secrets["wrds"]["password"]

        # 2. Establish database connection
        conn = psycopg2.connect(
            host="wrds-pgdata.wharton.upenn.edu",
            port=9737,
            database="wrds",
            user=wrds_username,
            password=wrds_password
        )

        # 3. Find the PERMNO for the given ticker
        query_permno = f"""
            SELECT permno, ticker, comnam 
            FROM crsp.stocknames 
            WHERE ticker = '{ticker}'
        """
        permno_df = pd.read_sql(query_permno, conn)

        if permno_df.empty:
            st.error(f"Did not find stock code {ticker}")
            return pd.DataFrame()

        permno = permno_df.iloc[0]['permno']
        company_name = permno_df.iloc[0]['comnam']

        # 4. Get daily price, return, and volume data for the specified date range
        query_data = f"""
            SELECT date, prc, ret, vol
            FROM crsp.dsf
            WHERE permno = {permno}
              AND date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY date
        """
        df = pd.read_sql(query_data, conn, parse_dates=['date'])

        # 5. Close the connection
        conn.close()

        if df.empty:
            st.warning(f"{ticker} No data found for the specified date range.")
            return pd.DataFrame()

        # 6. Data cleaning and formatting
        df['prc'] = df['prc'].abs()
        df['ret'] = df['ret'].astype(float).fillna(0)
        df.attrs['company_name'] = company_name

        return df

    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()