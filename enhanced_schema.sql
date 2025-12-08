-- Enhanced Anti-fraud Database Schema for P2P Transfers
-- Includes advanced fraud detection capabilities

-- Create Client table with enhanced fields
CREATE TABLE Client (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    kyc_status VARCHAR(50) CHECK (kyc_status IN ('none', 'pending', 'verified', 'rejected')),
    risk_level DECIMAL(5,2) DEFAULT 0.0,
    is_blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    last_login_date TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'closed')),
    risk_category VARCHAR(20) DEFAULT 'low' CHECK (risk_category IN ('low', 'medium', 'high', 'critical')),
    total_transactions INTEGER DEFAULT 0,
    total_amount_transferred DECIMAL(15,2) DEFAULT 0.0,
    avg_transaction_amount DECIMAL(15,2) DEFAULT 0.0,
    max_transaction_amount DECIMAL(15,2) DEFAULT 0.0,
    preferred_device_ids INTEGER[],
    preferred_ip_addresses INTEGER[],
    behavior_score DECIMAL(5,2) DEFAULT 0.0
);

-- Create Account/Card table with enhanced fields
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
    card_expiry_date DATE,
    card_type VARCHAR(20),
    bank_name VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    last_transaction_date TIMESTAMP,
    transaction_count_today INTEGER DEFAULT 0,
    transaction_count_month INTEGER DEFAULT 0,
    amount_transferred_today DECIMAL(15,2) DEFAULT 0.0,
    amount_transferred_month DECIMAL(15,2) DEFAULT 0.0,
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
);

-- Create Device table with enhanced tracking
CREATE TABLE Device (
    device_id SERIAL PRIMARY KEY,
    device_fingerprint VARCHAR(255) UNIQUE,
    device_type VARCHAR(20) CHECK (device_type IN ('mobile', 'desktop', 'tablet', 'unknown')),
    os VARCHAR(50),
    os_version VARCHAR(20),
    browser VARCHAR(50),
    browser_version VARCHAR(20),
    user_agent TEXT,
    screen_resolution VARCHAR(20),
    timezone VARCHAR(50),
    language VARCHAR(10),
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    is_emulator BOOLEAN DEFAULT FALSE,
    is_rooted BOOLEAN DEFAULT FALSE,
    vpn_detected BOOLEAN DEFAULT FALSE,
    transaction_count INTEGER DEFAULT 0,
    unique_clients_used INTEGER DEFAULT 0,
    device_age_hours INTEGER DEFAULT 0,
    reputation_score DECIMAL(5,2) DEFAULT 0.0
);

-- Create IP Address table with enhanced geolocation and risk data
CREATE TABLE IPAddress (
    ip_address_id SERIAL PRIMARY KEY,
    ip_address INET UNIQUE NOT NULL,
    country VARCHAR(100),
    country_code VARCHAR(2),
    city VARCHAR(100),
    region VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    isp VARCHAR(100),
    organization VARCHAR(100),
    asn VARCHAR(20),
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    is_proxy BOOLEAN DEFAULT FALSE,
    is_tor BOOLEAN DEFAULT FALSE,
    is_vpn BOOLEAN DEFAULT FALSE,
    is_datacenter BOOLEAN DEFAULT FALSE,
    is_mobile BOOLEAN DEFAULT FALSE,
    threat_level VARCHAR(20) DEFAULT 'low' CHECK (threat_level IN ('low', 'medium', 'high', 'critical')),
    transaction_count INTEGER DEFAULT 0,
    unique_clients_used INTEGER DEFAULT 0,
    reputation_score DECIMAL(5,2) DEFAULT 0.0
);

