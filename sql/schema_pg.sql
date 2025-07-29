DROP TABLE IF EXISTS Auth_log CASCADE;
DROP TABLE IF EXISTS Device CASCADE;
DROP TABLE IF EXISTS Risk_tag CASCADE;
DROP TABLE IF EXISTS Transaction CASCADE;
DROP TABLE IF EXISTS Account CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;


CREATE TABLE Customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    cccd VARCHAR(50) UNIQUE,
    date_of_birth VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(50),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Account (
    account_id SERIAL PRIMARY KEY,
    customer_id INT,
    account_number VARCHAR(20) UNIQUE,
    account_type VARCHAR(20) CHECK (account_type IN ('SAVINGS', 'CHECKING', 'BUSINESS')),
    balance DECIMAL(18, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('ACTIVE', 'FROZEN', 'CLOSED')) DEFAULT 'ACTIVE',
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Transaction (
    transaction_id SERIAL PRIMARY KEY,
    source_account_id INT,
    destination_account_id INT,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('TRANSFER', 'DEPOSIT', 'WITHDRAWAL', 'PAYMENT')),
    amount DECIMAL(18, 2),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (destination_account_id) REFERENCES Account(account_id)
);


CREATE TABLE Risk_tag (
    risk_id SERIAL PRIMARY KEY,
    transaction_id INT,
    risk_type VARCHAR(50),
    severity VARCHAR(20) CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('UNRESOLVED', 'RESOLVED', 'IGNORED')) DEFAULT 'UNRESOLVED',
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
);


CREATE TABLE Device (
    device_id SERIAL PRIMARY KEY,
    customer_id INT,
    type VARCHAR(50) CHECK (type IN ('MOBILE', 'TABLET', 'DESKTOP', 'UNKNOWN')),
    last_activity TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Auth_log (
    log_id SERIAL PRIMARY KEY,
    customer_id INT,
    device_id INT,
    method VARCHAR(20) CHECK (method IN ('OTP', 'BIOMETRIC', 'PASSWORD')),
    success BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id),
    FOREIGN KEY (risk_id) REFERENCES Risk_tag(risk_id)
);
