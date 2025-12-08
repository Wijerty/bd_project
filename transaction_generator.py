import psycopg2
import psycopg2.extras
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionGenerator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.connect()
        
        # Load realistic data
        self.first_names = ['Иван', 'Мария', 'Алексей', 'Елена', 'Дмитрий', 'Анна', 'Сергей', 'Ольга', 'Павел', 'Наталья']
        self.last_names = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Попов', 'Лебедев', 'Козлов', 'Новиков', 'Морозов']
        self.cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Нижний Новгород', 'Казань', 'Челябинск', 'Омск', 'Самара', 'Ростов-на-Дону']
        self.device_types = ['mobile', 'desktop', 'tablet']
        self.os_types = {
            'mobile': ['Android', 'iOS'],
            'desktop': ['Windows', 'macOS', 'Linux'],
            'tablet': ['Android', 'iOS']
        }
        self.browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def generate_realistic_clients(self, count: int = 50) -> List[Dict]:
        """Generate realistic client data"""
        clients = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            # Generate realistic dates
            birth_year = random.randint(1970, 2000)
            birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
            
            # Generate registration date (last 2 years)
            reg_days = random.randint(1, 730)
            reg_date = datetime.now() - timedelta(days=reg_days)
            
            # Determine risk level based on various factors
            risk_level = self._calculate_client_risk(birth_date, reg_date)
            risk_category = self._get_risk_category(risk_level)
            
            client = {
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': birth_date,
                'phone_number': f'+7{random.randint(900, 999)}{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(10, 99)}',
                'email': f'{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{"gmail.com" if random.random() > 0.3 else "yandex.ru"}',
                'registration_date': reg_date,
                'kyc_status': random.choices(['verified', 'pending', 'none'], weights=[0.7, 0.2, 0.1])[0],
                'risk_level': risk_level,
                'risk_category': risk_category,
                'last_login_date': datetime.now() - timedelta(hours=random.randint(0, 48)),
                'login_count': random.randint(1, 100),
                'failed_login_attempts': random.randint(0, 5)
            }
            clients.append(client)
        
        return clients
    
    def generate_realistic_devices(self, count: int = 100) -> List[Dict]:
        """Generate realistic device data"""
        devices = []
        
        for i in range(count):
            device_type = random.choice(self.device_types)
            os = random.choice(self.os_types[device_type])
            browser = random.choice(self.browsers)
            
            # Generate device fingerprint
            fingerprint = f"fp_{random.randint(100000, 999999)}_{random.randint(1000, 9999)}"
            
            # Calculate device risk based on characteristics
            risk_score = self._calculate_device_risk(device_type, os, browser)
            
            device = {
                'device_fingerprint': fingerprint,
                'device_type': device_type,
                'os': os,
                'os_version': self._get_os_version(os),
                'browser': browser,
                'browser_version': f"{random.randint(80, 120)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}",
                'user_agent': self._generate_user_agent(device_type, os, browser),
                'screen_resolution': self._get_screen_resolution(device_type),
                'timezone': random.choice(['Europe/Moscow', 'Europe/Samara', 'Asia/Yekaterinburg']),
                'language': 'ru-RU',
                'risk_score': risk_score,
                'is_emulator': random.random() < 0.05,
                'is_rooted': random.random() < 0.1 if device_type == 'mobile' else False,
                'vpn_detected': random.random() < 0.15,
                'reputation_score': max(0.1, 1.0 - risk_score)
            }
            devices.append(device)
        
        return devices
    
    def generate_realistic_ips(self, count: int = 80) -> List[Dict]:
        """Generate realistic IP address data"""
        ips = []
        
        # Russian IP ranges (simplified)
        russian_ips = [
            ('87.240.0.0', 'Russia', 'VK', 'Moscow'),
            ('5.45.192.0', 'Russia', 'Yandex', 'Moscow'),
            ('178.154.0.0', 'Russia', 'MTS', 'Moscow'),
            ('217.66.0.0', 'Russia', 'Beeline', 'Moscow'),
            ('188.170.0.0', 'Russia', 'Megafon', 'Moscow'),
            ('95.173.0.0', 'Russia', 'Rostelecom', 'Saint Petersburg'),
            ('46.29.0.0', 'Russia', 'Beeline', 'Saint Petersburg'),
            ('185.5.0.0', 'Russia', 'MTS', 'Novosibirsk'),
        ]
        
        # Some suspicious IPs
        suspicious_ips = [
            ('185.220.101.182', 'Unknown', 'Tor Exit Node', 'Unknown'),
            ('198.98.51.0', 'Panama', 'VPN', 'Panama City'),
            ('107.172.0.0', 'USA', 'Datacenter', 'New York'),
            ('192.168.1.0', 'Russia', 'Local Network', 'Moscow'),
        ]
        
        for i in range(count):
            if random.random() < 0.1:  # 10% suspicious IPs
                ip_data = random.choice(suspicious_ips)
                base_ip = ip_data[0]
                is_proxy = ip_data[2] in ['Tor Exit Node', 'VPN']
                is_tor = ip_data[2] == 'Tor Exit Node'
                is_vpn = ip_data[2] == 'VPN'
                is_datacenter = ip_data[2] == 'Datacenter'
                threat_level = random.choice(['high', 'critical']) if is_tor else 'medium'
            else:
                ip_data = random.choice(russian_ips)
                base_ip = ip_data[0]
                is_proxy = False
                is_tor = False
                is_vpn = random.random() < 0.05
                is_datacenter = False
                threat_level = 'low'
            
            # Generate IP address
            ip_parts = base_ip.split('.')
            ip_parts[3] = str(random.randint(1, 254))
            ip_address = '.'.join(ip_parts)
            
            # Calculate risk score
            risk_score = self._calculate_ip_risk(is_proxy, is_tor, is_vpn, is_datacenter)
            
            ip = {
                'ip_address': ip_address,
                'country': ip_data[1],
                'country_code': 'RU' if ip_data[1] == 'Russia' else 'XX',
                'city': ip_data[3],
                'region': ip_data[3],
                'latitude': self._get_latitude(ip_data[3]),
                'longitude': self._get_longitude(ip_data[3]),
                'isp': ip_data[2],
                'organization': ip_data[2],
                'asn': f"AS{random.randint(1000, 99999)}",
                'risk_score': risk_score,
                'is_proxy': is_proxy,
                'is_tor': is_tor,
                'is_vpn': is_vpn,
                'is_datacenter': is_datacenter,
                'is_mobile': random.random() < 0.3,
                'threat_level': threat_level,
                'reputation_score': max(0.1, 1.0 - risk_score)
            }
            ips.append(ip)
        
        return ips
    
    def generate_accounts_for_clients(self, clients: List[Dict]) -> List[Dict]:
        """Generate accounts for clients"""
        accounts = []
        
        for i, client in enumerate(clients):
            # Generate 1-3 accounts per client
            num_accounts = random.randint(1, 3)
            
            for j in range(num_accounts):
                account_type = random.choice(['card', 'bank_account', 'digital_wallet'])
                
                if account_type == 'card':
                    account_number = f"4276{random.randint(100000000000, 999999999999)}"
                    card_expiry = datetime.now() + timedelta(days=random.randint(30, 1825))
                    card_type = random.choice(['Visa', 'Mastercard', 'Mir'])
                    bank_name = random.choice(['Сбер', 'Тинькофф', 'Альфа', 'ВТБ'])
                elif account_type == 'bank_account':
                    account_number = f"408178{random.randint(1000000000, 9999999999)}"
                    card_expiry = None
                    card_type = None
                    bank_name = random.choice(['Сбер', 'Тинькофф', 'Альфа', 'ВТБ'])
                else:  # digital_wallet
                    account_number = f"WALLET{random.randint(100000000, 999999999)}"
                    card_expiry = None
                    card_type = None
                    bank_name = random.choice(['QIWI', 'ЮMoney', 'WebMoney'])
                
                account = {
                    'temp_client_id': i,  # Temporary ID to match with client after insertion
                    'client_id': None,  # Will be set after client insertion
                    'account_number': account_number,
                    'account_type': account_type,
                    'currency': 'RUB',
                    'balance': random.uniform(1000, 500000),
                    'card_expiry_date': card_expiry,
                    'card_type': card_type,
                    'bank_name': bank_name,
                    'is_verified': random.random() > 0.2,
                    'daily_limit': random.choice([50000, 100000, 200000]),
                    'monthly_limit': random.choice([500000, 1000000, 2000000])
                }
                accounts.append(account)
        
        return accounts
    
    def generate_normal_transactions(self, accounts: List[Dict], devices: List[Dict], ips: List[Dict], count: int = 1000) -> List[Dict]:
        """Generate normal P2P transactions"""
        transactions = []
        
        for i in range(count):
            # Select sender and receiver
            sender = random.choice(accounts)
            receiver = random.choice([a for a in accounts if a['account_id'] != sender['account_id']])
            
            # Generate amount (realistic distribution)
            amount = self._generate_realistic_amount()
            
            # Generate transaction date (last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            transaction_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Select device and IP
            device = random.choice(devices)
            ip = random.choice(ips)
            
            # Calculate fraud score (low for normal transactions)
            fraud_score = random.uniform(0.0, 0.3)
            
            transaction = {
                'sender_account_id': sender['account_id'],
                'receiver_account_id': receiver['account_id'],
                'amount': amount,
                'currency': 'RUB',
                'transaction_date': transaction_date,
                'transaction_type': 'P2P',
                'status': random.choices(['completed', 'pending', 'failed'], weights=[0.95, 0.04, 0.01])[0],
                'ip_address_id': ip['ip_address_id'],
                'device_id': device['device_id'],
                'location_city': ip.get('city', 'Unknown'),
                'location_country': ip.get('country', 'Unknown'),
                'description': random.choice(['Перевод другу', 'Оплата услуг', 'Возврат долга', 'Подарок']),
                'fraud_score': fraud_score,
                'is_flagged': fraud_score > 0.8,
                'is_suspicious': fraud_score > 0.6,
                'processing_time_ms': random.randint(100, 2000),
                'velocity_score': random.uniform(0.0, 0.2),
                'anomaly_score': random.uniform(0.0, 0.1),
                'chargeback_risk': random.uniform(0.0, 0.1)
            }
            transactions.append(transaction)
        
        return transactions
    
    def generate_fraudulent_transactions(self, accounts: List[Dict], devices: List[Dict], ips: List[Dict]) -> List[Dict]:
        """Generate fraudulent transactions for testing"""
        transactions = []
        
        # Carousel pattern
        if len(accounts) >= 3:
            carousel_accounts = random.sample(accounts, 3)
            base_time = datetime.now() - timedelta(hours=2)
            
            for i in range(3):
                sender = carousel_accounts[i]
                receiver = carousel_accounts[(i + 1) % 3]
                
                transaction = {
                    'sender_account_id': sender['account_id'],
                    'receiver_account_id': receiver['account_id'],
                    'amount': random.uniform(10000, 50000),
                    'currency': 'RUB',
                    'transaction_date': base_time + timedelta(minutes=i*10),
                    'transaction_type': 'P2P',
                    'status': 'completed',
                    'ip_address_id': random.choice(ips)['ip_address_id'],
                    'device_id': random.choice(devices)['device_id'],
                    'location_city': random.choice(ips).get('city', 'Unknown'),
                    'location_country': random.choice(ips).get('country', 'Unknown'),
                    'description': 'Перевод',
                    'fraud_score': 0.85,
                    'is_flagged': True,
                    'is_suspicious': True,
                    'processing_time_ms': random.randint(500, 1500),
                    'velocity_score': 0.9,
                    'anomaly_score': 0.8,
                    'chargeback_risk': 0.7
                }
                transactions.append(transaction)
        
        # High velocity burst
        if len(accounts) >= 1:
            burst_account = random.choice(accounts)
            base_time = datetime.now() - timedelta(minutes=30)
            
            for i in range(8):
                receiver = random.choice([a for a in accounts if a['account_id'] != burst_account['account_id']])
                
                transaction = {
                    'sender_account_id': burst_account['account_id'],
                    'receiver_account_id': receiver['account_id'],
                    'amount': random.uniform(5000, 15000),
                    'currency': 'RUB',
                    'transaction_date': base_time + timedelta(minutes=i*2),
                    'transaction_type': 'P2P',
                    'status': 'completed',
                    'ip_address_id': random.choice(ips)['ip_address_id'],
                    'device_id': random.choice(devices)['device_id'],
                    'location_city': random.choice(ips).get('city', 'Unknown'),
                    'location_country': random.choice(ips).get('country', 'Unknown'),
                    'description': 'Срочный перевод',
                    'fraud_score': 0.75,
                    'is_flagged': True,
                    'is_suspicious': True,
                    'processing_time_ms': random.randint(200, 800),
                    'velocity_score': 0.95,
                    'anomaly_score': 0.7,
                    'chargeback_risk': 0.5
                }
                transactions.append(transaction)
        
        # Suspicious IP transactions
        suspicious_ips = [ip for ip in ips if ip['threat_level'] in ['high', 'critical']]
        if suspicious_ips and accounts:
            for ip in suspicious_ips[:2]:
                sender = random.choice(accounts)
                receiver = random.choice([a for a in accounts if a['account_id'] != sender['account_id']])
                
                transaction = {
                    'sender_account_id': sender['account_id'],
                    'receiver_account_id': receiver['account_id'],
                    'amount': random.uniform(20000, 80000),
                    'currency': 'RUB',
                    'transaction_date': datetime.now() - timedelta(hours=random.randint(1, 12)),
                    'transaction_type': 'P2P',
                    'status': 'completed',
                    'ip_address_id': ip['ip_address_id'],
                    'device_id': random.choice(devices)['device_id'],
                    'location_city': ip.get('city', 'Unknown'),
                    'location_country': ip.get('country', 'Unknown'),
                    'description': 'Перевод',
                    'fraud_score': 0.9,
                    'is_flagged': True,
                    'is_suspicious': True,
                    'processing_time_ms': random.randint(1000, 3000),
                    'velocity_score': 0.6,
                    'anomaly_score': 0.85,
                    'chargeback_risk': 0.8
                }
                transactions.append(transaction)
        
        return transactions
    
    
    def generate_all_data(self, num_clients: int = 50, num_normal_transactions: int = 1000) -> None:
        """Generate and insert all test data"""
        logger.info("Starting data generation...")
        
        # Generate all data
        clients = self.generate_realistic_clients(num_clients)
        devices = self.generate_realistic_devices(100)
        ips = self.generate_realistic_ips(80)
        accounts = self.generate_accounts_for_clients(clients)
        
        # Insert clients, devices, IPs, and accounts first to get IDs
        try:
            with self.conn.cursor() as cursor:
                # Insert clients
                for i, client in enumerate(clients):
                    cursor.execute("""
                        INSERT INTO client (first_name, last_name, date_of_birth, phone_number, email,
                                         registration_date, kyc_status, risk_level, risk_category,
                                         last_login_date, login_count, failed_login_attempts)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING client_id
                    """, (
                        client['first_name'], client['last_name'], client['date_of_birth'],
                        client['phone_number'], client['email'], client['registration_date'],
                        client['kyc_status'], client['risk_level'], client['risk_category'],
                        client['last_login_date'], client['login_count'], client['failed_login_attempts']
                    ))
                    client['client_id'] = cursor.fetchone()[0]
                    client['temp_client_id'] = i
                
                # Insert devices
                for device in devices:
                    cursor.execute("""
                        INSERT INTO device (device_fingerprint, device_type, os, os_version, browser,
                                          browser_version, user_agent, screen_resolution, timezone, language,
                                          risk_score, is_emulator, is_rooted, vpn_detected, reputation_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING device_id
                    """, (
                        device['device_fingerprint'], device['device_type'], device['os'], device['os_version'],
                        device['browser'], device['browser_version'], device['user_agent'], device['screen_resolution'],
                        device['timezone'], device['language'], device['risk_score'], device['is_emulator'],
                        device['is_rooted'], device['vpn_detected'], device['reputation_score']
                    ))
                    device['device_id'] = cursor.fetchone()[0]
                
                # Insert IP addresses
                for ip in ips:
                    cursor.execute("""
                        INSERT INTO ipaddress (ip_address, country, country_code, city, region, latitude, longitude,
                                             isp, organization, asn, risk_score, is_proxy, is_tor, is_vpn, is_datacenter,
                                             is_mobile, threat_level, reputation_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING ip_address_id
                    """, (
                        ip['ip_address'], ip['country'], ip['country_code'], ip['city'], ip['region'],
                        ip['latitude'], ip['longitude'], ip['isp'], ip['organization'], ip['asn'],
                        ip['risk_score'], ip['is_proxy'], ip['is_tor'], ip['is_vpn'], ip['is_datacenter'],
                        ip['is_mobile'], ip['threat_level'], ip['reputation_score']
                    ))
                    ip['ip_address_id'] = cursor.fetchone()[0]
                
                # Update account client_ids and insert accounts
                account_index = 0
                for client in clients:
                    # Get number of accounts for this client
                    client_accounts = [acc for acc in accounts if acc.get('temp_client_id') == client['temp_client_id']]
                    
                    for account in client_accounts:
                        account['client_id'] = client['client_id']
                        cursor.execute("""
                            INSERT INTO account (client_id, account_number, account_type, currency, balance,
                                               card_expiry_date, card_type, bank_name, is_verified, daily_limit, monthly_limit)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING account_id
                        """, (
                            account['client_id'], account['account_number'], account['account_type'],
                            account['currency'], account['balance'], account['card_expiry_date'],
                            account['card_type'], account['bank_name'], account['is_verified'],
                            account['daily_limit'], account['monthly_limit']
                        ))
                        account['account_id'] = cursor.fetchone()[0]
                
                self.conn.commit()
                logger.info(f"Inserted {len(clients)} clients, {len(devices)} devices, {len(ips)} IPs, {len(accounts)} accounts")
        
        except Exception as e:
            logger.error(f"Error inserting base data: {e}")
            self.conn.rollback()
            raise
        
        # Now generate transactions with proper IDs
        normal_transactions = self.generate_normal_transactions(accounts, devices, ips, num_normal_transactions)
        fraudulent_transactions = self.generate_fraudulent_transactions(accounts, devices, ips)
        
        all_transactions = normal_transactions + fraudulent_transactions
        
        # Shuffle transactions for realistic order
        random.shuffle(all_transactions)
        
        # Insert transactions
        try:
            with self.conn.cursor() as cursor:
                for transaction in all_transactions:
                    cursor.execute("""
                        INSERT INTO transaction (sender_account_id, receiver_account_id, amount, currency,
                                              transaction_date, transaction_type, status, ip_address_id, device_id,
                                              location_city, location_country, description, fraud_score, is_flagged,
                                              is_suspicious, processing_time_ms, velocity_score, anomaly_score, chargeback_risk)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        transaction['sender_account_id'], transaction['receiver_account_id'], transaction['amount'],
                        transaction['currency'], transaction['transaction_date'], transaction['transaction_type'],
                        transaction['status'], transaction['ip_address_id'], transaction['device_id'],
                        transaction['location_city'], transaction['location_country'], transaction['description'],
                        transaction['fraud_score'], transaction['is_flagged'], transaction['is_suspicious'],
                        transaction['processing_time_ms'], transaction['velocity_score'], transaction['anomaly_score'],
                        transaction['chargeback_risk']
                    ))
                
                self.conn.commit()
                logger.info(f"Inserted {len(all_transactions)} transactions")
                
        except Exception as e:
            logger.error(f"Error inserting transactions: {e}")
            self.conn.rollback()
            raise
        
        logger.info("Data generation completed successfully!")
    
    # Helper methods
    def _calculate_client_risk(self, birth_date, reg_date) -> float:
        """Calculate client risk score"""
        risk = 0.1
        
        # Younger clients have slightly higher risk
        age = (datetime.now() - birth_date).days / 365.25
        if age < 25:
            risk += 0.1
        
        # Recently registered clients have higher risk
        days_since_reg = (datetime.now() - reg_date).days
        if days_since_reg < 30:
            risk += 0.2
        elif days_since_reg < 90:
            risk += 0.1
        
        return min(risk, 0.9)
    
    def _get_risk_category(self, risk_level: float) -> str:
        """Get risk category based on risk level"""
        if risk_level >= 0.7:
            return 'high'
        elif risk_level >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_device_risk(self, device_type: str, os: str, browser: str) -> float:
        """Calculate device risk score"""
        risk = 0.1
        
        # Mobile devices slightly higher risk
        if device_type == 'mobile':
            risk += 0.05
        
        # Less common browsers higher risk
        if browser not in ['Chrome', 'Safari']:
            risk += 0.1
        
        return min(risk, 0.8)
    
    def _calculate_ip_risk(self, is_proxy: bool, is_tor: bool, is_vpn: bool, is_datacenter: bool) -> float:
        """Calculate IP risk score"""
        risk = 0.1
        
        if is_tor:
            risk += 0.8
        if is_proxy:
            risk += 0.4
        if is_vpn:
            risk += 0.2
        if is_datacenter:
            risk += 0.3
        
        return min(risk, 0.95)
    
    def _get_os_version(self, os: str) -> str:
        """Get realistic OS version"""
        versions = {
            'Android': ['10', '11', '12', '13'],
            'iOS': ['14.6', '15.0', '16.0', '17.0'],
            'Windows': ['10', '11'],
            'macOS': ['12.0', '13.0', '14.0'],
            'Linux': ['20.04', '22.04', '23.04']
        }
        return random.choice(versions.get(os, ['Unknown']))
    
    def _generate_user_agent(self, device_type: str, os: str, browser: str) -> str:
        """Generate realistic user agent string"""
        if device_type == 'mobile':
            if os == 'Android':
                return f"Mozilla/5.0 (Linux; Android {random.choice(['10', '11', '12'])}) Chrome/{random.randint(90, 120)}.0 Mobile Safari/537.36"
            else:  # iOS
                return f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.choice(['15_6', '16_0'])} like Mac OS X) Safari/605.1.15"
        else:
            if os == 'Windows':
                return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {browser}/{random.randint(90, 120)}.0"
            else:
                return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) {browser}/{random.randint(90, 120)}.0"
    
    def _get_screen_resolution(self, device_type: str) -> str:
        """Get realistic screen resolution"""
        resolutions = {
            'mobile': ['375x667', '375x812', '414x896', '360x640'],
            'desktop': ['1920x1080', '1366x768', '1440x900', '2560x1440'],
            'tablet': ['768x1024', '820x1180', '1024x768']
        }
        return random.choice(resolutions.get(device_type, ['1920x1080']))
    
    def _get_latitude(self, city: str) -> float:
        """Get latitude for city"""
        latitudes = {
            'Moscow': 55.7558,
            'Saint Petersburg': 59.9343,
            'Novosibirsk': 55.0084,
            'Unknown': 0.0
        }
        return latitudes.get(city, 55.7558)
    
    def _get_longitude(self, city: str) -> float:
        """Get longitude for city"""
        longitudes = {
            'Moscow': 37.6173,
            'Saint Petersburg': 30.3351,
            'Novosibirsk': 82.9357,
            'Unknown': 0.0
        }
        return longitudes.get(city, 37.6173)
    
    def _generate_realistic_amount(self) -> float:
        """Generate realistic transaction amount"""
        # Most transactions are small amounts
        if random.random() < 0.7:
            return round(random.uniform(500, 10000), 2)
        elif random.random() < 0.9:
            return round(random.uniform(10000, 50000), 2)
        else:
            return round(random.uniform(50000, 200000), 2)

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'antifraud_p2p',
        'user': 'antifraud_user',
        'password': 'antifraud_pass',
        'port': 5432
    }
    
    # Generate test data
    generator = TransactionGenerator(db_config)
    generator.generate_all_data(num_clients=30, num_normal_transactions=500)
    
    print("Test data generation completed!")
    print("Run advanced_fraud_detection.py to test fraud detection algorithms.")