-- Create enhanced Transaction table
CREATE TABLE Transaction (
    transaction_id SERIAL PRIMARY KEY,
    sender_account_id INTEGER NOT NULL,
    receiver_account_id INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency CHAR(3) DEFAULT 'RUB',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('P2P', 'merchant', 'ATM', 'other')),
    status VARCHAR(20) CHECK (status IN ('completed', 'pending', 'failed', 'reversed', 'flagged', 'blocked')),
    ip_address_id INTEGER,
    device_id INTEGER,
    location_coordinates POINT,
    location_city VARCHAR(100),
    location_country VARCHAR(100),
    description TEXT,
    fraud_score DECIMAL(5,2) DEFAULT 0.0,
    is_flagged BOOLEAN DEFAULT FALSE,
    flagged_reason TEXT,
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_factors TEXT[],
    processing_time_ms INTEGER,
    merchant_category_code VARCHAR(10),
    reference_number VARCHAR(100),
    chargeback_risk DECIMAL(5,2) DEFAULT 0.0,
    velocity_score DECIMAL(5,2) DEFAULT 0.0,
    anomaly_score DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (sender_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (receiver_account_id) REFERENCES Account(account_id),
    FOREIGN KEY (ip_address_id) REFERENCES IPAddress(ip_address_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id)
);

-- Create enhanced Rules table
CREATE TABLE Rule (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    rule_category VARCHAR(50) CHECK (rule_category IN ('amount', 'velocity', 'behavior', 'network', 'device', 'location')),
    rule_condition TEXT,
    weight DECIMAL(5,2) DEFAULT 1.0,
    threshold DECIMAL(15,2),
    time_window VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    auto_block BOOLEAN DEFAULT FALSE,
    notification_required BOOLEAN DEFAULT TRUE
);

-- Create enhanced Blacklists table
CREATE TABLE Blacklist (
    blacklist_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) CHECK (entity_type IN ('client', 'account', 'ip', 'device', 'email', 'phone')),
    entity_value VARCHAR(255) NOT NULL,
    entity_id INTEGER,
    reason TEXT,
    risk_level VARCHAR(20) DEFAULT 'high' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    source VARCHAR(50),
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    added_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    auto_block BOOLEAN DEFAULT TRUE
);

-- Create Client Relationships table for network analysis
CREATE TABLE ClientRelationship (
    relationship_id SERIAL PRIMARY KEY,
    client_id_1 INTEGER NOT NULL,
    client_id_2 INTEGER NOT NULL,
    relationship_type VARCHAR(20) CHECK (relationship_type IN ('family', 'friend', 'colleague', 'business', 'unknown')),
    relationship_strength DECIMAL(3,2) DEFAULT 0.5,
    since_date DATE,
    transaction_count INTEGER DEFAULT 0,
    total_amount_transferred DECIMAL(15,2) DEFAULT 0.0,
    avg_transaction_amount DECIMAL(15,2) DEFAULT 0.0,
    last_transaction_date TIMESTAMP,
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (client_id_1) REFERENCES Client(client_id),
    FOREIGN KEY (client_id_2) REFERENCES Client(client_id),
    UNIQUE (client_id_1, client_id_2)
);

-- Create Transaction Pattern table for carousel detection
CREATE TABLE TransactionPattern (
    pattern_id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) CHECK (pattern_type IN ('carousel', 'layered', 'circular', 'burst', 'velocity')),
    client_id INTEGER,
    account_ids INTEGER[],
    transaction_ids INTEGER[],
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    transaction_count INTEGER,
    total_amount DECIMAL(15,2),
    risk_score DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
);

-- Create Alert table for fraud notifications
CREATE TABLE Alert (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) CHECK (alert_type IN ('fraud', 'suspicious', 'high_risk', 'blocked', 'velocity')),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    client_id INTEGER,
    account_id INTEGER,
    transaction_id INTEGER,
    rule_id INTEGER,
    title VARCHAR(200),
    description TEXT,
    alert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
    assigned_to VARCHAR(100),
    resolved_date TIMESTAMP,
    resolution_notes TEXT,
    risk_score DECIMAL(5,2),
    auto_generated BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (account_id) REFERENCES Account(account_id),
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id),
    FOREIGN KEY (rule_id) REFERENCES Rule(rule_id)
);

-- Create Session table for behavior tracking
CREATE TABLE Session (
    session_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    device_id INTEGER,
    ip_address_id INTEGER,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    duration_minutes INTEGER,
    login_method VARCHAR(20),
    login_success BOOLEAN DEFAULT TRUE,
    failed_attempts INTEGER DEFAULT 0,
    transactions_count INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.0,
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (device_id) REFERENCES Device(device_id),
    FOREIGN KEY (ip_address_id) REFERENCES IPAddress(ip_address_id)
);

