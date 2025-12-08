# Anti-fraud Database for P2P Transfers

## Objective
Detect suspicious transactions based on behavioral and network characteristics.

## Entities

### 1. Client
- client_id (Primary Key)
- first_name
- last_name
- date_of_birth
- phone_number
- email
- registration_date
- kyc_status (Know Your Customer status)
- risk_level
- is_blocked

### 2. Account/Card
- account_id (Primary Key)
- client_id (Foreign Key to Client)
- account_number
- account_type (card, bank_account, digital_wallet)
- currency
- balance
- opening_date
- is_active
- daily_limit
- monthly_limit

### 3. Transaction
- transaction_id (Primary Key)
- sender_account_id (Foreign Key to Account)
- receiver_account_id (Foreign Key to Account)
- amount
- currency
- transaction_date
- transaction_type (P2P, merchant, ATM, etc.)
- status (completed, pending, failed, reversed)
- ip_address_id (Foreign Key to IP)
- device_id (Foreign Key to Device)
- location_coordinates
- description
- fraud_score
- is_flagged
- flagged_reason

### 4. Device
- device_id (Primary Key)
- device_fingerprint
- device_type (mobile, desktop, tablet)
- os
- browser
- user_agent
- first_seen_date
- last_seen_date
- risk_score

### 5. IP Address
- ip_address_id (Primary Key)
- ip_address
- geolocation_data
- isp
- first_seen_date
- last_seen_date
- risk_score
- is_proxy
- is_tor

### 6. Rules/Alerts
- rule_id (Primary Key)
- rule_name
- rule_description
- rule_condition
- weight
- is_active
- created_date
- last_modified_date

### 7. Blacklists
- blacklist_id (Primary Key)
- entity_type (client, account, ip, device)
- entity_id
- reason
- added_date
- expiry_date
- added_by

### 8. Client Relationships
- relationship_id (Primary Key)
- client_id_1 (Foreign Key to Client)
- client_id_2 (Foreign Key to Client)
- relationship_type (family, friend, colleague)
- since_date
- transaction_count
- total_amount_transferred

## Relationships

1. Client 1 → N Account/Card
2. Account/Card 1 → N Transaction (as sender)
3. Account/Card 1 → N Transaction (as receiver)
4. Transaction N → 1 IP Address
5. Transaction N → 1 Device
6. Client N → N Client (via Client Relationships)

## Indexes

1. Transaction: transaction_date, sender_account_id, receiver_account_id
2. Account: client_id, account_number
3. Client: phone_number, email
4. Device: device_fingerprint
5. IP: ip_address
6. Client Relationships: client_id_1, client_id_2

## Queries and Reports

### 1. Spike in Transfer Frequency
```sql
SELECT DATE(transaction_date) as day, COUNT(*) as transaction_count
FROM Transaction 
WHERE transaction_date >= NOW() - INTERVAL 7 DAY
GROUP BY DATE(transaction_date)
ORDER BY day;
```

### 2. Transfer "Carousels"
```sql
-- Find circular transfer patterns
WITH RECURSIVE transfer_chain AS (
  SELECT 
    transaction_id,
    sender_account_id,
    receiver_account_id,
    transaction_date,
    ARRAY[sender_account_id] as chain,
    1 as depth
  FROM Transaction
  WHERE transaction_date >= NOW() - INTERVAL 1 HOUR
  
  UNION ALL
  
  SELECT 
    t.transaction_id,
    t.sender_account_id,
    t.receiver_account_id,
    t.transaction_date,
    tc.chain || t.sender_account_id,
    tc.depth + 1
  FROM Transaction t
  JOIN transfer_chain tc ON t.sender_account_id = tc.receiver_account_id
  WHERE t.transaction_date >= tc.transaction_date 
    AND t.transaction_date <= tc.transaction_date + INTERVAL 1 HOUR
    AND NOT t.sender_account_id = ANY(tc.chain)
    AND tc.depth < 10
)
SELECT * FROM transfer_chain WHERE sender_account_id = ANY(chain) AND depth > 2;
```

### 3. Transactions with New Devices
```sql
SELECT t.*, d.*
FROM Transaction t
JOIN Device d ON t.device_id = d.device_id
WHERE d.first_seen_date >= NOW() - INTERVAL 24 HOUR;
```

### 4. Graph Queries for Connectivity Clusters
```sql
-- Find connected components of clients
WITH RECURSIVE client_network(client_id, component_id) AS (
  SELECT client_id_1 as client_id, MIN(client_id_1, client_id_2) as component_id
  FROM ClientRelationships
  
  UNION
  
  SELECT cr.client_id_2, cn.component_id
  FROM ClientRelationships cr
  JOIN client_network cn ON cr.client_id_1 = cn.client_id
)
SELECT component_id, COUNT(*) as component_size
FROM client_network
GROUP BY component_id
ORDER BY component_size DESC;
```

### 5. Scoring by Rules/Weights
```sql
SELECT 
  t.transaction_id,
  SUM(r.weight) as risk_score
FROM Transaction t
JOIN Rules r ON (
  -- Rule conditions would be evaluated here
  -- This is a simplified example
  CASE 
    WHEN t.amount > 10000 THEN r.rule_name = 'HighAmount'
    WHEN d.risk_score > 0.8 THEN r.rule_name = 'HighRiskDevice'
    WHEN ip.risk_score > 0.8 THEN r.rule_name = 'HighRiskIP'
    ELSE FALSE
  END
)
JOIN Device d ON t.device_id = d.device_id
JOIN IP_Address ip ON t.ip_address_id = ip.ip_address_id
WHERE r.is_active = TRUE
GROUP BY t.transaction_id
HAVING SUM(r.weight) > 5.0; -- Threshold for flagging
```

## Additional Considerations

1. **Real-time Processing**: Consider using streaming processing for real-time fraud detection
2. **Machine Learning Integration**: Store features for ML model training
3. **Audit Trail**: Log all fraud detection decisions for compliance
4. **Data Retention**: Define policies for data archival and deletion
5. **Privacy**: Ensure compliance with data protection regulations