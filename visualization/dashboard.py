import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST_LOCAL"),
    port=os.getenv("DB_PORT")
)

st.title("📊 Banking Data Quality Dashboard")

# Risky transactions
st.header("⚠️ Risky Transactions")
risky_query = """
    SELECT 
        t.transaction_id,
        a.customer_id,
        t.amount,
        t.auth_method,
        t.created_at
    FROM transaction t
    JOIN account a ON t.src_account_id = a.account_id
    WHERE t.amount > 10000000
    AND t.auth_method NOT IN ('OTP', 'BIOMETRIC')
    ORDER BY t.amount DESC;
"""
df_risky = pd.read_sql(risky_query, conn)
st.dataframe(df_risky)

# Failed CCCD format
st.header("❌ Invalid CCCD Format")
cccd_query = """
    SELECT customer_id, cccd
    FROM customer
    WHERE cccd !~ '^\d{12}$'
"""
df_cccd = pd.read_sql(cccd_query, conn)
st.dataframe(df_cccd)

# Unverified devices
st.header("🖥️ Unverified Devices")
device_query = """
    SELECT d.device_id, c.customer_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, d.device_type, d.last_activity, d.created_at
    FROM Device d
    JOIN Customer c ON d.customer_id = c.customer_id
    WHERE d.is_verified = FALSE
    ORDER BY d.last_activity DESC;
"""
df_device = pd.read_sql(device_query, conn)
st.dataframe(df_device)

conn.close()


