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
    SELECT transaction_id, amount, transaction_type, source_account_id
    FROM transaction
    WHERE amount > 8000
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

# # Unverified devices
# st.header("🖥️ Unverified Devices")
# device_query = """
#     SELECT d.device_id, d.customer_id, d.ip_address, a.customer_id
#     FROM device d
#     LEFT JOIN auth_log a ON d.device_id = a.device_id
#     WHERE a.method NOT IN ('BIOMETRIC', 'OTP') OR a.method IS NULL
# """
# df_device = pd.read_sql(device_query, conn)
# st.dataframe(df_device)

conn.close()


# import streamlit as st
# import psycopg2
# import pandas as pd
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Database connection settings
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "5432")
# DB_NAME = os.getenv("DB_NAME", "airflow")
# DB_USER = os.getenv("DB_USER", "airflow")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "airflow")

# # Test connection and query
# st.title("PostgreSQL Connection Test")

# try:
#     conn = psycopg2.connect(
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         host=DB_HOST,
#         port=DB_PORT
#     )

#     st.success("✅ Connected to PostgreSQL!")

#     # Run a test query — make sure this table exists
#     test_query = "SELECT * FROM customer LIMIT 5;"
#     df = pd.read_sql(test_query, conn)
#     st.dataframe(df)

# except Exception as e:
#     st.error("❌ Failed to connect to PostgreSQL")
#     st.code(str(e))

# finally:
#     if 'conn' in locals():
#         conn.close()
