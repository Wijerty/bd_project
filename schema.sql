-- Anti-fraud Database Schema for P2P Transfers

-- Create Client table
CREATE TABLE Client (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    kyc_status VARCHAR(50),
    risk_level DECIMAL(3,2) DEFAULT 0.0,
    is_blocked BOOLEAN DEFAULT FALSE
);

-- Create Account/Card table
CREATE TABLE Account (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    account_type VARCHAR(20) CHECK (account_type IN ('card', 'bank_account', 'digital_wallet')),
    currency CHAR(3) DEFAULT 'RUB',
    balance DECIMAL(15,2) DEFAULT 0.0,
    opening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    daily_limit DECIMAL(15,2) DEFAULT 100000.0,
    monthly_limit DECIMAL(15,2) DEFAULT 1000000.0,
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
);

-- Create Device table
CREATE TABLE Device (
    device_id SERIAL PRIMARY KEY,
    device_fingerprint VARCHAR(255) UNIQUE,
    device_type VARCHAR(20) CHECK (device_type IN ('mobile', 'desktop', 'tablet')),
    os VARCHAR(50),
    browser VARCHAR(50),
    user_agent TEXT,
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP,
    risk_score DECIMAL(3,2) DEFAULT 0.0
);

-- Create IP Address table
CREATE TABLE IPAddress (
    ip_address_id SERIAL PRIMARY KEY,
    ip_address INET UNIQUE NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    isp VARCHAR(100),
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    is_proxy BOOLEAN DEFAULT FALSE,
    is_tor BOOLEAN DEFAULT FALSE
);

-- Create Transaction table
CREATE TABLE Transaction (
    transaction_id SERIAL PRIMARY KEY,
    sender_account_id INTEGER NOT NULL,
    receiver_account_id INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency CHAR(3) DEFAULT 'RUB',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('P2P', 'merchant', 'ATM', 'other')),
    status VARCHAR(20) CHECK (status IN ('completed', 'pending', 'failed', 'reversed')),
    ip_address_id INTEGER,
    device_id INTEGER,
    location_coordinates POINT,
    description TEXT,
    fraud_score DECIMAL(5,2) DEFAULT 0.0,
    is_flagged BOOLEAN DEFAULT FALSE,
    flagged_reason TEXT,
    FOREIGN KEY (sender_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (receiver_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (ip_address_id) REFERENCES IPAddress(ip_address_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id)
);

-- Create Rules/Alerts table
CREATE TABLE Rule (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    rule_condition TEXT,
    weight DECIMAL(5,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Blacklists table
CREATE TABLE Blacklist (
    blacklist_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) CHECK (entity_type IN ('client', 'account', 'ip', 'device')),
    entity_id INTEGER NOT NULL,
    reason TEXT,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    added_by VARCHAR(100)
);

-- Create Client Relationships table
CREATE TABLE ClientRelationship (
    relationship_id SERIAL PRIMARY KEY,
    client_id_1 INTEGER NOT NULL,
    client_id_2 INTEGER NOT NULL,
    relationship_type VARCHAR(20) CHECK (relationship_type IN ('family', 'friend', 'colleague')),
    since_date DATE,
    transaction_count INTEGER DEFAULT 0,
    total_amount_transferred DECIMAL(15,2) DEFAULT 0.0,
    FOREIGN KEY (client_id_1) REFERENCES Client(client_id),
    FOREIGN KEY (client_id_2) REFERENCES Client(client_id),
    UNIQUE (client_id_1, client_id_2)
);

-- Create indexes for better query performance
CREATE INDEX idx_transaction_date ON Transaction(transaction_date);
CREATE INDEX idx_transaction_sender ON Transaction(sender_account_id);
CREATE INDEX idx_transaction_receiver ON Transaction(receiver_account_id);
CREATE INDEX idx_account_client ON Account(client_id);
CREATE INDEX idx_account_number ON Account(account_number);
CREATE INDEX idx_client_phone ON Client(phone_number);
CREATE INDEX idx_client_email ON Client(email);
CREATE INDEX idx_device_fingerprint ON Device(device_fingerprint);
CREATE INDEX idx_ip_address ON IPAddress(ip_address);
CREATE INDEX idx_client_relationship_1 ON ClientRelationship(client_id_1);
CREATE INDEX idx_client_relationship_2 ON ClientRelationship(client_id_2);

-- Sample data for testing
INSERT INTO Client (first_name, last_name, date_of_birth, phone_number, email, kyc_status, risk_level) VALUES
('Ivan', 'Petrov', '1990-05-15', '+79991234567', 'ivan.petrov@email.com', 'verified', 0.1),
('Maria', 'Sidorova', '1985-12-03', '+79997654321', 'maria.sidorova@email.com', 'verified', 0.05),
('Alexey', 'Ivanov', '1992-08-21', '+79991112233', 'alexey.ivanov@email.com', 'pending', 0.3);

INSERT INTO Account (client_id, account_number, account_type, balance) VALUES
(1, '4276123456789012', 'card', 50000.00),
(2, '4276987654321098', 'card', 30000.00),
(3, '4276112233445566', 'card', 15000.00);

INSERT INTO Device (device_fingerprint, device_type, os, browser, user_agent) VALUES
('fingerprint_001', 'mobile', 'Android', 'Chrome', 'Mozilla/5.0 (Linux; Android 10) Chrome/91.0.4472.120 Mobile Safari/537.36'),
('fingerprint_002', 'desktop', 'Windows', 'Firefox', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0');

INSERT INTO IPAddress (ip_address, country, city, latitude, longitude, isp) VALUES
('192.168.1.100', 'Russia', 'Moscow', 55.7558, 37.6173, 'MTS'),
('192.168.1.101', 'Russia', 'Saint Petersburg', 59.9343, 30.3351, 'Beeline');

INSERT INTO Transaction (sender_account_id, receiver_account_id, amount, transaction_type, status, ip_address_id, device_id) VALUES
(1, 2, 5000.00, 'P2P', 'completed', 1, 1),
(2, 3, 3000.00, 'P2P', 'completed', 2, 2),
(3, 1, 1000.00, 'P2P', 'completed', 1, 1);

INSERT INTO Rule (rule_name, rule_description, rule_condition, weight, is_active) VALUES
('HighAmount', 'Transaction amount exceeds threshold', 'amount > 10000', 5.0, TRUE),
('NewDevice', 'Transaction from a newly registered device', 'device_first_seen < 24 hours', 3.0, TRUE),
('HighRiskIP', 'Transaction from a high-risk IP address', 'ip_risk_score > 0.8', 4.0, TRUE),
('FrequentTransactions', 'Multiple transactions in short time period', 'transaction_count > 10 in 1 hour', 2.0, TRUE);

INSERT INTO ClientRelationship (client_id_1, client_id_2, relationship_type, since_date, transaction_count, total_amount_transferred) VALUES
(1, 2, 'friend', '2022-01-15', 5, 25000.00);