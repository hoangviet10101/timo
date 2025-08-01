--This schema is written for Postgres


-- Can use these commands to restart the the tables
-- DROP TABLE IF EXISTS Auth_log CASCADE;
-- DROP TABLE IF EXISTS Device CASCADE;
-- DROP TABLE IF EXISTS Risk_tag CASCADE;
-- DROP TABLE IF EXISTS Transaction CASCADE;
-- DROP TABLE IF EXISTS Account CASCADE;
-- DROP TABLE IF EXISTS Customer CASCADE;


CREATE TABLE Customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    cccd VARCHAR(50) ,
    date_of_birth DATE,
    email VARCHAR(50) ,
    phone_number VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Account (
    account_id SERIAL PRIMARY KEY,
    customer_id INT,
    account_number VARCHAR(50) UNIQUE,
    account_type VARCHAR(50),
    balance DECIMAL(18, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Device (
    device_id SERIAL PRIMARY KEY,
    customer_id INT,
    device_type VARCHAR(50),
    is_verified BOOLEAN,
    last_activity TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Transaction (
    transaction_id SERIAL PRIMARY KEY,
    src_account_id INT,
    dest_account_id INT,
    transaction_type VARCHAR(50),
    amount FLOAT,
    auth_method VARCHAR(50), 
    device_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (src_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (dest_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id)
);


CREATE TABLE Risk_tag (
    risk_id SERIAL PRIMARY KEY,
    transaction_id INT,
    risk_type VARCHAR(50),
    severity VARCHAR(50),
    description TEXT,
    status VARCHAR(50) DEFAULT 'UNRESOLVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
);


CREATE TABLE Auth_log (
    log_id SERIAL PRIMARY KEY,
    customer_id INT,
    device_id INT,
    method VARCHAR(50),
    success BOOLEAN,
    risk_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id),
    FOREIGN KEY (risk_id) REFERENCES Risk_tag(risk_id)
);
