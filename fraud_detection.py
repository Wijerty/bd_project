#!/usr/bin/env python3
"""
Fraud Detection System for P2P Transfers

This script demonstrates how to interact with the anti-fraud database
to detect suspicious transactions.
"""

import psycopg2
from psycopg2 import sql
import datetime
from typing import List, Dict, Any

class FraudDetectionSystem:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the fraud detection system with database configuration.
        
        Args:
            db_config: Dictionary containing database connection parameters
        """
        self.db_config = db_config
        self.connection = None
    
    def connect(self):
        """Establish connection to the database."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            print("Successfully connected to the database")
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def detect_high_amount_transactions(self, threshold: float = 10000.0) -> List[Dict[str, Any]]:
        """
        Detect transactions with amounts exceeding the threshold.
        
        Args:
            threshold: Amount threshold for flagging transactions
            
        Returns:
            List of high-amount transactions
        """
        if not self.connection:
            print("Not connected to database")
            return []
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT t.transaction_id, t.amount, t.transaction_date, 
                       s.account_number as sender_account,
                       r.account_number as receiver_account
                FROM Transaction t
                JOIN Account s ON t.sender_account_id = s.account_id
                JOIN Account r ON t.receiver_account_id = r.account_id
                WHERE t.amount > %s
                ORDER BY t.amount DESC
            """
            cursor.execute(query, (threshold,))
            results = cursor.fetchall()
            
            transactions = []
            for row in results:
                transactions.append({
                    'transaction_id': row[0],
                    'amount': float(row[1]),
                    'transaction_date': row[2],
                    'sender_account': row[3],
                    'receiver_account': row[4]
                })
            
            return transactions
        except Exception as e:
            print(f"Error detecting high amount transactions: {e}")
            return []
    
    def detect_new_devices(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Detect transactions made with newly registered devices.
        
        Args:
            hours: Time window in hours to consider a device as "new"
            
        Returns:
            List of transactions with new devices
        """
        if not self.connection:
            print("Not connected to database")
            return []
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT t.transaction_id, t.transaction_date, d.device_fingerprint,
                       s.account_number as sender_account
                FROM Transaction t
                JOIN Device d ON t.device_id = d.device_id
                JOIN Account s ON t.sender_account_id = s.account_id
                WHERE d.first_seen_date >= NOW() - INTERVAL '%s hours'
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query, (hours,))
            results = cursor.fetchall()
            
            transactions = []
            for row in results:
                transactions.append({
                    'transaction_id': row[0],
                    'transaction_date': row[1],
                    'device_fingerprint': row[2],
                    'sender_account': row[3]
                })
            
            return transactions
        except Exception as e:
            print(f"Error detecting transactions with new devices: {e}")
            return []
    
    def detect_frequent_transactions(self, account_id: int, minutes: int = 60) -> int:
        """
        Count transactions for an account within a time window.
        
        Args:
            account_id: ID of the account to check
            minutes: Time window in minutes
            
        Returns:
            Number of transactions in the time window
        """
        if not self.connection:
            print("Not connected to database")
            return 0
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT COUNT(*) 
                FROM Transaction 
                WHERE sender_account_id = %s 
                AND transaction_date >= NOW() - INTERVAL '%s minutes'
            """
            cursor.execute(query, (account_id, minutes))
            result = cursor.fetchone()
            
            return result[0] if result else 0
        except Exception as e:
            print(f"Error counting frequent transactions: {e}")
            return 0
    
    def calculate_fraud_score(self, transaction_id: int) -> float:
        """
        Calculate fraud score for a transaction based on rules.
        
        Args:
            transaction_id: ID of the transaction to score
            
        Returns:
            Fraud score (higher means more suspicious)
        """
        if not self.connection:
            print("Not connected to database")
            return 0.0
        
        try:
            cursor = self.connection.cursor()
            
            # Get transaction details
            query = """
                SELECT t.amount, d.risk_score, i.risk_score
                FROM Transaction t
                LEFT JOIN Device d ON t.device_id = d.device_id
                LEFT JOIN IPAddress i ON t.ip_address_id = i.ip_address_id
                WHERE t.transaction_id = %s
            """
            cursor.execute(query, (transaction_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"Transaction {transaction_id} not found")
                return 0.0
            
            amount, device_risk, ip_risk = result
            
            # Simple scoring algorithm
            score = 0.0
            
            # High amount rule
            if amount and amount > 10000:
                score += 5.0
            
            # High-risk device rule
            if device_risk and device_risk > 0.8:
                score += 3.0
            
            # High-risk IP rule
            if ip_risk and ip_risk > 0.8:
                score += 4.0
            
            return score
        except Exception as e:
            print(f"Error calculating fraud score: {e}")
            return 0.0
    
    def flag_suspicious_transaction(self, transaction_id: int, reason: str):
        """
        Flag a transaction as suspicious in the database.
        
        Args:
            transaction_id: ID of the transaction to flag
            reason: Reason for flagging the transaction
        """
        if not self.connection:
            print("Not connected to database")
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE Transaction 
                SET is_flagged = TRUE, flagged_reason = %s 
                WHERE transaction_id = %s
            """
            cursor.execute(query, (reason, transaction_id))
            self.connection.commit()
            print(f"Transaction {transaction_id} flagged as suspicious: {reason}")
        except Exception as e:
            print(f"Error flagging transaction: {e}")
            self.connection.rollback()

def main():
    # Database configuration (update with your settings)
    db_config = {
        'host': 'localhost',
        'database': 'antifraud_p2p',
        'user': 'your_username',
        'password': 'your_password'
    }
    
    # Initialize fraud detection system
    fds = FraudDetectionSystem(db_config)
    
    try:
        # Connect to database
        fds.connect()
        
        # Example 1: Detect high amount transactions
        print("=== High Amount Transactions ===")
        high_amount_txs = fds.detect_high_amount_transactions(5000.0)
        for tx in high_amount_txs:
            print(f"Transaction {tx['transaction_id']}: {tx['amount']} "
                  f"from {tx['sender_account']} to {tx['receiver_account']}")
        
        # Example 2: Detect transactions with new devices
        print("\n=== Transactions with New Devices ===")
        new_device_txs = fds.detect_new_devices(48)  # Last 48 hours
        for tx in new_device_txs:
            print(f"Transaction {tx['transaction_id']} on {tx['transaction_date']} "
                  f"from device {tx['device_fingerprint'][:20]}...")
        
        # Example 3: Calculate fraud scores
        print("\n=== Fraud Scores ===")
        # Calculate score for transaction ID 1
        score = fds.calculate_fraud_score(1)
        print(f"Fraud score for transaction 1: {score}")
        
        # Flag transaction if score is high
        if score > 5.0:
            fds.flag_suspicious_transaction(1, f"High fraud score: {score}")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # Disconnect from database
        fds.disconnect()

if __name__ == "__main__":
    main()