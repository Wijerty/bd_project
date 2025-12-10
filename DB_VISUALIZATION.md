# Визуализация Базы Данных

Ниже представлена ER-диаграмма (Entity-Relationship) базы данных антифрод системы.
Вы можете открыть предварительный просмотр этого файла в VS Code (Ctrl+K V), чтобы увидеть отрендеренную диаграмму.

```mermaid
erDiagram
    Client ||--o{ Account : "owns"
    Client ||--o{ ClientRelationship : "participates in"
    
    Account ||--o{ Transaction : "sends"
    Account ||--o{ Transaction : "receives"
    
    Transaction }|--|| Device : "uses"
    Transaction }|--|| IPAddress : "originates from"
    
    Client {
        int client_id PK
        string first_name
        string last_name
        date date_of_birth
        string phone_number
        string email
        timestamp registration_date
        string kyc_status
        decimal risk_level
        boolean is_blocked
    }

    Account {
        int account_id PK
        int client_id FK
        string account_number
        string account_type
        string currency
        decimal balance
        timestamp opening_date
        boolean is_active
        decimal daily_limit
        decimal monthly_limit
    }

    Transaction {
        int transaction_id PK
        int sender_account_id FK
        int receiver_account_id FK
        decimal amount
        string currency
        timestamp transaction_date
        string transaction_type
        string status
        int ip_address_id FK
        int device_id FK
        point location_coordinates
        decimal fraud_score
        boolean is_flagged
        string flagged_reason
    }

    Device {
        int device_id PK
        string device_fingerprint
        string device_type
        string os
        string browser
        string user_agent
        timestamp first_seen_date
        timestamp last_seen_date
        decimal risk_score
    }

    IPAddress {
        int ip_address_id PK
        inet ip_address
        string country
        string city
        decimal latitude
        decimal longitude
        string isp
        timestamp first_seen_date
        timestamp last_seen_date
        decimal risk_score
        boolean is_proxy
        boolean is_tor
    }

    ClientRelationship {
        int relationship_id PK
        int client_id_1 FK
        int client_id_2 FK
        string relationship_type
        date since_date
        int transaction_count
        decimal total_amount_transferred
    }

    Rule {
        int rule_id PK
        string rule_name
        string rule_description
        string rule_condition
        decimal weight
        boolean is_active
    }

    Blacklist {
        int blacklist_id PK
        string entity_type
        int entity_id
        string reason
        timestamp added_date
        timestamp expiry_date
    }
```
