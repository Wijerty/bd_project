from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'antifraud_p2p'),
    'user': os.environ.get('DB_USER', 'antifraud_user'),
    'password': os.environ.get('DB_PASSWORD', 'antifraud_pass'),
    'port': os.environ.get('DB_PORT', '5432')
}

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/transactions')
def get_transactions():
    """Get recent transactions with fraud scores."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get flagged transactions
        query = """
            SELECT t.transaction_id, t.amount, t.currency, t.transaction_date,
                   t.status, t.is_flagged, t.fraud_score, t.flagged_reason,
                   s.account_number as sender_account,
                   r.account_number as receiver_account,
                   c1.first_name as sender_first_name,
                   c1.last_name as sender_last_name,
                   c2.first_name as receiver_first_name,
                   c2.last_name as receiver_last_name
            FROM Transaction t
            JOIN Account s ON t.sender_account_id = s.account_id
            JOIN Account r ON t.receiver_account_id = r.account_id
            JOIN Client c1 ON s.client_id = c1.client_id
            JOIN Client c2 ON r.client_id = c2.client_id
            ORDER BY t.transaction_date DESC
            LIMIT 50
        """
        cursor.execute(query)
        transactions = cursor.fetchall()
        
        conn.close()
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flagged-transactions')
def get_flagged_transactions():
    """Get transactions flagged as suspicious."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT t.transaction_id, t.amount, t.currency, t.transaction_date,
                   t.status, t.fraud_score, t.flagged_reason,
                   s.account_number as sender_account,
                   r.account_number as receiver_account,
                   c1.first_name as sender_first_name,
                   c1.last_name as sender_last_name,
                   c2.first_name as receiver_first_name,
                   c2.last_name as receiver_last_name
            FROM Transaction t
            JOIN Account s ON t.sender_account_id = s.account_id
            JOIN Account r ON t.receiver_account_id = r.account_id
            JOIN Client c1 ON s.client_id = c1.client_id
            JOIN Client c2 ON r.client_id = c2.client_id
            WHERE t.is_flagged = TRUE
            ORDER BY t.fraud_score DESC, t.transaction_date DESC
            LIMIT 50
        """
        cursor.execute(query)
        transactions = cursor.fetchall()
        
        conn.close()
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/high-risk-clients')
def get_high_risk_clients():
    """Get clients with high risk levels."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT client_id, first_name, last_name, phone_number, email, 
                   risk_level, is_blocked
            FROM Client
            WHERE risk_level > 0.5 OR is_blocked = TRUE
            ORDER BY risk_level DESC
            LIMIT 50
        """
        cursor.execute(query)
        clients = cursor.fetchall()
        
        conn.close()
        return jsonify({'clients': clients})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transaction-patterns')
def get_transaction_patterns():
    """Get transaction patterns for spike detection."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get transaction counts by hour for the last 24 hours
        query = """
            SELECT 
                DATE_TRUNC('hour', transaction_date) as hour,
                COUNT(*) as transaction_count
            FROM Transaction
            WHERE transaction_date >= NOW() - INTERVAL '24 hours'
            GROUP BY DATE_TRUNC('hour', transaction_date)
            ORDER BY hour
        """
        cursor.execute(query)
        patterns = cursor.fetchall()
        
        conn.close()
        return jsonify({'patterns': patterns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/client/<int:client_id>')
def get_client_details(client_id):
    """Get detailed information about a specific client."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get client details
        client_query = """
            SELECT client_id, first_name, last_name, date_of_birth, 
                   phone_number, email, registration_date, kyc_status, 
                   risk_level, is_blocked
            FROM Client
            WHERE client_id = %s
        """
        cursor.execute(client_query, (client_id,))
        client = cursor.fetchone()
        
        if not client:
            conn.close()
            return jsonify({'error': 'Client not found'}), 404
        
        # Get client accounts
        accounts_query = """
            SELECT account_id, account_number, account_type, balance, 
                   opening_date, is_active
            FROM Account
            WHERE client_id = %s
        """
        cursor.execute(accounts_query, (client_id,))
        accounts = cursor.fetchall()
        
        # Get recent transactions for this client (as sender)
        transactions_query = """
            SELECT t.transaction_id, t.amount, t.currency, t.transaction_date,
                   t.status, t.fraud_score, t.is_flagged,
                   r.account_number as receiver_account,
                   c.first_name as receiver_first_name,
                   c.last_name as receiver_last_name
            FROM Transaction t
            JOIN Account r ON t.receiver_account_id = r.account_id
            JOIN Client c ON r.client_id = c.client_id
            WHERE t.sender_account_id IN (
                SELECT account_id FROM Account WHERE client_id = %s
            )
            ORDER BY t.transaction_date DESC
            LIMIT 20
        """
        cursor.execute(transactions_query, (client_id,))
        transactions = cursor.fetchall()
        
        conn.close()
        return jsonify({
            'client': client,
            'accounts': accounts,
            'transactions': transactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transaction/<int:transaction_id>')
def get_transaction_details(transaction_id):
    """Get detailed information about a specific transaction."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT t.transaction_id, t.amount, t.currency, t.transaction_date,
                   t.transaction_type, t.status, t.location_coordinates,
                   t.description, t.fraud_score, t.is_flagged, t.flagged_reason,
                   s.account_number as sender_account,
                   r.account_number as receiver_account,
                   c1.first_name as sender_first_name,
                   c1.last_name as sender_last_name,
                   c1.phone_number as sender_phone,
                   c2.first_name as receiver_first_name,
                   c2.last_name as receiver_last_name,
                   c2.phone_number as receiver_phone,
                   d.device_fingerprint, d.device_type, d.os, d.browser,
                   i.ip_address, i.country, i.city
            FROM Transaction t
            JOIN Account s ON t.sender_account_id = s.account_id
            JOIN Account r ON t.receiver_account_id = r.account_id
            JOIN Client c1 ON s.client_id = c1.client_id
            JOIN Client c2 ON r.client_id = c2.client_id
            LEFT JOIN Device d ON t.device_id = d.device_id
            LEFT JOIN IPAddress i ON t.ip_address_id = i.ip_address_id
            WHERE t.transaction_id = %s
        """
        cursor.execute(query, (transaction_id,))
        transaction = cursor.fetchone()
        
        if not transaction:
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404
        
        conn.close()
        return jsonify({'transaction': transaction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flag-transaction', methods=['POST'])
def flag_transaction():
    """Flag a transaction as suspicious."""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        reason = data.get('reason')
        
        if not transaction_id or not reason:
            return jsonify({'error': 'Missing transaction_id or reason'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        query = """
            UPDATE Transaction 
            SET is_flagged = TRUE, flagged_reason = %s 
            WHERE transaction_id = %s
        """
        cursor.execute(query, (reason, transaction_id))
        conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Transaction flagged successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/block-client', methods=['POST'])
def block_client():
    """Block a client."""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        reason = data.get('reason')
        
        if not client_id:
            return jsonify({'error': 'Missing client_id'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        query = """
            UPDATE Client 
            SET is_blocked = TRUE 
            WHERE client_id = %s
        """
        cursor.execute(query, (client_id,))
        conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Client blocked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/accounts')
def get_accounts():
    """Get all active accounts for transaction creation."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT a.account_id, a.account_number, a.account_type, a.balance, a.currency,
                   c.client_id, c.first_name, c.last_name, c.risk_level, c.is_blocked
            FROM Account a
            JOIN Client c ON a.client_id = c.client_id
            WHERE a.is_active = TRUE
            ORDER BY c.last_name, c.first_name
        """
        cursor.execute(query)
        accounts = cursor.fetchall()
        
        conn.close()
        return jsonify({'accounts': accounts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create-transaction', methods=['POST'])
def create_transaction():
    """Create a new transaction with fraud check."""
    try:
        data = request.get_json()
        sender_account_id = data.get('sender_account_id')
        receiver_account_id = data.get('receiver_account_id')
        amount = data.get('amount')
        description = data.get('description', '')
        
        # Validation
        if not all([sender_account_id, receiver_account_id, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if sender_account_id == receiver_account_id:
            return jsonify({'error': 'Sender and receiver cannot be the same'}), 400
        
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check sender account and get client info
        cursor.execute("""
            SELECT a.account_id, a.balance, a.is_active,
                   c.client_id, c.first_name, c.last_name, c.risk_level, c.is_blocked
            FROM Account a
            JOIN Client c ON a.client_id = c.client_id
            WHERE a.account_id = %s
        """, (sender_account_id,))
        sender = cursor.fetchone()
        
        if not sender:
            conn.close()
            return jsonify({'error': 'Sender account not found'}), 404
        
        if sender['is_blocked']:
            conn.close()
            return jsonify({
                'error': 'Transaction blocked',
                'reason': 'Sender client is blocked',
                'fraud_check': {
                    'passed': False,
                    'score': 1.0,
                    'flags': ['BLOCKED_CLIENT']
                }
            }), 403
        
        if not sender['is_active']:
            conn.close()
            return jsonify({'error': 'Sender account is not active'}), 400
        
        if sender['balance'] < amount:
            conn.close()
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Check receiver account
        cursor.execute("""
            SELECT a.account_id, a.is_active,
                   c.client_id, c.first_name, c.last_name, c.risk_level, c.is_blocked
            FROM Account a
            JOIN Client c ON a.client_id = c.client_id
            WHERE a.account_id = %s
        """, (receiver_account_id,))
        receiver = cursor.fetchone()
        
        if not receiver:
            conn.close()
            return jsonify({'error': 'Receiver account not found'}), 404
        
        # Perform fraud check
        fraud_result = check_fraud(cursor, sender, receiver, amount)
        
        # Determine transaction status based on fraud check
        if fraud_result['score'] >= 0.8:
            status = 'blocked'
        elif fraud_result['score'] >= 0.5:
            status = 'review'
        else:
            status = 'completed'
        
        # Create the transaction
        cursor.execute("""
            INSERT INTO Transaction 
            (sender_account_id, receiver_account_id, amount, currency, 
             transaction_type, status, description, fraud_score, is_flagged, flagged_reason)
            VALUES (%s, %s, %s, 'RUB', 'transfer', %s, %s, %s, %s, %s)
            RETURNING transaction_id, transaction_date
        """, (
            sender_account_id,
            receiver_account_id,
            amount,
            status,
            description,
            fraud_result['score'],
            fraud_result['is_flagged'],
            fraud_result['reason'] if fraud_result['is_flagged'] else None
        ))
        
        new_transaction = cursor.fetchone()
        
        # Update balances if transaction is completed
        if status == 'completed':
            cursor.execute("""
                UPDATE Account SET balance = balance - %s WHERE account_id = %s
            """, (amount, sender_account_id))
            cursor.execute("""
                UPDATE Account SET balance = balance + %s WHERE account_id = %s
            """, (amount, receiver_account_id))
        
        # Create alert if flagged
        if fraud_result['is_flagged']:
            severity = 'critical' if fraud_result['score'] >= 0.8 else 'high' if fraud_result['score'] >= 0.6 else 'medium'
            cursor.execute("""
                INSERT INTO Alert (transaction_id, client_id, alert_type, severity, status, notes)
                VALUES (%s, %s, %s, %s, 'open', %s)
            """, (
                new_transaction['transaction_id'],
                sender['client_id'],
                fraud_result['flags'][0] if fraud_result['flags'] else 'suspicious',
                severity,
                fraud_result['reason']
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'transaction_id': new_transaction['transaction_id'],
            'transaction_date': new_transaction['transaction_date'].isoformat(),
            'status': status,
            'fraud_check': fraud_result,
            'message': get_status_message(status, fraud_result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def check_fraud(cursor, sender, receiver, amount):
    """Check transaction for fraud indicators."""
    flags = []
    score = 0.0
    reasons = []
    
    # Rule 1: Large amount (> 100,000)
    if amount > 100000:
        flags.append('HIGH_AMOUNT')
        score += 0.3
        reasons.append(f'Большая сумма перевода: {amount:,.2f} ₽')
    elif amount > 50000:
        flags.append('MEDIUM_AMOUNT')
        score += 0.15
        reasons.append(f'Повышенная сумма перевода: {amount:,.2f} ₽')
    
    # Rule 2: Sender risk level
    sender_risk = float(sender['risk_level']) if sender['risk_level'] else 0
    if sender_risk > 0.5:
        flags.append('HIGH_RISK_SENDER')
        score += sender_risk * 0.4
        reasons.append(f'Высокий риск отправителя: {sender_risk:.2f}')
    
    # Rule 3: Receiver risk level
    receiver_risk = float(receiver['risk_level']) if receiver['risk_level'] else 0
    if receiver_risk > 0.5:
        flags.append('HIGH_RISK_RECEIVER')
        score += receiver_risk * 0.3
        reasons.append(f'Высокий риск получателя: {receiver_risk:.2f}')
    
    # Rule 4: Receiver is blocked
    if receiver['is_blocked']:
        flags.append('BLOCKED_RECEIVER')
        score += 0.5
        reasons.append('Получатель заблокирован')
    
    # Rule 5: Round amount (suspicious pattern)
    if amount >= 10000 and amount % 10000 == 0:
        flags.append('ROUND_AMOUNT')
        score += 0.1
        reasons.append('Подозрительно круглая сумма')
    
    # Rule 6: Check for velocity (multiple transactions in short time)
    cursor.execute("""
        SELECT COUNT(*) as tx_count
        FROM Transaction
        WHERE sender_account_id = %s
        AND transaction_date >= NOW() - INTERVAL '1 hour'
    """, (sender['account_id'],))
    velocity = cursor.fetchone()
    if velocity and velocity['tx_count'] >= 5:
        flags.append('HIGH_VELOCITY')
        score += 0.25
        reasons.append(f'Много транзакций за час: {velocity["tx_count"]}')
    
    # Rule 7: Night time transaction (00:00 - 06:00)
    from datetime import datetime
    current_hour = datetime.now().hour
    if 0 <= current_hour < 6:
        flags.append('NIGHT_TRANSACTION')
        score += 0.15
        reasons.append('Транзакция в ночное время')
    
    # Cap score at 1.0
    score = min(score, 1.0)
    
    return {
        'score': round(score, 2),
        'is_flagged': score >= 0.4 or len(flags) >= 2,
        'flags': flags,
        'reason': '; '.join(reasons) if reasons else None
    }


def get_status_message(status, fraud_result):
    """Get user-friendly status message."""
    if status == 'completed':
        if fraud_result['is_flagged']:
            return 'Транзакция выполнена, но помечена для проверки'
        return 'Транзакция успешно выполнена'
    elif status == 'review':
        return 'Транзакция отправлена на проверку службой безопасности'
    elif status == 'blocked':
        return 'Транзакция заблокирована системой антифрода'
    return 'Неизвестный статус'


@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total transactions
        cursor.execute("SELECT COUNT(*) as total FROM Transaction")
        total_transactions = cursor.fetchone()['total']
        
        # Today's transactions
        cursor.execute("""
            SELECT COUNT(*) as today 
            FROM Transaction 
            WHERE DATE(transaction_date) = CURRENT_DATE
        """)
        today_transactions = cursor.fetchone()['today']
        
        # Flagged transactions
        cursor.execute("SELECT COUNT(*) as flagged FROM Transaction WHERE is_flagged = TRUE")
        flagged_transactions = cursor.fetchone()['flagged']
        
        # High risk clients
        cursor.execute("SELECT COUNT(*) as high_risk FROM Client WHERE risk_level > 0.5")
        high_risk_clients = cursor.fetchone()['high_risk']
        
        # Blocked clients
        cursor.execute("SELECT COUNT(*) as blocked FROM Client WHERE is_blocked = TRUE")
        blocked_clients = cursor.fetchone()['blocked']
        
        conn.close()
        
        return jsonify({
            'total_transactions': total_transactions,
            'today_transactions': today_transactions,
            'flagged_transactions': flagged_transactions,
            'high_risk_clients': high_risk_clients,
            'blocked_clients': blocked_clients
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)