-- Create Velocity Counter table for real-time monitoring
CREATE TABLE VelocityCounter (
    counter_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    account_id INTEGER,
    metric_type VARCHAR(50) CHECK (metric_type IN ('transaction_count', 'amount', 'failed_attempts')),
    time_window VARCHAR(20) CHECK (time_window IN ('1min', '5min', '15min', '1hour', '1day', '1week')),
    counter_value INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    threshold INTEGER,
    is_alerted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (account_id) REFERENCES Account(account_id)
);

-- Create Risk Score History table
CREATE TABLE RiskScoreHistory (
    history_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    account_id INTEGER,
    transaction_id INTEGER,
    old_risk_score DECIMAL(5,2),
    new_risk_score DECIMAL(5,2),
    score_change DECIMAL(5,2),
    reason TEXT,
    rule_ids INTEGER[],
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (account_id) REFERENCES Account(account_id),
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
);

-- Enhanced indexes for better query performance
CREATE INDEX idx_transaction_date ON Transaction(transaction_date);
CREATE INDEX idx_transaction_sender ON Transaction(sender_account_id);
CREATE INDEX idx_transaction_receiver ON Transaction(receiver_account_id);
CREATE INDEX idx_transaction_amount ON Transaction(amount);
CREATE INDEX idx_transaction_fraud_score ON Transaction(fraud_score);
CREATE INDEX idx_transaction_flagged ON Transaction(is_flagged);
CREATE INDEX idx_account_client ON Account(client_id);
CREATE INDEX idx_account_number ON Account(account_number);
CREATE INDEX idx_client_phone ON Client(phone_number);
CREATE INDEX idx_client_email ON Client(email);
CREATE INDEX idx_client_risk_level ON Client(risk_level);
CREATE INDEX idx_device_fingerprint ON Device(device_fingerprint);
CREATE INDEX idx_device_risk_score ON Device(risk_score);
CREATE INDEX idx_ip_address ON IPAddress(ip_address);
CREATE INDEX idx_ip_risk_score ON IPAddress(risk_score);
CREATE INDEX idx_client_relationship_1 ON ClientRelationship(client_id_1);
CREATE INDEX idx_client_relationship_2 ON ClientRelationship(client_id_2);
CREATE INDEX idx_alert_client ON Alert(client_id);
CREATE INDEX idx_alert_status ON Alert(status);
CREATE INDEX idx_alert_date ON Alert(alert_date);
CREATE INDEX idx_session_client ON Session(client_id);
CREATE INDEX idx_session_date ON Session(session_start);
CREATE INDEX idx_velocity_client_metric ON VelocityCounter(client_id, metric_type, time_window);
CREATE INDEX idx_pattern_client ON TransactionPattern(client_id);
CREATE INDEX idx_pattern_active ON TransactionPattern(is_active);

-- Create composite indexes for complex queries
CREATE INDEX idx_transaction_composite ON Transaction(sender_account_id, transaction_date, amount);
CREATE INDEX idx_client_risk_composite ON Client(risk_level, is_blocked, account_status);
CREATE INDEX idx_alert_severity_status ON Alert(severity, status, alert_date);

-- Create functions for automatic calculations
CREATE OR REPLACE FUNCTION update_client_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE Client 
        SET 
            total_transactions = total_transactions + 1,
            total_amount_transferred = total_amount_transferred + NEW.amount,
            avg_transaction_amount = (total_amount_transferred + NEW.amount) / (total_transactions + 1),
            max_transaction_amount = GREATEST(max_transaction_amount, NEW.amount)
        WHERE client_id = (SELECT client_id FROM Account WHERE account_id = NEW.sender_account_id);
        
        UPDATE Account 
        SET 
            transaction_count_today = transaction_count_today + 1,
            amount_transferred_today = amount_transferred_today + NEW.amount,
            last_transaction_date = NEW.transaction_date
        WHERE account_id = NEW.sender_account_id;
        
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_client_stats
    AFTER INSERT ON Transaction
    FOR EACH ROW
    EXECUTE FUNCTION update_client_stats();

