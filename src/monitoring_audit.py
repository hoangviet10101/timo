# File: src/monitoring_audit.py

import psycopg2
import data_quality_standards as dq
import os
from dotenv import load_dotenv


load_dotenv()

# --- DB Config ---
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST_DOCKER")
DB_PORT = os.getenv("PORT")


def log_result(name, passed, detail):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{status}] {name}\n{detail}\n")

def main():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    checks = [
        ("Null check: customer.cccd", dq.check_nulls, (cur, "customer", "cccd")),
        ("Null check: account.account_number", dq.check_nulls, (cur, "account", "account_number")),
        ("Null check: transaction.amount", dq.check_nulls, (cur, "transaction", "amount")),
        ("Uniqueness check: customer.cccd", dq.check_uniqueness, (cur, "customer", "cccd")),
        ("Format check: customer.cccd (12 digits)", dq.check_cccd_format, (cur,)),
        ("Foreign Key: transaction.account_id → account", dq.check_foreign_keys_transaction_account, (cur,)),
        ("High-value transaction requires strong auth", dq.high_value_auth_check, (cur,)),
        ("Daily total > 20M requires strong auth", dq.daily_total_auth_check, (cur,))
    ]

    for label, func, args in checks:
        passed, detail = func(*args)
        log_result(label, passed, detail)

    conn.close()

if __name__ == "__main__":
    main()
