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
                random.choice(['SAVINGS', 'CHECKING', 'LOAN', 'CREDIT']),
                round(random.uniform(50000.0, 500000000.0), 2),
                random.choice(['ACTIVE', 'FROZEN', 'CLOSED']),
                datetime.now()
            ))
    return accounts

def generate_transactions(account_ids, device_ids):
    transactions = []
    for src_id in account_ids:
        for _ in range(random.randint(2, 5)):
            dest_id = random.choice(account_ids)
            if dest_id != src_id:
                transaction_type = random.choice(['TRANSFER', 'PAYMENT', 'DEPOSIT'])
                amount = round(random.uniform(50000.0, 20000000.0), 2)
                auth_method = random.choice(['OTP', 'PASSWORD', 'BIOMETRIC'])
                device_id = random.choice(device_ids)
                created_at = random_date()
                
                transactions.append((
                    src_id,
                    dest_id,
                    transaction_type,
                    amount,
                    auth_method,
                    device_id,
                    created_at
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
                random.choice(['UNRESOLVED', 'RESOLVED', 'IGNORED']),
                datetime.now(),
            ))
    return tags

def generate_devices(customer_ids):
    devices = []
    for cid in customer_ids:
        for _ in range(random.randint(1, 3)):  # Each customer can have 1 to 3 devices
            devices.append((
                cid,
                random.choice(['MOBILE', 'TABLET', 'DESKTOP']),
                random.choice([True, False]),  # is_verified
                fake.date_time_between(start_date='-30d', end_date='now'),  # last_activity
                datetime.now()  # created_at
            ))
    return devices

def generate_auth_logs(customer_ids, device_ids, risk_ids):
    logs = []
    for _ in range(random.randint(20, 40)):  # Generate 20–40 auth logs
        customer_id = random.choice(customer_ids)
        device_id = random.choice(device_ids)
        method = random.choice(['PASSWORD', 'OTP', 'BIOMETRIC', '2FA'])
        success = random.choice([True] * 8 + [False] * 2)  # 80% success rate
        risk_id = random.choice(risk_ids) if not success and random.random() < 0.5 else None

        logs.append((
            customer_id,
            device_id,
            method,
            success,
            risk_id,
            datetime.now()
        ))
    return logs


# --- Generate Edge Cases
def generate_edge_case_customers():
    edge_cases = [

        # 1. NULL fields (represented as empty strings where not nullable)
        (
            'edge case',                                 # first_name 
            None,                                 # last_name
            fake.unique.numerify('############'),   # valid CCCD
            None,                                   # date_of_birth (NULL)
            None,                                     # email
            None,                                     # phone_number
            None,                                     # address
            datetime.now()
        ),

        # 2. Invalid CCCD (too short or contains letters)
        (
            fake.first_name(),
            fake.last_name(),
            'ABC123',        # Invalid CCCD
            fake.date_of_birth(minimum_age=18, maximum_age=90),
            fake.email(),
            fake.phone_number(),
            fake.address(),
            datetime.now()
        ),

        # 3. Duplicate CCCD
        (
            fake.first_name(),
            fake.last_name(),
            '123456789012',      # Duplicate cccd
            fake.date_of_birth(minimum_age=18, maximum_age=90),
            fake.email(),
            fake.phone_number(),
            fake.address(),
            datetime.now()
        ),
        (
            fake.first_name(),
            fake.last_name(),
            '123456789012',      # Duplicate cccd
            fake.date_of_birth(minimum_age=18, maximum_age=90),
            fake.email(),
            fake.phone_number(),
            fake.address(),
            datetime.now()
        ),
    ]
    return edge_cases