-- Function to calculate risk score based on multiple factors
CREATE OR REPLACE FUNCTION calculate_transaction_risk(
    p_amount DECIMAL,
    p_client_risk DECIMAL,
    p_device_risk DECIMAL,
    p_ip_risk DECIMAL,
    p_velocity_score DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    RETURN (
        p_amount * 0.3 +
        p_client_risk * 0.25 +
        p_device_risk * 0.2 +
        p_ip_risk * 0.15 +
        p_velocity_score * 0.1
    );
END;
$$ LANGUAGE plpgsql;

-- Enhanced sample data for testing
INSERT INTO Client (first_name, last_name, date_of_birth, phone_number, email, kyc_status, risk_level, risk_category) VALUES
('Ivan', 'Petrov', '1990-05-15', '+79991234567', 'ivan.petrov@email.com', 'verified', 0.1, 'low'),
('Maria', 'Sidorova', '1985-12-03', '+79997654321', 'maria.sidorova@email.com', 'verified', 0.05, 'low'),
('Alexey', 'Ivanov', '1992-08-21', '+79991112233', 'alexey.ivanov@email.com', 'pending', 0.3, 'medium'),
('Elena', 'Kuznetsova', '1988-03-15', '+79995556677', 'elena.kuznetsova@ suspicious.com', 'none', 0.8, 'high'),
('Dmitry', 'Smirnov', '1975-11-30', '+79994443322', 'dmitry.smirnov@email.com', 'verified', 0.6, 'medium');

INSERT INTO Account (client_id, account_number, account_type, balance, daily_limit, monthly_limit) VALUES
(1, '4276123456789012', 'card', 50000.00, 100000.0, 1000000.0),
(2, '4276987654321098', 'card', 30000.00, 50000.0, 500000.0),
(3, '4276112233445566', 'card', 15000.00, 75000.0, 750000.0),
(4, '4276998877665544', 'card', 200000.00, 50000.0, 500000.0),
(5, '4276555444333222', 'bank_account', 100000.00, 200000.0, 2000000.0);

INSERT INTO Device (device_fingerprint, device_type, os, browser, user_agent, risk_score, reputation_score) VALUES
('fingerprint_001', 'mobile', 'Android', 'Chrome', 'Mozilla/5.0 (Linux; Android 10) Chrome/91.0.4472.120 Mobile Safari/537.36', 0.1, 0.9),
('fingerprint_002', 'desktop', 'Windows', 'Firefox', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0', 0.05, 0.95),
('fingerprint_003', 'mobile', 'iOS', 'Safari', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/605.1.15', 0.2, 0.8),
('fingerprint_004', 'desktop', 'Windows', 'Chrome', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124', 0.8, 0.3),
('fingerprint_005', 'unknown', 'Unknown', 'Unknown', 'Suspicious User Agent', 0.9, 0.1);

INSERT INTO IPAddress (ip_address, country, city, latitude, longitude, isp, risk_score, threat_level, is_proxy) VALUES
('192.168.1.100', 'Russia', 'Moscow', 55.7558, 37.6173, 'MTS', 0.1, 'low', FALSE),
('192.168.1.101', 'Russia', 'Saint Petersburg', 59.9343, 30.3351, 'Beeline', 0.05, 'low', FALSE),
('178.62.123.45', 'Germany', 'Berlin', 52.5200, 13.4050, 'DigitalOcean', 0.7, 'high', TRUE),
('185.220.101.182', 'Unknown', 'Unknown', 0.0, 0.0, 'Tor Exit Node', 0.9, 'critical', TRUE),
('10.0.0.1', 'Russia', 'Moscow', 55.7558, 37.6173, 'Local Network', 0.3, 'medium', FALSE);

-- Enhanced sample transactions with various scenarios
INSERT INTO Transaction (sender_account_id, receiver_account_id, amount, transaction_type, status, ip_address_id, device_id, fraud_score, is_flagged, flagged_reason) VALUES
(1, 2, 5000.00, 'P2P', 'completed', 1, 1, 0.1, FALSE, NULL),
(2, 3, 3000.00, 'P2P', 'completed', 2, 2, 0.05, FALSE, NULL),
(3, 1, 1000.00, 'P2P', 'completed', 1, 1, 0.08, FALSE, NULL),
(4, 1, 50000.00, 'P2P', 'flagged', 3, 4, 0.85, TRUE, 'High amount from high-risk device'),
(5, 2, 75000.00, 'P2P', 'blocked', 4, 5, 0.95, TRUE, 'Transaction from Tor network'),
(1, 4, 15000.00, 'P2P', 'completed', 1, 1, 0.3, FALSE, NULL),
(2, 5, 25000.00, 'P2P', 'completed', 2, 2, 0.2, FALSE, NULL);

-- Enhanced rules with categories and priorities
INSERT INTO Rule (rule_name, rule_description, rule_category, rule_condition, weight, threshold, time_window, priority, auto_block) VALUES
('HighAmount', 'Transaction amount exceeds daily limit', 'amount', 'amount > daily_limit', 5.0, 100000.0, NULL, 1, FALSE),
('NewDevice', 'Transaction from a newly registered device', 'device', 'device_age_hours < 24', 3.0, NULL, '24h', 2, FALSE),
('HighRiskIP', 'Transaction from a high-risk IP address', 'network', 'ip_risk_score > 0.8', 4.0, 0.8, NULL, 1, TRUE),
('VelocityBurst', 'Multiple transactions in short time period', 'velocity', 'transaction_count > 10', 3.0, 10, '1hour', 2, FALSE),
('UnusualAmount', 'Transaction deviates from user average', 'behavior', 'amount > avg_amount * 5', 2.5, NULL, NULL, 3, FALSE),
('ProxyDetected', 'Transaction from proxy/VPN', 'network', 'is_proxy = TRUE', 4.5, NULL, NULL, 1, TRUE),
('TorDetected', 'Transaction from Tor network', 'network', 'is_tor = TRUE', 5.0, NULL, NULL, 1, TRUE),
('CarouselPattern', 'Circular transaction pattern detected', 'network', 'carousel_pattern = TRUE', 4.0, NULL, NULL, 2, FALSE),
('FailedLogins', 'Multiple failed login attempts', 'behavior', 'failed_attempts > 5', 3.5, 5, '1hour', 2, FALSE),
('CrossBorder', 'Transaction from unusual location', 'location', 'country != usual_country', 2.0, NULL, NULL, 3, FALSE);

-- Sample alerts
INSERT INTO Alert (alert_type, severity, client_id, account_id, transaction_id, rule_id, title, description, risk_score) VALUES
('fraud', 'high', 4, 4, 4, 1, 'High Amount Transaction', 'Transaction amount 50000.00 exceeds daily limit', 0.85),
('fraud', 'critical', 5, 5, 5, 7, 'Tor Network Usage', 'Transaction initiated from Tor exit node', 0.95),
('suspicious', 'medium', 1, 1, 6, 2, 'New Device Alert', 'Transaction from new device fingerprint', 0.3);

-- Sample transaction patterns
INSERT INTO TransactionPattern (pattern_type, client_id, account_ids, transaction_ids, start_date, end_date, transaction_count, total_amount, risk_score, description) VALUES
('carousel', 4, ARRAY[4,1,2], ARRAY[4,6,7], '2025-10-29 10:00:00', '2025-10-29 11:00:00', 3, 90000.00, 0.75, 'Circular transactions between accounts'),
('burst', 5, ARRAY[5,2,1], ARRAY[5,7,6], '2025-10-29 09:00:00', '2025-10-29 09:30:00', 3, 115000.00, 0.6, 'High velocity transactions in short period');

-- Sample velocity counters
INSERT INTO VelocityCounter (client_id, account_id, metric_type, time_window, counter_value, threshold) VALUES
(4, 4, 'transaction_count', '1hour', 3, 5),
(5, 5, 'amount', '1hour', 75000, 100000),
(1, 1, 'transaction_count', '1day', 3, 10);

-- Sample blacklist entries
INSERT INTO Blacklist (entity_type, entity_value, reason, risk_level, source, auto_block) VALUES
('ip', '185.220.101.182', 'Tor exit node', 'critical', 'threat_intelligence', TRUE),
('device', 'fingerprint_005', 'Suspicious user agent', 'high', 'behavioral_analysis', TRUE),
('email', 'elena.kuznetsova@ suspicious.com', 'Suspicious domain', 'medium', 'manual_review', FALSE);