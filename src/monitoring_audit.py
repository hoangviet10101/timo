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
    divider = "-" * 50

    print(f"{divider}")
    print(f"{status} | Check: {name}")
    
    # Limit long detail output (e.g., long lists of IDs)
    if isinstance(detail, str) and len(detail) > 500:
        detail = detail[:500] + "...\n[Output truncated]"
    print(f"Details: {detail}")
    print(f"{divider}\n")


def main():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    checks = [
        ("Null check: Customer.email", dq.check_nulls, (cur, "Customer", "email")),
        ("Null check: Account.account_number", dq.check_nulls, (cur, "Account", "account_number")),
        ("Null check: Transaction.amount", dq.check_nulls, (cur, "Transaction", "amount")),
        ("Uniqueness check: Account.account_number", dq.check_uniqueness, (cur, "Account", "account_number")),
        ("Uniqueness check: Customer.cccd", dq.check_uniqueness, (cur, "Customer", "cccd")),
        ("Format check: Customer.cccd (12 digits)", dq.check_cccd_format, (cur,)),
        ("Foreign Key Check: Transaction.src_account_id → Account.account_id", dq.check_foreign_keys_transaction_account, (cur,)),
        ("High-value transaction requires strong auth", dq.high_value_auth_check, (cur,)),
        ("Daily total > 20M requires strong auth", dq.daily_total_auth_check, (cur,)),
        ("Transactions using unverified devices", dq.check_unverified_device_transactions, (cur,)),
    ]

    for label, func, args in checks:
        passed, detail = func(*args)
        log_result(label, passed, detail)

    conn.close()


if __name__ == "__main__":
    main()
