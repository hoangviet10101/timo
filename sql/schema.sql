--This schema is written in MySQL

CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    cccd VARCHAR(20) UNIQUE,
    date_of_birth DATE,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Account (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_number VARCHAR(20) UNIQUE,
    account_type ENUM('SAVINGS', 'CHECKING', 'BUSINESS'),
    balance DECIMAL(18, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ACTIVE', 'FROZEN', 'CLOSED') DEFAULT 'ACTIVE',
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE Transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    source_account_id INT,
    destination_account_id INT,
    transaction_type ENUM('TRANSFER', 'WITHDRAWAL', 'DEPOSIT'),
    amount DECIMAL(18, 2),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (destination_account_id) REFERENCES Account(account_id)
);


CREATE TABLE RiskTag (
    risk_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    risk_type VARCHAR(50),
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('UNRESOLVED', 'RESOLVED', 'IGNORED') DEFAULT 'UNRESOLVED',
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
);


CREATE TABLE Device (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    type ENUM('MOBILE', 'DESKTOP', 'TABLET'),
    last_activity DATETIME,
    ip_address VARCHAR(45),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


CREATE TABLE AuthLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    device_id INT,
    method ENUM('PASSWORD', 'OTP', 'BIOMETRIC'),
    success BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id),
    FOREIGN KEY (risk_id) REFERENCES RiskTag(risk_id)
);
