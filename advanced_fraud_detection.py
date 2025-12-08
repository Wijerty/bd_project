import psycopg2
import psycopg2.extras
import random
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
import networkx as nx
from typing import List, Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFraudDetection:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.connect()
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def detect_carousel_patterns(self, time_window_hours=24) -> List[Dict]:
        """
        Detect carousel patterns - circular transactions between multiple accounts
        designed to obscure money trail
        """
        query = """
        WITH RECURSIVE transaction_paths AS (
            SELECT 
                t.sender_account_id,
                t.receiver_account_id,
                t.amount,
                t.transaction_date,
                ARRAY[t.transaction_id] as transaction_ids,
                ARRAY[t.sender_account_id, t.receiver_account_id] as account_path,
                1 as path_length
            FROM transaction t
            WHERE t.transaction_date >= NOW() - INTERVAL '%s hours'
            
            UNION ALL
            
            SELECT 
                tp.sender_account_id,
                t.receiver_account_id,
                tp.amount + t.amount as total_amount,
                GREATEST(tp.transaction_date, t.transaction_date) as latest_date,
                tp.transaction_ids || t.transaction_id,
                tp.account_path || t.receiver_account_id,
                tp.path_length + 1
            FROM transaction_paths tp
            JOIN transaction t ON tp.receiver_account_id = t.sender_account_id
            WHERE t.transaction_date >= NOW() - INTERVAL '%s hours'
            AND tp.path_length < 6
            AND t.receiver_account_id != ALL(tp.account_path[1:-1])
        )
        SELECT 
            account_path,
            transaction_ids,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count,
            MAX(transaction_date) as latest_date,
            path_length
        FROM transaction_paths
        WHERE account_path[1] = account_path[array_length(account_path, 1)]
        AND path_length >= 3
        GROUP BY account_path, transaction_ids, path_length
        HAVING COUNT(*) >= 3
        ORDER BY total_amount DESC, path_length DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (time_window_hours, time_window_hours))
                patterns = cursor.fetchall()
                
                results = []
                for pattern in patterns:
                    results.append({
                        'pattern_type': 'carousel',
                        'account_path': pattern['account_path'],
                        'transaction_ids': pattern['transaction_ids'],
                        'total_amount': float(pattern['total_amount']),
                        'transaction_count': pattern['transaction_count'],
                        'risk_score': self._calculate_carousel_risk(pattern),
                        'latest_date': pattern['latest_date']
                    })
                
                logger.info(f"Detected {len(results)} carousel patterns")
                return results
                
        except Exception as e:
            logger.error(f"Error detecting carousel patterns: {e}")
            return []
    
    def detect_velocity_bursts(self, time_window_minutes=15, threshold_count=5) -> List[Dict]:
        """
        Detect velocity bursts - unusual high frequency of transactions
        """
        query = """
        SELECT 
            a.client_id,
            t.sender_account_id,
            COUNT(*) as transaction_count,
            SUM(t.amount) as total_amount,
            AVG(t.amount) as avg_amount,
            MIN(t.transaction_date) as first_transaction,
            MAX(t.transaction_date) as last_transaction
        FROM transaction t
        JOIN account a ON t.sender_account_id = a.account_id
        WHERE t.transaction_date >= NOW() - INTERVAL '%s minutes'
        GROUP BY a.client_id, t.sender_account_id
        HAVING COUNT(*) >= %s
        ORDER BY transaction_count DESC, total_amount DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (time_window_minutes, threshold_count))
                bursts = cursor.fetchall()
                
                results = []
                for burst in bursts:
                    results.append({
                        'pattern_type': 'velocity_burst',
                        'client_id': burst['client_id'],
                        'account_id': burst['sender_account_id'],
                        'transaction_count': burst['transaction_count'],
                        'total_amount': float(burst['total_amount']),
                        'avg_amount': float(burst['avg_amount']),
                        'time_window_minutes': time_window_minutes,
                        'risk_score': self._calculate_velocity_risk(burst),
                        'first_transaction': burst['first_transaction'],
                        'last_transaction': burst['last_transaction']
                    })
                
                logger.info(f"Detected {len(results)} velocity bursts")
                return results
                
        except Exception as e:
            logger.error(f"Error detecting velocity bursts: {e}")
            return []
    
    def detect_layered_transactions(self, min_layers=3, time_window_hours=24) -> List[Dict]:
        """
        Detect layered transactions - complex money laundering patterns
        with multiple intermediate accounts
        """
        query = """
        WITH transaction_chains AS (
            SELECT 
                t1.sender_account_id as originator,
                tN.receiver_account_id as final_beneficiary,
                ARRAY_AGG(t1.sender_account_id ORDER BY t1.transaction_date) as account_chain,
                ARRAY_AGG(t1.transaction_id ORDER BY t1.transaction_date) as transaction_ids,
                SUM(t1.amount) as total_amount,
                COUNT(*) as chain_length,
                MAX(t1.transaction_date) as latest_date
            FROM (
                SELECT 
                    t.sender_account_id,
                    t.receiver_account_id,
                    t.transaction_id,
                    t.amount,
                    t.transaction_date,
                    ROW_NUMBER() OVER (PARTITION BY t.sender_account_id ORDER BY t.transaction_date) as rn
                FROM transaction t
                WHERE t.transaction_date >= NOW() - INTERVAL '%s hours'
            ) t1
            JOIN transaction t2 ON t1.receiver_account_id = t2.sender_account_id
            JOIN transaction t3 ON t2.receiver_account_id = t3.sender_account_id
            WHERE t3.transaction_date >= NOW() - INTERVAL '%s hours'
            AND t1.sender_account_id != t3.receiver_account_id
            GROUP BY t1.sender_account_id, t3.receiver_account_id
            HAVING COUNT(DISTINCT t1.receiver_account_id) >= %s
        )
        SELECT * FROM transaction_chains
        ORDER BY chain_length DESC, total_amount DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (time_window_hours, time_window_hours, min_layers - 1))
                layers = cursor.fetchall()
                
                results = []
                for layer in layers:
                    results.append({
                        'pattern_type': 'layered_transaction',
                        'originator': layer['originator'],
                        'final_beneficiary': layer['final_beneficiary'],
                        'account_chain': layer['account_chain'],
                        'transaction_ids': layer['transaction_ids'],
                        'total_amount': float(layer['total_amount']),
                        'chain_length': layer['chain_length'],
                        'risk_score': self._calculate_layered_risk(layer),
                        'latest_date': layer['latest_date']
                    })
                
                logger.info(f"Detected {len(results)} layered transaction patterns")
                return results
                
        except Exception as e:
            logger.error(f"Error detecting layered transactions: {e}")
            return []
    
    def analyze_network_clusters(self, min_cluster_size=5, time_window_days=7) -> List[Dict]:
        """
        Analyze transaction network to identify suspicious clusters
        using graph analysis
        """
        query = """
        SELECT 
            t.sender_account_id,
            t.receiver_account_id,
            COUNT(*) as transaction_count,
            SUM(t.amount) as total_amount,
            MAX(t.transaction_date) as last_transaction
        FROM transaction t
        WHERE t.transaction_date >= NOW() - INTERVAL '%s days'
        GROUP BY t.sender_account_id, t.receiver_account_id
        HAVING COUNT(*) >= 1
        ORDER BY transaction_count DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (time_window_days,))
                edges = cursor.fetchall()
                
                # Build network graph
                G = nx.Graph()
                
                for edge in edges:
                    G.add_edge(
                        edge['sender_account_id'], 
                        edge['receiver_account_id'],
                        weight=edge['transaction_count'],
                        total_amount=edge['total_amount']
                    )
                
                # Find connected components
                clusters = []
                for component in nx.connected_components(G):
                    if len(component) >= min_cluster_size:
                        subgraph = G.subgraph(component)
                        
                        # Calculate cluster metrics
                        density = nx.density(subgraph)
                        avg_clustering = nx.average_clustering(subgraph)
                        
                        # Find central nodes
                        centrality = nx.degree_centrality(subgraph)
                        central_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]
                        
                        clusters.append({
                            'pattern_type': 'network_cluster',
                            'cluster_size': len(component),
                            'accounts': list(component),
                            'density': density,
                            'avg_clustering_coefficient': avg_clustering,
                            'central_accounts': central_nodes,
                            'risk_score': self._calculate_cluster_risk(subgraph),
                            'transaction_count': subgraph.size(weight='weight')
                        })
                
                logger.info(f"Detected {len(clusters)} suspicious network clusters")
                return clusters
                
        except Exception as e:
            logger.error(f"Error analyzing network clusters: {e}")
            return []
    
    def detect_new_device_patterns(self, device_age_hours=24) -> List[Dict]:
        """
        Detect transactions from new or suspicious devices
        """
        query = """
        SELECT 
            d.device_id,
            d.device_fingerprint,
            d.device_type,
            d.os,
            d.browser,
            d.first_seen_date,
            COUNT(t.transaction_id) as transaction_count,
            SUM(t.amount) as total_amount,
            COUNT(DISTINCT t.sender_account_id) as unique_accounts,
            MIN(t.transaction_date) as first_transaction,
            MAX(t.transaction_date) as last_transaction
        FROM device d
        LEFT JOIN transaction t ON d.device_id = t.device_id
        WHERE d.first_seen_date >= NOW() - INTERVAL '%s hours'
        GROUP BY d.device_id, d.device_fingerprint, d.device_type, d.os, d.browser, d.first_seen_date
        ORDER BY transaction_count DESC, total_amount DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (device_age_hours,))
                devices = cursor.fetchall()
                
                results = []
                for device in devices:
                    results.append({
                        'pattern_type': 'new_device',
                        'device_id': device['device_id'],
                        'device_fingerprint': device['device_fingerprint'],
                        'device_type': device['device_type'],
                        'os': device['os'],
                        'browser': device['browser'],
                        'device_age_hours': device_age_hours,
                        'transaction_count': device['transaction_count'],
                        'total_amount': float(device['total_amount']) if device['total_amount'] else 0,
                        'unique_accounts': device['unique_accounts'],
                        'risk_score': self._calculate_device_risk(device),
                        'first_transaction': device['first_transaction'],
                        'last_transaction': device['last_transaction']
                    })
                
                logger.info(f"Detected {len(results)} new device patterns")
                return results
                
        except Exception as e:
            logger.error(f"Error detecting new device patterns: {e}")
            return []
    
    def detect_suspicious_ip_patterns(self) -> List[Dict]:
        """
        Detect transactions from suspicious IP addresses
        """
        query = """
        SELECT 
            ip.ip_address_id,
            ip.ip_address,
            ip.country,
            ip.is_proxy,
            ip.is_tor,
            ip.is_vpn,
            ip.threat_level,
            COUNT(t.transaction_id) as transaction_count,
            SUM(t.amount) as total_amount,
            COUNT(DISTINCT t.sender_account_id) as unique_accounts,
            MIN(t.transaction_date) as first_transaction,
            MAX(t.transaction_date) as last_transaction
        FROM ipaddress ip
        LEFT JOIN transaction t ON ip.ip_address_id = t.ip_address_id
        WHERE ip.is_proxy = TRUE OR ip.is_tor = TRUE OR ip.threat_level IN ('high', 'critical')
        GROUP BY ip.ip_address_id, ip.ip_address, ip.country, ip.is_proxy, ip.is_tor, ip.is_vpn, ip.threat_level
        ORDER BY transaction_count DESC, total_amount DESC;
        """
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query)
                ips = cursor.fetchall()
                
                results = []
                for ip in ips:
                    results.append({
                        'pattern_type': 'suspicious_ip',
                        'ip_address_id': ip['ip_address_id'],
                        'ip_address': str(ip['ip_address']),
                        'country': ip['country'],
                        'is_proxy': ip['is_proxy'],
                        'is_tor': ip['is_tor'],
                        'is_vpn': ip['is_vpn'],
                        'threat_level': ip['threat_level'],
                        'transaction_count': ip['transaction_count'],
                        'total_amount': float(ip['total_amount']) if ip['total_amount'] else 0,
                        'unique_accounts': ip['unique_accounts'],
                        'risk_score': self._calculate_ip_risk(ip),
                        'first_transaction': ip['first_transaction'],
                        'last_transaction': ip['last_transaction']
                    })
                
                logger.info(f"Detected {len(results)} suspicious IP patterns")
                return results
                
        except Exception as e:
            logger.error(f"Error detecting suspicious IP patterns: {e}")
            return []
    
    def _calculate_carousel_risk(self, pattern) -> float:
        """Calculate risk score for carousel patterns"""
        base_score = 0.7
        length_multiplier = min(pattern['path_length'] * 0.1, 0.3)
        amount_multiplier = min(pattern['total_amount'] / 100000, 0.2)
        return min(base_score + length_multiplier + amount_multiplier, 1.0)
    
    def _calculate_velocity_risk(self, burst) -> float:
        """Calculate risk score for velocity bursts"""
        base_score = 0.5
        count_multiplier = min(burst['transaction_count'] * 0.05, 0.3)
        amount_multiplier = min(burst['total_amount'] / 50000, 0.2)
        return min(base_score + count_multiplier + amount_multiplier, 1.0)
    
    def _calculate_layered_risk(self, layer) -> float:
        """Calculate risk score for layered transactions"""
        base_score = 0.6
        layer_multiplier = min(layer['chain_length'] * 0.1, 0.3)
        amount_multiplier = min(layer['total_amount'] / 100000, 0.2)
        return min(base_score + layer_multiplier + amount_multiplier, 1.0)
    
    def _calculate_cluster_risk(self, subgraph) -> float:
        """Calculate risk score for network clusters"""
        base_score = 0.4
        size_multiplier = min(len(subgraph.nodes()) * 0.02, 0.3)
        density_multiplier = min(nx.density(subgraph) * 0.5, 0.3)
        return min(base_score + size_multiplier + density_multiplier, 1.0)
    
    def _calculate_device_risk(self, device) -> float:
        """Calculate risk score for new devices"""
        base_score = 0.3
        transaction_multiplier = min(device['transaction_count'] * 0.05, 0.3)
        account_multiplier = min(device['unique_accounts'] * 0.1, 0.2)
        amount_multiplier = min((device['total_amount'] or 0) / 10000, 0.2)
        return min(base_score + transaction_multiplier + account_multiplier + amount_multiplier, 1.0)
    
    def _calculate_ip_risk(self, ip) -> float:
        """Calculate risk score for suspicious IPs"""
        base_score = 0.5
        if ip['is_tor']:
            base_score += 0.3
        if ip['is_proxy']:
            base_score += 0.2
        if ip['threat_level'] == 'critical':
            base_score += 0.2
        elif ip['threat_level'] == 'high':
            base_score += 0.1
        
        transaction_multiplier = min(ip['transaction_count'] * 0.02, 0.2)
        account_multiplier = min(ip['unique_accounts'] * 0.05, 0.1)
        
        return min(base_score + transaction_multiplier + account_multiplier, 1.0)
    
    def create_alerts_for_patterns(self, patterns: List[Dict]) -> None:
        """Create alerts for detected fraud patterns"""
        for pattern in patterns:
            try:
                with self.conn.cursor() as cursor:
                    # Determine alert severity based on risk score
                    if pattern['risk_score'] >= 0.8:
                        severity = 'critical'
                    elif pattern['risk_score'] >= 0.6:
                        severity = 'high'
                    elif pattern['risk_score'] >= 0.4:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    # Create alert
                    alert_query = """
                    INSERT INTO alert (alert_type, severity, title, description, risk_score, auto_generated)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                    """
                    
                    title = f"{pattern['pattern_type'].replace('_', ' ').title()} Detected"
                    description = f"Suspicious {pattern['pattern_type']} with risk score {pattern['risk_score']:.2f}"
                    
                    cursor.execute(alert_query, (
                        'fraud',
                        severity,
                        title,
                        description,
                        pattern['risk_score']
                    ))
                
                self.conn.commit()
                
            except Exception as e:
                logger.error(f"Error creating alert for pattern: {e}")
                self.conn.rollback()
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all fraud detection algorithms"""
        logger.info("Starting comprehensive fraud detection analysis")
        
        results = {
            'timestamp': datetime.now(),
            'patterns': [],
            'total_patterns': 0,
            'high_risk_patterns': 0
        }
        
        # Run all detection algorithms
        patterns = []
        patterns.extend(self.detect_carousel_patterns())
        patterns.extend(self.detect_velocity_bursts())
        patterns.extend(self.detect_layered_transactions())
        patterns.extend(self.analyze_network_clusters())
        patterns.extend(self.detect_new_device_patterns())
        patterns.extend(self.detect_suspicious_ip_patterns())
        
        # Sort by risk score
        patterns.sort(key=lambda x: x['risk_score'], reverse=True)
        
        results['patterns'] = patterns
        results['total_patterns'] = len(patterns)
        results['high_risk_patterns'] = len([p for p in patterns if p['risk_score'] >= 0.7])
        
        # Create alerts for high-risk patterns
        high_risk_patterns = [p for p in patterns if p['risk_score'] >= 0.6]
        if high_risk_patterns:
            self.create_alerts_for_patterns(high_risk_patterns)
        
        logger.info(f"Analysis complete. Found {len(patterns)} patterns, {len(high_risk_patterns)} high-risk")
        
        return results

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'antifraud_p2p',
        'user': 'antifraud_user',
        'password': 'antifraud_pass',
        'port': 5432
    }
    
    # Initialize and run fraud detection
    detector = AdvancedFraudDetection(db_config)
    results = detector.run_comprehensive_analysis()
    
    # Print results
    print(f"\n=== Fraud Detection Results ===")
    print(f"Analysis Time: {results['timestamp']}")
    print(f"Total Patterns Detected: {results['total_patterns']}")
    print(f"High-Risk Patterns: {results['high_risk_patterns']}")
    
    print(f"\n=== Top 10 Riskiest Patterns ===")
    for i, pattern in enumerate(results['patterns'][:10], 1):
        print(f"{i}. {pattern['pattern_type']} - Risk Score: {pattern['risk_score']:.2f}")