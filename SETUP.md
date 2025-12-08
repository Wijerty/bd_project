# Anti-fraud System for P2P Transfers - Setup Guide

## Overview

This document provides instructions for setting up and using the anti-fraud system for P2P transfers.

## Prerequisites

1. Docker and Docker Compose installed
2. Python 3.7 or higher (for the fraud detection script)

## Setup Instructions

### 1. Database Setup with Docker

1. Navigate to the project directory:
   ```
   cd /path/to/bd_project
   ```

2. Build and start the database using Docker Compose:
   ```
   docker-compose up -d
   ```

3. The database will be available at:
   - Host: localhost
   - Port: 5432
   - Database: antifraud_p2p
   - User: antifraud_user
   - Password: antifraud_pass

4. Adminer (web-based database management tool) will be available at:
   - URL: http://localhost:8080

### 2. Manual Database Setup (Alternative)

If you prefer to set up the database manually:

1. Install PostgreSQL (version 12 or higher recommended)

2. Create the database:
   ```sql
   CREATE DATABASE antifraud_p2p;
   CREATE USER antifraud_user WITH PASSWORD 'antifraud_pass';
   GRANT ALL PRIVILEGES ON DATABASE antifraud_p2p TO antifraud_user;
   ```

3. Apply the schema:
   ```
   psql -U antifraud_user -d antifraud_p2p -f schema.sql
   ```

## Python Script Setup

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Update the database configuration in `fraud_detection.py`:
   ```python
   db_config = {
       'host': 'localhost',
       'database': 'antifraud_p2p',
       'user': 'antifraud_user',
       'password': 'antifraud_pass'
   }
   ```

3. Run the fraud detection script:
   ```
   python fraud_detection.py
   ```

## Database Schema Overview

The database contains the following tables:

1. **Client** - Stores client information
2. **Account** - Stores account/card information
3. **Transaction** - Records all transactions
4. **Device** - Tracks device information
5. **IPAddress** - Stores IP address details
6. **Rule** - Defines fraud detection rules
7. **Blacklist** - Contains blacklisted entities
8. **ClientRelationship** - Maps relationships between clients

## Sample Queries

The system supports various fraud detection queries:

1. **Spike Detection**: Identifies unusual increases in transaction frequency
2. **Carousel Detection**: Finds circular transaction patterns
3. **New Device Detection**: Flags transactions from newly seen devices
4. **Graph Analysis**: Analyzes connectivity clusters in the client network
5. **Risk Scoring**: Calculates fraud scores based on rules and weights

## Extending the System

To add new fraud detection rules:

1. Add a new entry to the `Rule` table
2. Update the `calculate_fraud_score` method in `fraud_detection.py`
3. Add new detection methods as needed

## Maintenance

1. Regularly update the risk scores for devices and IP addresses
2. Review and update fraud detection rules based on new patterns
3. Monitor the database performance and optimize queries as needed
4. Implement data retention policies for compliance

## Troubleshooting

1. **Connection Issues**: Verify database credentials and network connectivity
2. **Performance Issues**: Check database indexes and query execution plans
3. **Data Issues**: Validate data integrity and implement proper constraints

## Security Considerations

1. Use strong passwords for database users
2. Restrict database access to authorized systems only
3. Encrypt sensitive data at rest and in transit
4. Regularly update and patch the database software
5. Implement proper audit logging for all database operations