-- Additional tables and modifications for enhanced anti-fraud system

-- Add new columns to existing tables
ALTER TABLE Client ADD COLUMN IF NOT EXISTS block_reason TEXT;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS last_login_date TIMESTAMP;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'closed'));
ALTER TABLE Client ADD COLUMN IF NOT EXISTS risk_category VARCHAR(20) DEFAULT 'low' CHECK (risk_category IN ('low', 'medium', 'high', 'critical'));
ALTER TABLE Client ADD COLUMN IF NOT EXISTS total_transactions INTEGER DEFAULT 0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS total_amount_transferred DECIMAL(15,2) DEFAULT 0.0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS avg_transaction_amount DECIMAL(15,2) DEFAULT 0.0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS max_transaction_amount DECIMAL(15,2) DEFAULT 0.0;
ALTER TABLE Client ADD COLUMN IF NOT EXISTS preferred_device_ids INTEGER[];
ALTER TABLE Client ADD COLUMN IF NOT EXISTS preferred_ip_addresses INTEGER[];
ALTER TABLE Client ADD COLUMN IF NOT EXISTS behavior_score DECIMAL(5,2) DEFAULT 0.0;

ALTER TABLE Account ADD COLUMN IF NOT EXISTS card_expiry_date DATE;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS card_type VARCHAR(20);
ALTER TABLE Account ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100);
ALTER TABLE Account ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS last_transaction_date TIMESTAMP;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS transaction_count_today INTEGER DEFAULT 0;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS transaction_count_month INTEGER DEFAULT 0;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS amount_transferred_today DECIMAL(15,2) DEFAULT 0.0;
ALTER TABLE Account ADD COLUMN IF NOT EXISTS amount_transferred_month DECIMAL(15,2) DEFAULT 0.0;

ALTER TABLE Device ADD COLUMN IF NOT EXISTS os_version VARCHAR(20);
ALTER TABLE Device ADD COLUMN IF NOT EXISTS browser_version VARCHAR(20);
ALTER TABLE Device ADD COLUMN IF NOT EXISTS screen_resolution VARCHAR(20);
ALTER TABLE Device ADD COLUMN IF NOT EXISTS timezone VARCHAR(50);
ALTER TABLE Device ADD COLUMN IF NOT EXISTS language VARCHAR(10);
ALTER TABLE Device ADD COLUMN IF NOT EXISTS is_emulator BOOLEAN DEFAULT FALSE;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS is_rooted BOOLEAN DEFAULT FALSE;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS vpn_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS transaction_count INTEGER DEFAULT 0;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS unique_clients_used INTEGER DEFAULT 0;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS device_age_hours INTEGER DEFAULT 0;
ALTER TABLE Device ADD COLUMN IF NOT EXISTS reputation_score DECIMAL(5,2) DEFAULT 0.0;

ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS country_code VARCHAR(2);
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS region VARCHAR(100);
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS organization VARCHAR(100);
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS asn VARCHAR(20);
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS is_vpn BOOLEAN DEFAULT FALSE;
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS is_datacenter BOOLEAN DEFAULT FALSE;
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS is_mobile BOOLEAN DEFAULT FALSE;
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS threat_level VARCHAR(20) DEFAULT 'low' CHECK (threat_level IN ('low', 'medium', 'high', 'critical'));
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS transaction_count INTEGER DEFAULT 0;
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS unique_clients_used INTEGER DEFAULT 0;
ALTER TABLE IPAddress ADD COLUMN IF NOT EXISTS reputation_score DECIMAL(5,2) DEFAULT 0.0;

ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS location_city VARCHAR(100);
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS location_country VARCHAR(100);
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS risk_factors TEXT[];
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS merchant_category_code VARCHAR(10);
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS reference_number VARCHAR(100);
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS chargeback_risk DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS velocity_score DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS anomaly_score DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE "Transaction" ADD COLUMN IF NOT EXISTS is_suspicious BOOLEAN DEFAULT FALSE;

-- Add new status to Transaction check constraint
ALTER TABLE "Transaction" DROP CONSTRAINT IF EXISTS transaction_status_check;
ALTER TABLE "Transaction" ADD CONSTRAINT transaction_status_check 
    CHECK (status IN ('completed', 'pending', 'failed', 'reversed', 'flagged', 'blocked'));

