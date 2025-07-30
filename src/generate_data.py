import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
import os
from dotenv import load_dotenv


fake = Faker()


load_dotenv()

# --- DB Config ---
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST_DOCKER")
DB_PORT = os.getenv("PORT")

# --- Utilities ---
def random_date(days_back=365):
    return datetime.now() - timedelta(days=random.randint(1, days_back))

# --- Data Generators ---
# def generate_customers(n=10):
#     return [
#         (
#             fake.first_name(),
#             fake.last_name(),
#             fake.unique.bothify(text='############'),
#             fake.date_of_birth(minimum_age=18, maximum_age=75),
#             fake.email(),
#             fake.phone_number(),
#             fake.address(),
#             datetime.now()
#         ) for _ in range(n)
#     ]

def generate_customers(n=10):
    customers = []

    for _ in range(n):
        customer = (
            fake.first_name(),
            fake.last_name(),
            fake.unique.numerify('############'),  # CCCD: 12 digits
            fake.date_of_birth(minimum_age=18, maximum_age=75),
            fake.email(),
            fake.phone_number(),
            fake.address(),
            datetime.now()
        )
        customers.append(customer)

    return customers


def generate_accounts(customer_ids):
    accounts = []
    for cid in customer_ids:
        for _ in range(random.randint(1, 2)):
            accounts.append((
                cid,
                fake.unique.bothify(text='ACCT#######'),
                random.choice(['SAVINGS', 'CHECKING', 'BUSINESS']),
                round(random.uniform(100.0, 50000.0), 2),
                datetime.now(),
                random.choice(['ACTIVE', 'FROZEN', 'CLOSED'])
            ))
    return accounts

def generate_transactions(account_ids):
    transactions = []
    for src_id in account_ids:
        for _ in range(random.randint(2, 5)):
            dest_id = random.choice(account_ids)
            if dest_id != src_id:
                transactions.append((
                    src_id,
                    dest_id,
                    random.choice(['TRANSFER', 'PAYMENT', 'DEPOSIT']),
                    round(random.uniform(50.0, 10000.0), 2),
                    random_date()
                ))
    return transactions

def generate_risk_tags(transaction_ids):
    tags = []
    for tid in transaction_ids:
        if random.random() < 0.3:
            tags.append((
                tid,
                random.choice(['FRAUD', 'HIGH_VALUE', 'UNUSUAL_ACTIVITY']),
                random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                fake.sentence(),
                datetime.now(),
                random.choice(['UNRESOLVED', 'RESOLVED', 'IGNORED'])
            ))
    return tags

def generate_devices(customer_ids):
    return [
        (
            cid,
            random.choice(['MOBILE', 'DESKTOP', 'TABLET']),
            random_date(),
            fake.ipv4()
        ) for cid in customer_ids
    ]

def generate_auth_logs(customer_ids, device_ids, risk_ids):
    logs = []
    for cid in customer_ids:
        for _ in range(random.randint(1, 3)):
            device_id = random.choice(device_ids)
            risk_id = random.choice(risk_ids) if risk_ids and random.random() < 0.2 else None
            logs.append((
                cid,
                device_id,
                random.choice(['OTP', 'BIOMETRIC']),
                random.choice([True, False]),
                random_date(),
                risk_id
            ))
    return logs

# --- Main Insert Logic ---
def insert_data():
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD,
        host=DB_HOST, 
        port=DB_PORT
    )
    cur = conn.cursor()

    # Customers
    customer_data = generate_customers(20)
    customer_ids = []
    for row in customer_data:
        cur.execute("""
            INSERT INTO customer (first_name, last_name, cccd, date_of_birth, email, phone_number, address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_id
        """, row)
        customer_ids.append(cur.fetchone()[0])

    # Accounts
    account_data = generate_accounts(customer_ids)
    account_ids = []
    for row in account_data:
        cur.execute("""
            INSERT INTO account (customer_id, account_number, account_type, balance, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING account_id
        """, row)
        account_ids.append(cur.fetchone()[0])

    # Transactions
    transaction_data = generate_transactions(account_ids)
    transaction_ids = []
    for row in transaction_data:
        cur.execute("""
            INSERT INTO transaction (source_account_id, destination_account_id, transaction_type, amount, date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING transaction_id
        """, row)
        transaction_ids.append(cur.fetchone()[0])

    # Risk Tags
    risk_data = generate_risk_tags(transaction_ids)
    risk_ids = []
    for row in risk_data:
        cur.execute("""
            INSERT INTO risk_tag (transaction_id, risk_type, severity, description, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING risk_id
        """, row)
        risk_ids.append(cur.fetchone()[0])

    # Devices
    device_data = generate_devices(customer_ids)
    device_ids = []
    for row in device_data:
        cur.execute("""
            INSERT INTO device (customer_id, type, last_activity, ip_address)
            VALUES (%s, %s, %s, %s)
            RETURNING device_id
        """, row)
        device_ids.append(cur.fetchone()[0])

    # Auth Logs
    auth_data = generate_auth_logs(customer_ids, device_ids, risk_ids)
    for row in auth_data:
        cur.execute("""
            INSERT INTO auth_log (customer_id, device_id, method, success, timestamp, risk_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, row)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Sample data inserted into 'timo' database.")

# --- Run Script ---
if __name__ == "__main__":
    insert_data()
