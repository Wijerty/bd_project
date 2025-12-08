-- =====================================================
-- Антифрод система для P2P переводов
-- Учебный проект: База данных Security Dashboard
-- =====================================================

-- Создание базы данных (выполнить отдельно от имени postgres)
-- CREATE DATABASE antifraud_p2p;
-- CREATE USER antifraud_user WITH PASSWORD 'antifraud_pass';
-- GRANT ALL PRIVILEGES ON DATABASE antifraud_p2p TO antifraud_user;

-- =====================================================
-- СОЗДАНИЕ ТАБЛИЦ
-- =====================================================

-- Таблица клиентов
CREATE TABLE IF NOT EXISTS Client (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    kyc_status VARCHAR(20) DEFAULT 'pending' CHECK (kyc_status IN ('pending', 'verified', 'rejected')),
    risk_level DECIMAL(3,2) DEFAULT 0.0 CHECK (risk_level >= 0 AND risk_level <= 1),
    is_blocked BOOLEAN DEFAULT FALSE
);

-- Таблица счетов
CREATE TABLE IF NOT EXISTS Account (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES Client(client_id) ON DELETE CASCADE,
    account_number VARCHAR(30) UNIQUE NOT NULL,
    account_type VARCHAR(20) DEFAULT 'standard' CHECK (account_type IN ('standard', 'premium', 'business')),
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'RUB',
    opening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица устройств
CREATE TABLE IF NOT EXISTS Device (
    device_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES Client(client_id) ON DELETE SET NULL,
    device_fingerprint VARCHAR(255) UNIQUE NOT NULL,
    device_type VARCHAR(50),
    os VARCHAR(100),
    browser VARCHAR(100),
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_trusted BOOLEAN DEFAULT FALSE
);

-- Таблица IP-адресов
CREATE TABLE IF NOT EXISTS IPAddress (
    ip_address_id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100),
    is_proxy BOOLEAN DEFAULT FALSE,
    is_vpn BOOLEAN DEFAULT FALSE,
    is_tor BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица транзакций
CREATE TABLE IF NOT EXISTS Transaction (
    transaction_id SERIAL PRIMARY KEY,
    sender_account_id INTEGER NOT NULL REFERENCES Account(account_id),
    receiver_account_id INTEGER NOT NULL REFERENCES Account(account_id),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'RUB',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(30) DEFAULT 'transfer' CHECK (transaction_type IN ('transfer', 'payment', 'withdrawal', 'deposit')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'blocked', 'review')),
    location_coordinates VARCHAR(100),
    description TEXT,
    device_id INTEGER REFERENCES Device(device_id),
    ip_address_id INTEGER REFERENCES IPAddress(ip_address_id),
    fraud_score DECIMAL(3,2) DEFAULT 0.0 CHECK (fraud_score >= 0 AND fraud_score <= 1),
    is_flagged BOOLEAN DEFAULT FALSE,
    flagged_reason TEXT
);

