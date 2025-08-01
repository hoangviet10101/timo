import re
from datetime import date

def check_nulls(cur, table, column):
    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
    count = cur.fetchone()[0]
    return count == 0, f"{count} NULLs in {table}.{column}"

def check_uniqueness(cur, table, column):
    cur.execute(f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} HAVING COUNT(*) > 1")
    dups = cur.fetchall()
    return len(dups) == 0, f"{len(dups)} duplicates in {table}.{column}: {dups}"

def check_cccd_format(cur):
    cur.execute("SELECT customer_id, cccd FROM Customer")
    rows = cur.fetchall()
    invalid = [(cid, cccd) for cid, cccd in rows if cccd and not re.fullmatch(r"\d{12}", cccd)]
    return len(invalid) == 0, f"Invalid CCCDs: {invalid}"

def check_foreign_keys_transaction_account(cur):
    cur.execute("""
        SELECT transaction_id FROM Transaction t
        LEFT JOIN Account a ON t.src_account_id = a.account_id
        WHERE a.account_id IS NULL
    """)
    orphans = cur.fetchall()
    return len(orphans) == 0, f"Orphaned transactions with invalid source account: {orphans}"

def high_value_auth_check(cur):
    cur.execute("""
        SELECT t.transaction_id, t.amount, a.customer_id
        FROM Transaction t
        JOIN Account a ON t.src_account_id = a.account_id
        WHERE t.amount > 10000000
    """)
    rows = cur.fetchall()
    failed = []
    for tx_id, amt, cid in rows:
        cur.execute("""
            SELECT COUNT(*) FROM Auth_log
            WHERE customer_id = %s AND method IN ('OTP', 'BIOMETRIC')
            AND created_at::date = CURRENT_DATE
        """, (cid,))
        if cur.fetchone()[0] == 0:
            failed.append((tx_id, cid))
    return len(failed) == 0, f"Missing strong auth on high-value transactions: {failed}"

def daily_total_auth_check(cur):
    cur.execute("""
        SELECT a.customer_id, DATE(t.created_at), SUM(t.amount)
        FROM Transaction t
        JOIN Account a ON t.src_account_id = a.account_id
        GROUP BY a.customer_id, DATE(t.created_at)
        HAVING SUM(t.amount) > 20000000
    """)
    rows = cur.fetchall()
    failed = []
    for cid, tx_date, _ in rows:
        cur.execute("""
            SELECT COUNT(*) FROM Auth_log
            WHERE customer_id = %s AND method IN ('OTP', 'BIOMETRIC')
            AND created_at::date = %s
        """, (cid, tx_date))
        if cur.fetchone()[0] == 0:
            failed.append((cid, tx_date))
    return len(failed) == 0, f"Missing auth on high daily total: {failed}"

def check_unverified_device_transactions(cur):
    cur.execute("""
        SELECT t.transaction_id, t.device_id FROM Transaction t
        JOIN Device d ON t.device_id = d.device_id
        WHERE d.is_verified = FALSE
    """)
    unverified = cur.fetchall()
    return len(unverified) == 0, f"Transactions using unverified devices: {unverified}"


