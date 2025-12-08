# Anti-fraud System for P2P Transfers

This project implements a database system for detecting fraudulent activities in peer-to-peer (P2P) money transfers.

## Overview

The system is designed to identify suspicious transactions based on behavioral and network characteristics. It tracks clients, their accounts/cards, transactions, devices, IP addresses, and relationships between clients to build a comprehensive picture for fraud detection.

## Database Schema

The database consists of the following main entities:

1. **Client** - Information about users
2. **Account/Card** - Financial accounts owned by clients
3. **Transaction** - Transfer records between accounts
4. **Device** - Information about devices used for transactions
5. **IPAddress** - Details about IP addresses involved in transactions
6. **Rule** - Fraud detection rules with weights
7. **Blacklist** - Entities blacklisted for various reasons
8. **ClientRelationship** - Relationships between clients

## Key Features

- Behavioral analysis of transaction patterns
- Network analysis based on devices and IP addresses
- Rule-based scoring system for fraud detection
- Relationship mapping between clients
- Blacklisting capabilities
- Real-time fraud detection queries

## Components

1. **Database** - PostgreSQL schema with all necessary tables and relationships
2. **Security Dashboard** - Web-based interface for fraud analysts
3. **Fraud Detection Scripts** - Python scripts for fraud analysis

## Files

- `schema.sql` - Complete database schema with tables, constraints, and sample data
- `database_design.md` - Detailed design document with entity descriptions and sample queries
- `security_dashboard/` - Web-based dashboard for security analysts
- `fraud_detection.py` - Python script demonstrating fraud detection algorithms

## Sample Queries

The system supports various types of fraud detection queries:

1. Spike detection in transaction frequency
2. Carousel transaction pattern detection
3. New device identification
4. Graph-based connectivity cluster analysis
5. Risk scoring based on rules and weights

## Implementation Notes

This database schema is designed for PostgreSQL. Some modifications may be needed for other database systems.