ALTER TABLE Rule ADD COLUMN IF NOT EXISTS rule_category VARCHAR(50) CHECK (rule_category IN ('amount', 'velocity', 'behavior', 'network', 'device', 'location'));
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS threshold DECIMAL(15,2);
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS time_window VARCHAR(20);
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 1;
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS auto_block BOOLEAN DEFAULT FALSE;
ALTER TABLE Rule ADD COLUMN IF NOT EXISTS notification_required BOOLEAN DEFAULT TRUE;

ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS entity_value VARCHAR(255);
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) DEFAULT 'high' CHECK (risk_level IN ('low', 'medium', 'high', 'critical'));
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS source VARCHAR(50);
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP;
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS added_by VARCHAR(100);
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE Blacklist ADD COLUMN IF NOT EXISTS auto_block BOOLEAN DEFAULT TRUE;

ALTER TABLE ClientRelationship ADD COLUMN IF NOT EXISTS relationship_strength DECIMAL(3,2) DEFAULT 0.5;
ALTER TABLE ClientRelationship ADD COLUMN IF NOT EXISTS avg_transaction_amount DECIMAL(15,2) DEFAULT 0.0;
ALTER TABLE ClientRelationship ADD COLUMN IF NOT EXISTS last_transaction_date TIMESTAMP;
ALTER TABLE ClientRelationship ADD COLUMN IF NOT EXISTS is_suspicious BOOLEAN DEFAULT FALSE;
ALTER TABLE ClientRelationship ADD COLUMN IF NOT EXISTS risk_score DECIMAL(5,2) DEFAULT 0.0;

-- Create new tables
CREATE TABLE IF NOT EXISTS TransactionPattern (
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

CREATE TABLE IF NOT EXISTS Alert (
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

CREATE TABLE IF NOT EXISTS Session (
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

CREATE TABLE IF NOT EXISTS VelocityCounter (
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

CREATE TABLE IF NOT EXISTS RiskScoreHistory (
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

-- Create additional indexes
CREATE INDEX IF NOT EXISTS idx_transaction_amount ON "Transaction"(amount);
CREATE INDEX IF NOT EXISTS idx_transaction_fraud_score ON "Transaction"(fraud_score);
CREATE INDEX IF NOT EXISTS idx_transaction_flagged ON "Transaction"(is_flagged);
CREATE INDEX IF NOT EXISTS idx_client_risk_level ON Client(risk_level);
CREATE INDEX IF NOT EXISTS idx_device_risk_score ON Device(risk_score);
CREATE INDEX IF NOT EXISTS idx_ip_risk_score ON IPAddress(risk_score);
CREATE INDEX IF NOT EXISTS idx_alert_client ON Alert(client_id);
CREATE INDEX IF NOT EXISTS idx_alert_status ON Alert(status);
CREATE INDEX IF NOT EXISTS idx_alert_date ON Alert(alert_date);
CREATE INDEX IF NOT EXISTS idx_session_client ON Session(client_id);
CREATE INDEX IF NOT EXISTS idx_session_date ON Session(session_start);
CREATE INDEX IF NOT EXISTS idx_velocity_client_metric ON VelocityCounter(client_id, metric_type, time_window);
CREATE INDEX IF NOT EXISTS idx_pattern_client ON TransactionPattern(client_id);
CREATE INDEX IF NOT EXISTS idx_pattern_active ON TransactionPattern(is_active);

-- Create composite indexes
CREATE INDEX IF NOT EXISTS idx_transaction_composite ON "Transaction"(sender_account_id, transaction_date, amount);
CREATE INDEX IF NOT EXISTS idx_client_risk_composite ON Client(risk_level, is_blocked, account_status);
CREATE INDEX IF NOT EXISTS idx_alert_severity_status ON Alert(severity, status, alert_date);

-- Create functions for automatic calculations
CREATE OR REPLACE FUNCTION update_client_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE Client 
        SET 
            total_transactions = total_transactions + 1,
            total_amount_transferred = total_amount_transferred + NEW.amount,
            avg_transaction_amount = COALESCE((total_amount_transferred + NEW.amount) / (total_transactions + 1), NEW.amount),
            max_transaction_amount = GREATEST(COALESCE(max_transaction_amount, 0), NEW.amount)
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

DROP TRIGGER IF EXISTS trigger_update_client_stats ON "Transaction";
CREATE TRIGGER trigger_update_client_stats
    AFTER INSERT ON "Transaction"
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