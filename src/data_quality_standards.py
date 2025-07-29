

import re
from datetime import date

def check_nulls(cur, table, column):
    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
    result = cur.fetchone()
    count = result[0]
    # return count == 0, f"{count} NULLs in {table}.{column}"

    if count == 0:
        return True, f"0 NULLs in {table}.{column}"
    else:
        return False, f"{count} NULLs in {table}.{column}"

def check_uniqueness(cur, table, column):
    cur.execute(f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} HAVING COUNT(*) > 1")
    dups = cur.fetchall()

    if len(dups)==0:
        return True, f"{len(dups)} duplicates in {table}.{column}: {dups}"
    else:
        return False, f"{len(dups)} duplicates in {table}.{column}: {dups}"

    # return len(dups) == 0, f"{len(dups)} duplicates in {table}.{column}: {dups}"

def check_cccd_format(cur):
    cur.execute("SELECT customer_id, cccd FROM customer")
    rows = cur.fetchall()

    invalid = []
    for cid, cccd in rows:
        if not re.fullmatch(r"\d{12}", cccd):
            invalid.append((cid, cccd))

    if len(invalid) == 0:
        return True, "All CCCDs are valid"
    else:
        return False, f"Invalid CCCDs: {invalid}"


def check_foreign_keys_transaction_account(cur):
    cur.execute("""
        SELECT t.transaction_id FROM transaction t
        LEFT JOIN account a ON t.source_account_id = a.account_id
        WHERE a.account_id IS NULL
    """)
    orphans = cur.fetchall()
    return len(orphans) == 0, f"Orphaned transactions: {orphans}"

def high_value_auth_check(cur):
    cur.execute("""
        SELECT t.transaction_id, t.amount, a.customer_id FROM transaction t
        JOIN account a ON t.source_account_id = a.account_id
        WHERE t.amount > 10000000
    """)
    rows = cur.fetchall()
    failed = []
    for tx_id, amt, cid in rows:
        cur.execute("""
            SELECT COUNT(*) FROM authlog
            WHERE customer_id = %s AND method IN ('OTP', 'BIOMETRIC')
            AND timestamp::date = CURRENT_DATE
        """, (cid,))
        if cur.fetchone()[0] == 0:
            failed.append((tx_id, cid))
    return len(failed) == 0, f"Missing strong auth: {failed}"

def daily_total_auth_check(cur):
    cur.execute("""
        SELECT a.customer_id, DATE(t.date), SUM(t.amount)
        FROM transaction t
        JOIN account a ON t.source_account_id = a.account_id
        GROUP BY a.customer_id, DATE(t.date)
        HAVING SUM(t.amount) > 20000000
    """)
    rows = cur.fetchall()
    failed = []
    for cid, tx_date, _ in rows:
        cur.execute("""
            SELECT COUNT(*) FROM authlog
            WHERE customer_id = %s AND method IN ('OTP', 'BIOMETRIC')
            AND timestamp::date = %s
        """, (cid, tx_date))
        if cur.fetchone()[0] == 0:
            failed.append((cid, tx_date))
    return len(failed) == 0, f"Missing auth on high daily total: {failed}"