def generate_edge_case_transactions(account_ids, verified_device_id, unverified_device_id):
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    src_id = random.choice(account_ids)

    # Ensure dest_id is different from src_id
    while True:
        dest_id = random.choice(account_ids)
        if dest_id != src_id:
            break

    edge_cases = [
        # Violation 1: Transactions more than 10M VND must use strong auth (biometric or OTP). 
        (src_id, dest_id, 'TRANSFER', 15000000.0, 'PASSWORD', verified_device_id, today),
        
        # Violation 2: Device must be verified if new or untrusted.
        (src_id, dest_id, 'PAYMENT', 8000000.0, 'PASSWORD', unverified_device_id, today),

        # Violation 3: Total transaction amount per customer more than 20M VND in a day must have at least one strong auth method.
        (src_id, dest_id, 'TRANSFER', 8000000.0, 'PASSWORD', verified_device_id, today),
        (src_id, dest_id, 'TRANSFER', 7000000.0, 'PASSWORD', verified_device_id, today),
        (src_id, dest_id, 'TRANSFER', 6000000.0, 'PASSWORD', verified_device_id, today),
    ]

    return edge_cases





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

    # --- Insert Customers ---
    customers = generate_customers()
    customer_ids = []

    for customer in customers:
        cur.execute("""
            INSERT INTO Customer (first_name, last_name, cccd, date_of_birth, email, phone_number, address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_id
        """, customer)
        customer_ids.append(cur.fetchone()[0])

    
    # --- Insert Devices ---
    # devices = generate_devices(customer_ids)

    # Separate list to track verification status for each device


    # cur.executemany("""
    #     INSERT INTO Device (customer_id, device_type, is_verified, last_activity, created_at)
    #     VALUES (%s, %s, %s, %s, %s)
    #     RETURNING device_id
    # """, devices)
    # device_ids = [row[0] for row in cur.fetchall()]

    devices = generate_devices(customer_ids)
    device_ids = []
    device_verification_flags = [d[2] for d in devices]  # is_verified is the 3rd element
    
    for device in devices:
        cur.execute("""
            INSERT INTO Device (customer_id, device_type, is_verified, last_activity, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING device_id
        """, device)
        device_ids.append(cur.fetchone()[0])


    # Create a map of device_id -> is_verified
    device_map = {device_id: is_verified for device_id, is_verified in zip(device_ids, device_verification_flags)}

    verified_devices = [did for did, verified in device_map.items() if verified]
    unverified_devices = [did for did, verified in device_map.items() if not verified]

    # --- Insert Accounts ---
    accounts = generate_accounts(customer_ids)
    account_ids=[]
    for account in accounts:
        cur.execute("""
            INSERT INTO Account (customer_id, account_number, account_type, balance, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING account_id
        """, account)
        account_ids.append(cur.fetchone()[0])


    # --- Insert Transactions ---
    transactions = generate_transactions(account_ids, device_ids)
    transaction_ids=[]
    for transaction in transactions:    
        cur.execute("""
            INSERT INTO Transaction (src_account_id, dest_account_id, transaction_type, amount, auth_method, device_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING transaction_id
        """, transaction)
        transaction_ids.append(cur.fetchone()[0]) 

    # --- Insert Risk Tags ---
    risk_tags = generate_risk_tags(transaction_ids)
    risk_ids=[]
    for risk in risk_tags:
        cur.execute("""
            INSERT INTO Risk_tag (transaction_id, risk_type, severity, description, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING risk_id
        """, risk)
        risk_ids.append(cur.fetchone()[0])

    # --- Insert Auth Logs ---
    auth_logs = generate_auth_logs(customer_ids, device_ids, risk_ids)
    auth_ids=[]
    for auth in auth_logs:
        cur.execute("""
            INSERT INTO Auth_log (customer_id, device_id, method, success, risk_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING log_id
        """, auth)
        auth_ids.append(cur.fetchone()[0])
    
    # --- Insert Edge Case Customers ---
    edge_case_customers = generate_edge_case_customers()
    cur.executemany("""
        INSERT INTO Customer (
            first_name, last_name, cccd, date_of_birth,
            email, phone_number, address, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, edge_case_customers)


    # Generate edge cases
    edge_transactions = generate_edge_case_transactions(
        account_ids,
        verified_device_id = random.choice(verified_devices),
        unverified_device_id = random.choice(unverified_devices)
    )

    # Insert into the Transaction table
    cur.executemany("""
        INSERT INTO Transaction (
            src_account_id, dest_account_id, transaction_type, amount,
            auth_method, device_id, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, edge_transactions)

    
    conn.commit()
    cur.close()
    conn.close()
    print("Sample data successfully inserted.")

# --- Run Script ---
if __name__ == "__main__":
    insert_data()
