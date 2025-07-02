"""
Database module for Ariel system
Handles all database operations and connections
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger("ArielDatabase")

class ArielDatabase:
    """
    Database manager for the Ariel system
    Handles SQLite operations with async support
    """
    
    def __init__(self, db_path: str = "ariel_system.db"):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create main tables
            self._create_tables(cursor)
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self, cursor):
        """Create all required database tables"""
        
        # Ariel logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ariel_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cycle_number INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                data TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cycle history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER NOT NULL,
                duration REAL NOT NULL,
                opportunities_found INTEGER DEFAULT 0,
                revenue_generated REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Dashboard metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initialized BOOLEAN DEFAULT FALSE,
                timestamp TEXT NOT NULL,
                total_cycles INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                last_cycle_duration REAL DEFAULT 0.0,
                last_opportunities INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                symbol TEXT,
                confidence REAL DEFAULT 0.0,
                potential_revenue REAL DEFAULT 0.0,
                source TEXT,
                data TEXT DEFAULT '{}',
                status TEXT DEFAULT 'identified',
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Revenue records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                description TEXT,
                transaction_id TEXT,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL,
                symbol TEXT,
                quantity REAL DEFAULT 0.0,
                value REAL DEFAULT 0.0,
                acquisition_price REAL DEFAULT 0.0,
                acquisition_date TEXT,
                status TEXT DEFAULT 'active',
                data TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_type TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                budget REAL DEFAULT 0.0,
                spent REAL DEFAULT 0.0,
                revenue REAL DEFAULT 0.0,
                roi REAL DEFAULT 0.0,
                start_date TEXT,
                end_date TEXT,
                data TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_type TEXT NOT NULL,
                results TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Neural engine data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neural_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                training_data TEXT,
                predictions TEXT,
                accuracy REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def insert_one(self, table: str, data: Dict) -> int:
        """Insert a single record into table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare data
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ','.join(['?' for _ in values])
            
            # Convert complex objects to JSON strings
            processed_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    processed_values.append(json.dumps(value))
                else:
                    processed_values.append(value)
            
            # Execute insert
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, processed_values)
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return record_id
            
        except Exception as e:
            logger.error(f"Insert failed for table {table}: {e}")
            raise
    
    async def find_one(self, table: str, conditions: Dict = None) -> Optional[Dict]:
        """Find a single record from table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = f"SELECT * FROM {table}"
            params = []
            
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                query += f" WHERE {' AND '.join(where_clauses)}"
            
            query += " ORDER BY id DESC LIMIT 1"
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create dictionary
                result = dict(zip(columns, row))
                
                # Parse JSON fields
                for key, value in result.items():
                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                        try:
                            result[key] = json.loads(value)
                        except:
                            pass  # Keep as string if not valid JSON
                
                conn.close()
                return result
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Find one failed for table {table}: {e}")
            return None
    
    async def find_many(self, table: str, conditions: Dict = None, limit: int = 100) -> List[Dict]:
        """Find multiple records from table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = f"SELECT * FROM {table}"
            params = []
            
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                query += f" WHERE {' AND '.join(where_clauses)}"
            
            query += f" ORDER BY id DESC LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create list of dictionaries
                results = []
                for row in rows:
                    result = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    for key, value in result.items():
                        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                            try:
                                result[key] = json.loads(value)
                            except:
                                pass  # Keep as string if not valid JSON
                    
                    results.append(result)
                
                conn.close()
                return results
            
            conn.close()
            return []
            
        except Exception as e:
            logger.error(f"Find many failed for table {table}: {e}")
            return []
    
    async def to_list(self, table: str, limit: int = 100) -> List[Dict]:
        """Get records as list (alias for find_many)"""
        return await self.find_many(table, limit=limit)
    
    async def update_one(self, table: str, conditions: Dict, updates: Dict) -> bool:
        """Update a single record in table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                if isinstance(value, (dict, list)):
                    params.append(json.dumps(value))
                else:
                    params.append(value)
            
            # Build where clause
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            
            query = f"UPDATE {table} SET {','.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
            
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Update failed for table {table}: {e}")
            return False
    
    async def delete_one(self, table: str, conditions: Dict) -> bool:
        """Delete a single record from table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build delete query
            where_clauses = []
            params = []
            
            for key, value in conditions.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            
            query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)} LIMIT 1"
            
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Delete failed for table {table}: {e}")
            return False
    
    async def delete_many(self, table: str, conditions: Dict = None) -> int:
        """Delete multiple records from table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build delete query
            query = f"DELETE FROM {table}"
            params = []
            
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                query += f" WHERE {' AND '.join(where_clauses)}"
            
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Delete many failed for table {table}: {e}")
            return 0
    
    async def count(self, table: str, conditions: Dict = None) -> int:
        """Count records in table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build count query
            query = f"SELECT COUNT(*) FROM {table}"
            params = []
            
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                query += f" WHERE {' AND '.join(where_clauses)}"
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Count failed for table {table}: {e}")
            return 0
    
    async def execute_query(self, query: str, params: List = None) -> List[Dict]:
        """Execute custom SQL query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            if rows:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create list of dictionaries
                results = []
                for row in rows:
                    result = dict(zip(columns, row))
                    results.append(result)
                
                conn.close()
                return results
            
            conn.close()
            return []
            
        except Exception as e:
            logger.error(f"Custom query failed: {e}")
            return []
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Get table counts
            tables = [
                'ariel_logs', 'cycle_history', 'dashboard_metrics',
                'opportunities', 'revenue_records', 'assets',
                'campaigns', 'test_reports', 'system_metrics', 'neural_data'
            ]
            
            for table in tables:
                count = await self.count(table)
                stats[f"{table}_count"] = count
            
            # Get database file size
            if os.path.exists(self.db_path):
                stats["database_size_bytes"] = os.path.getsize(self.db_path)
                stats["database_size_mb"] = stats["database_size_bytes"] / (1024 * 1024)
            
            stats["database_path"] = self.db_path
            stats["last_updated"] = datetime.utcnow().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Database stats failed: {e}")
            return {"error": str(e)}

# Global database instance
_db_instance = None

async def get_db() -> ArielDatabase:
    """Get database instance (singleton pattern)"""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ArielDatabase()
    
    return _db_instance

async def init_database():
    """Initialize database"""
    db = await get_db()
    logger.info("✅ Database initialized and ready")
    return db