-- Таблица правил антифрода
CREATE TABLE IF NOT EXISTS FraudRule (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    rule_type VARCHAR(50),
    threshold_value DECIMAL(15,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица алертов
CREATE TABLE IF NOT EXISTS Alert (
    alert_id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES Transaction(transaction_id),
    client_id INTEGER REFERENCES Client(client_id),
    rule_id INTEGER REFERENCES FraudRule(rule_id),
    alert_type VARCHAR(50),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    notes TEXT
);

-- Таблица логов аудита
CREATE TABLE IF NOT EXISTS AuditLog (
    log_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- СОЗДАНИЕ ИНДЕКСОВ
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_transaction_date ON Transaction(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transaction_sender ON Transaction(sender_account_id);
CREATE INDEX IF NOT EXISTS idx_transaction_receiver ON Transaction(receiver_account_id);
CREATE INDEX IF NOT EXISTS idx_transaction_flagged ON Transaction(is_flagged);
CREATE INDEX IF NOT EXISTS idx_transaction_fraud_score ON Transaction(fraud_score);
CREATE INDEX IF NOT EXISTS idx_client_risk ON Client(risk_level);
CREATE INDEX IF NOT EXISTS idx_client_blocked ON Client(is_blocked);
CREATE INDEX IF NOT EXISTS idx_account_client ON Account(client_id);
CREATE INDEX IF NOT EXISTS idx_alert_status ON Alert(status);
CREATE INDEX IF NOT EXISTS idx_alert_severity ON Alert(severity);

-- =====================================================
-- ЗАПОЛНЕНИЕ ТЕСТОВЫМИ ДАННЫМИ
-- =====================================================

-- Клиенты
INSERT INTO Client (first_name, last_name, date_of_birth, phone_number, email, kyc_status, risk_level, is_blocked) VALUES
('Александр', 'Иванов', '1985-03-15', '+79161234567', 'ivanov@mail.ru', 'verified', 0.1, FALSE),
('Мария', 'Петрова', '1990-07-22', '+79162345678', 'petrova@gmail.com', 'verified', 0.15, FALSE),
('Дмитрий', 'Сидоров', '1988-11-08', '+79163456789', 'sidorov@yandex.ru', 'verified', 0.2, FALSE),
('Елена', 'Козлова', '1995-01-30', '+79164567890', 'kozlova@mail.ru', 'verified', 0.05, FALSE),
('Сергей', 'Новиков', '1982-06-12', '+79165678901', 'novikov@gmail.com', 'verified', 0.3, FALSE),
('Анна', 'Морозова', '1993-09-25', '+79166789012', 'morozova@yandex.ru', 'verified', 0.1, FALSE),
('Павел', 'Волков', '1987-04-18', '+79167890123', 'volkov@mail.ru', 'pending', 0.4, FALSE),
('Ольга', 'Соколова', '1991-12-03', '+79168901234', 'sokolova@gmail.com', 'verified', 0.2, FALSE),
('Игорь', 'Лебедев', '1979-08-27', '+79169012345', 'lebedev@yandex.ru', 'verified', 0.55, FALSE),
('Татьяна', 'Кузнецова', '1986-02-14', '+79160123456', 'kuznetsova@mail.ru', 'verified', 0.1, FALSE),
('Андрей', 'Попов', '1984-05-20', '+79171234567', 'popov@gmail.com', 'rejected', 0.75, TRUE),
('Наталья', 'Васильева', '1992-10-11', '+79172345678', 'vasilieva@yandex.ru', 'verified', 0.15, FALSE),
('Виктор', 'Зайцев', '1980-07-05', '+79173456789', 'zaitsev@mail.ru', 'verified', 0.8, TRUE),
('Екатерина', 'Павлова', '1994-03-28', '+79174567890', 'pavlova@gmail.com', 'verified', 0.1, FALSE),
('Михаил', 'Семенов', '1983-11-16', '+79175678901', 'semenov@yandex.ru', 'verified', 0.25, FALSE);

-- Счета
INSERT INTO Account (client_id, account_number, account_type, balance, currency) VALUES
(1, '40817810099910004001', 'standard', 150000.00, 'RUB'),
(1, '40817810099910004002', 'premium', 500000.00, 'RUB'),
(2, '40817810099910004003', 'standard', 75000.00, 'RUB'),
(3, '40817810099910004004', 'business', 1200000.00, 'RUB'),
(4, '40817810099910004005', 'standard', 45000.00, 'RUB'),
(5, '40817810099910004006', 'premium', 320000.00, 'RUB'),
(6, '40817810099910004007', 'standard', 180000.00, 'RUB'),
(7, '40817810099910004008', 'standard', 25000.00, 'RUB'),
(8, '40817810099910004009', 'business', 890000.00, 'RUB'),
(9, '40817810099910004010', 'standard', 560000.00, 'RUB'),
(10, '40817810099910004011', 'standard', 95000.00, 'RUB'),
(11, '40817810099910004012', 'standard', 0.00, 'RUB'),
(12, '40817810099910004013', 'premium', 420000.00, 'RUB'),
(13, '40817810099910004014', 'standard', 15000.00, 'RUB'),
(14, '40817810099910004015', 'standard', 230000.00, 'RUB'),
(15, '40817810099910004016', 'business', 780000.00, 'RUB');

-- Устройства
INSERT INTO Device (client_id, device_fingerprint, device_type, os, browser, is_trusted) VALUES
(1, 'fp_a1b2c3d4e5f6', 'mobile', 'iOS 17.1', 'Safari', TRUE),
(1, 'fp_g7h8i9j0k1l2', 'desktop', 'Windows 11', 'Chrome 119', TRUE),
(2, 'fp_m3n4o5p6q7r8', 'mobile', 'Android 14', 'Chrome Mobile', TRUE),
(3, 'fp_s9t0u1v2w3x4', 'desktop', 'macOS 14', 'Safari 17', TRUE),
(4, 'fp_y5z6a7b8c9d0', 'mobile', 'iOS 16.5', 'Safari', TRUE),
(5, 'fp_e1f2g3h4i5j6', 'desktop', 'Windows 10', 'Firefox 120', TRUE),
(6, 'fp_k7l8m9n0o1p2', 'mobile', 'Android 13', 'Chrome Mobile', TRUE),
(7, 'fp_q3r4s5t6u7v8', 'desktop', 'Linux', 'Firefox 119', FALSE),
(8, 'fp_w9x0y1z2a3b4', 'tablet', 'iPadOS 17', 'Safari', TRUE),
(9, 'fp_c5d6e7f8g9h0', 'desktop', 'Windows 11', 'Edge 119', FALSE),
(10, 'fp_i1j2k3l4m5n6', 'mobile', 'iOS 17.0', 'Safari', TRUE),
(11, 'fp_suspicious_01', 'desktop', 'Unknown', 'Tor Browser', FALSE),
(12, 'fp_o7p8q9r0s1t2', 'mobile', 'Android 14', 'Samsung Browser', TRUE),
(13, 'fp_suspicious_02', 'desktop', 'Windows 7', 'Chrome 90', FALSE),
(14, 'fp_u3v4w5x6y7z8', 'mobile', 'iOS 17.1', 'Safari', TRUE),
(15, 'fp_a9b0c1d2e3f4', 'desktop', 'macOS 13', 'Chrome 119', TRUE);

-- IP-адреса
INSERT INTO IPAddress (ip_address, country, city, is_proxy, is_vpn, is_tor, risk_score) VALUES
('185.212.45.67', 'Россия', 'Москва', FALSE, FALSE, FALSE, 0.1),
('91.234.56.78', 'Россия', 'Санкт-Петербург', FALSE, FALSE, FALSE, 0.1),
('77.88.99.100', 'Россия', 'Новосибирск', FALSE, FALSE, FALSE, 0.15),
('195.208.12.34', 'Россия', 'Екатеринбург', FALSE, FALSE, FALSE, 0.1),
('46.29.56.78', 'Россия', 'Казань', FALSE, FALSE, FALSE, 0.1),
('178.154.200.100', 'Россия', 'Нижний Новгород', FALSE, FALSE, FALSE, 0.1),
('5.255.88.90', 'Россия', 'Самара', FALSE, FALSE, FALSE, 0.15),
('89.108.67.89', 'Россия', 'Ростов-на-Дону', FALSE, FALSE, FALSE, 0.1),
('185.156.78.90', 'Нидерланды', 'Амстердам', TRUE, TRUE, FALSE, 0.7),
('103.45.67.89', 'Китай', 'Пекин', FALSE, FALSE, FALSE, 0.4),
('45.33.32.156', 'США', 'Нью-Йорк', FALSE, TRUE, FALSE, 0.5),
('185.220.101.45', 'Германия', 'Франкфурт', FALSE, FALSE, TRUE, 0.9),
('91.219.236.78', 'Украина', 'Киев', TRUE, FALSE, FALSE, 0.6),
('194.87.234.56', 'Россия', 'Краснодар', FALSE, FALSE, FALSE, 0.1),
('80.78.90.123', 'Россия', 'Воронеж', FALSE, FALSE, FALSE, 0.1);

-- Правила антифрода
INSERT INTO FraudRule (rule_name, rule_description, rule_type, threshold_value, is_active) VALUES
('Большая сумма перевода', 'Транзакция превышает 100,000 рублей', 'amount', 100000.00, TRUE),
('Подозрительный IP', 'Транзакция с IP через VPN/Tor/Proxy', 'ip_check', NULL, TRUE),
('Множественные переводы', 'Более 10 переводов за час', 'velocity', 10.00, TRUE),
('Новое устройство', 'Транзакция с неизвестного устройства', 'device', NULL, TRUE),
('Ночные транзакции', 'Транзакции между 00:00 и 06:00', 'time', NULL, TRUE),
('Круглая сумма', 'Подозрительно круглые суммы перевода', 'pattern', NULL, TRUE),
('Географическая аномалия', 'Транзакция из другой страны', 'geo', NULL, TRUE),
('Высокий риск получателя', 'Получатель с высоким уровнем риска', 'recipient', 0.5, TRUE),
('Новый клиент большой перевод', 'Большой перевод от нового клиента', 'new_client', 50000.00, TRUE),
('Частая смена устройств', 'Клиент использует много разных устройств', 'device_velocity', 5.00, TRUE);

-- Транзакции (генерация за последние 7 дней)
INSERT INTO Transaction (sender_account_id, receiver_account_id, amount, currency, transaction_date, transaction_type, status, device_id, ip_address_id, fraud_score, is_flagged, flagged_reason) VALUES
-- Обычные транзакции
(1, 3, 5000.00, 'RUB', NOW() - INTERVAL '6 days 10 hours', 'transfer', 'completed', 1, 1, 0.05, FALSE, NULL),
(2, 5, 15000.00, 'RUB', NOW() - INTERVAL '6 days 8 hours', 'transfer', 'completed', 2, 1, 0.1, FALSE, NULL),
(3, 7, 3500.00, 'RUB', NOW() - INTERVAL '6 days 5 hours', 'transfer', 'completed', 3, 2, 0.05, FALSE, NULL),
(4, 1, 25000.00, 'RUB', NOW() - INTERVAL '5 days 22 hours', 'transfer', 'completed', 4, 3, 0.15, FALSE, NULL),
(5, 9, 8000.00, 'RUB', NOW() - INTERVAL '5 days 18 hours', 'transfer', 'completed', 5, 4, 0.08, FALSE, NULL),
(6, 11, 12000.00, 'RUB', NOW() - INTERVAL '5 days 14 hours', 'transfer', 'completed', 6, 5, 0.1, FALSE, NULL),
(7, 3, 2000.00, 'RUB', NOW() - INTERVAL '5 days 10 hours', 'transfer', 'completed', 7, 6, 0.12, FALSE, NULL),
(8, 15, 45000.00, 'RUB', NOW() - INTERVAL '5 days 6 hours', 'transfer', 'completed', 8, 7, 0.2, FALSE, NULL),
(9, 1, 7500.00, 'RUB', NOW() - INTERVAL '4 days 23 hours', 'transfer', 'completed', 9, 8, 0.1, FALSE, NULL),
(10, 5, 18000.00, 'RUB', NOW() - INTERVAL '4 days 19 hours', 'transfer', 'completed', 10, 1, 0.12, FALSE, NULL),

-- Подозрительные транзакции
(11, 14, 150000.00, 'RUB', NOW() - INTERVAL '4 days 15 hours', 'transfer', 'review', 11, 9, 0.75, TRUE, 'Большая сумма перевода с VPN'),
(12, 8, 99000.00, 'RUB', NOW() - INTERVAL '4 days 11 hours', 'transfer', 'blocked', 11, 12, 0.85, TRUE, 'Транзакция через Tor'),
(13, 3, 200000.00, 'RUB', NOW() - INTERVAL '4 days 7 hours', 'transfer', 'blocked', 13, 10, 0.9, TRUE, 'Заблокированный клиент, большая сумма'),

-- Ещё обычные транзакции
(1, 7, 4200.00, 'RUB', NOW() - INTERVAL '4 days 3 hours', 'transfer', 'completed', 1, 1, 0.05, FALSE, NULL),
(2, 9, 6800.00, 'RUB', NOW() - INTERVAL '3 days 22 hours', 'transfer', 'completed', 2, 2, 0.08, FALSE, NULL),
(3, 11, 11000.00, 'RUB', NOW() - INTERVAL '3 days 18 hours', 'transfer', 'completed', 3, 3, 0.1, FALSE, NULL),
(4, 15, 33000.00, 'RUB', NOW() - INTERVAL '3 days 14 hours', 'transfer', 'completed', 4, 4, 0.15, FALSE, NULL),
(5, 1, 9500.00, 'RUB', NOW() - INTERVAL '3 days 10 hours', 'transfer', 'completed', 5, 5, 0.1, FALSE, NULL),
(6, 3, 2800.00, 'RUB', NOW() - INTERVAL '3 days 6 hours', 'transfer', 'completed', 6, 6, 0.05, FALSE, NULL),
(7, 5, 16000.00, 'RUB', NOW() - INTERVAL '3 days 2 hours', 'transfer', 'completed', 7, 7, 0.12, FALSE, NULL),

-- Подозрительные транзакции (ночные, круглые суммы)
(9, 12, 50000.00, 'RUB', NOW() - INTERVAL '2 days 3 hours', 'transfer', 'review', 9, 11, 0.65, TRUE, 'Ночная транзакция, круглая сумма'),
(10, 14, 100000.00, 'RUB', NOW() - INTERVAL '2 days 2 hours', 'transfer', 'review', 10, 13, 0.7, TRUE, 'Подозрительный IP, большая сумма'),

-- Обычные транзакции за последние 2 дня
(1, 5, 7300.00, 'RUB', NOW() - INTERVAL '2 days', 'transfer', 'completed', 1, 1, 0.05, FALSE, NULL),
(2, 7, 4100.00, 'RUB', NOW() - INTERVAL '1 day 20 hours', 'transfer', 'completed', 2, 2, 0.08, FALSE, NULL),
(3, 9, 19000.00, 'RUB', NOW() - INTERVAL '1 day 16 hours', 'transfer', 'completed', 3, 3, 0.1, FALSE, NULL),
(4, 11, 5600.00, 'RUB', NOW() - INTERVAL '1 day 12 hours', 'transfer', 'completed', 4, 4, 0.05, FALSE, NULL),
(5, 13, 8800.00, 'RUB', NOW() - INTERVAL '1 day 8 hours', 'transfer', 'completed', 5, 5, 0.1, FALSE, NULL),
(6, 15, 22000.00, 'RUB', NOW() - INTERVAL '1 day 4 hours', 'transfer', 'completed', 6, 6, 0.12, FALSE, NULL),
(7, 1, 3200.00, 'RUB', NOW() - INTERVAL '1 day', 'transfer', 'completed', 7, 7, 0.08, FALSE, NULL),
(8, 3, 14500.00, 'RUB', NOW() - INTERVAL '20 hours', 'transfer', 'completed', 8, 8, 0.1, FALSE, NULL),
(9, 5, 6700.00, 'RUB', NOW() - INTERVAL '16 hours', 'transfer', 'completed', 9, 1, 0.15, FALSE, NULL),
(10, 7, 28000.00, 'RUB', NOW() - INTERVAL '12 hours', 'transfer', 'completed', 10, 2, 0.18, FALSE, NULL),

-- Транзакции за последние часы
(1, 9, 9200.00, 'RUB', NOW() - INTERVAL '8 hours', 'transfer', 'completed', 1, 1, 0.05, FALSE, NULL),
(2, 11, 5500.00, 'RUB', NOW() - INTERVAL '6 hours', 'transfer', 'completed', 2, 2, 0.08, FALSE, NULL),
(3, 13, 17000.00, 'RUB', NOW() - INTERVAL '4 hours', 'transfer', 'completed', 3, 3, 0.1, FALSE, NULL),
(4, 15, 4300.00, 'RUB', NOW() - INTERVAL '3 hours', 'transfer', 'completed', 4, 4, 0.05, FALSE, NULL),
(5, 1, 11500.00, 'RUB', NOW() - INTERVAL '2 hours', 'transfer', 'completed', 5, 5, 0.1, FALSE, NULL),
(6, 3, 8100.00, 'RUB', NOW() - INTERVAL '1 hour', 'transfer', 'completed', 6, 6, 0.08, FALSE, NULL),

-- Последние подозрительные транзакции
(14, 12, 75000.00, 'RUB', NOW() - INTERVAL '30 minutes', 'transfer', 'review', 14, 9, 0.6, TRUE, 'Подозрительный паттерн переводов'),
(10, 8, 120000.00, 'RUB', NOW() - INTERVAL '15 minutes', 'transfer', 'pending', 9, 11, 0.72, TRUE, 'Большая сумма, клиент с повышенным риском');

-- Алерты
INSERT INTO Alert (transaction_id, client_id, rule_id, alert_type, severity, status, notes) VALUES
(11, 11, 1, 'high_amount', 'high', 'investigating', 'Клиент совершил крупный перевод через VPN'),
(12, 11, 2, 'suspicious_ip', 'critical', 'resolved', 'Транзакция заблокирована автоматически'),
(13, 13, 1, 'high_amount', 'critical', 'resolved', 'Заблокированный клиент пытался совершить перевод'),
(21, 9, 5, 'night_transaction', 'medium', 'open', 'Ночная транзакция на крупную сумму'),
(22, 10, 7, 'geo_anomaly', 'high', 'investigating', 'Транзакция с подозрительного IP'),
(39, 14, 6, 'pattern', 'medium', 'open', 'Необычный паттерн переводов'),
(40, 9, 1, 'high_amount', 'high', 'open', 'Крупный перевод от клиента с повышенным риском');

-- Логи аудита
INSERT INTO AuditLog (user_id, action_type, table_name, record_id, new_value, ip_address) VALUES
('admin', 'CREATE', 'Client', 1, '{"first_name": "Александр", "last_name": "Иванов"}', '192.168.1.100'),
('admin', 'CREATE', 'Client', 2, '{"first_name": "Мария", "last_name": "Петрова"}', '192.168.1.100'),
('system', 'UPDATE', 'Transaction', 12, '{"status": "blocked"}', '127.0.0.1'),
('system', 'UPDATE', 'Transaction', 13, '{"status": "blocked"}', '127.0.0.1'),
('analyst1', 'UPDATE', 'Client', 11, '{"is_blocked": true}', '192.168.1.105'),
('analyst1', 'UPDATE', 'Client', 13, '{"is_blocked": true}', '192.168.1.105'),
('system', 'CREATE', 'Alert', 1, '{"severity": "high", "status": "open"}', '127.0.0.1'),
('system', 'CREATE', 'Alert', 2, '{"severity": "critical", "status": "open"}', '127.0.0.1');

-- =====================================================
-- ВЬЮХИ ДЛЯ ОТЧЁТОВ
-- =====================================================

-- Вьюха для подозрительных транзакций
CREATE OR REPLACE VIEW v_suspicious_transactions AS
SELECT 
    t.transaction_id,
    t.amount,
    t.currency,
    t.transaction_date,
    t.status,
    t.fraud_score,
    t.flagged_reason,
    c1.first_name || ' ' || c1.last_name as sender_name,
    c2.first_name || ' ' || c2.last_name as receiver_name,
    s.account_number as sender_account,
    r.account_number as receiver_account,
    ip.country,
    ip.is_vpn,
    ip.is_tor
FROM Transaction t
JOIN Account s ON t.sender_account_id = s.account_id
JOIN Account r ON t.receiver_account_id = r.account_id
JOIN Client c1 ON s.client_id = c1.client_id
JOIN Client c2 ON r.client_id = c2.client_id
LEFT JOIN IPAddress ip ON t.ip_address_id = ip.ip_address_id
WHERE t.is_flagged = TRUE
ORDER BY t.fraud_score DESC;

-- Вьюха для статистики по клиентам
CREATE OR REPLACE VIEW v_client_statistics AS
SELECT 
    c.client_id,
    c.first_name,
    c.last_name,
    c.risk_level,
    c.is_blocked,
    COUNT(DISTINCT a.account_id) as account_count,
    COALESCE(SUM(a.balance), 0) as total_balance,
    COUNT(DISTINCT t.transaction_id) as transaction_count,
    COALESCE(SUM(t.amount), 0) as total_sent
FROM Client c
LEFT JOIN Account a ON c.client_id = a.client_id
LEFT JOIN Transaction t ON a.account_id = t.sender_account_id
GROUP BY c.client_id, c.first_name, c.last_name, c.risk_level, c.is_blocked;

-- =====================================================
-- ФУНКЦИИ
-- =====================================================

-- Функция для расчёта fraud score
CREATE OR REPLACE FUNCTION calculate_fraud_score(
    p_amount DECIMAL,
    p_is_vpn BOOLEAN,
    p_is_tor BOOLEAN,
    p_sender_risk DECIMAL,
    p_is_night BOOLEAN
) RETURNS DECIMAL AS $$
DECLARE
    score DECIMAL := 0.0;
BEGIN
    -- Базовый скор от суммы
    IF p_amount > 100000 THEN
        score := score + 0.3;
    ELSIF p_amount > 50000 THEN
        score := score + 0.15;
    END IF;
    
    -- VPN/Tor
    IF p_is_tor THEN
        score := score + 0.4;
    ELSIF p_is_vpn THEN
        score := score + 0.2;
    END IF;
    
    -- Риск отправителя
    score := score + (p_sender_risk * 0.3);
    
    -- Ночное время
    IF p_is_night THEN
        score := score + 0.1;
    END IF;
    
    -- Ограничение максимума
    IF score > 1.0 THEN
        score := 1.0;
    END IF;
    
    RETURN ROUND(score, 2);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ВЫДАЧА ПРАВ (после создания пользователя)
-- =====================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO antifraud_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO antifraud_user;

SELECT 'База данных успешно создана и заполнена тестовыми данными!' as status;
