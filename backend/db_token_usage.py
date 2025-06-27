#!/usr/bin/env python3
"""
Token Usage Database Module
Handles tracking of Azure OpenAI token usage for both transcriber and agent services
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger("token-usage-db")

@dataclass
class TokenUsageRecord:
    session_id: str
    user_name: str
    service_type: str  # 'transcriber' or 'agent'
    model_name: str    # 'whisper' or 'gpt-4o-realtime'
    input_tokens: int
    output_tokens: int
    total_tokens: int
    session_start: datetime
    session_end: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

class TokenUsageDatabase:
    def __init__(self, db_path: str = "token_usage.sqlite"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the token usage database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create token_usage table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS token_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_name TEXT,
                        service_type TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        input_tokens INTEGER DEFAULT 0,
                        output_tokens INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        session_start TIMESTAMP,
                        session_end TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_id 
                    ON token_usage(session_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_name 
                    ON token_usage(user_name)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_service_type 
                    ON token_usage(service_type)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON token_usage(created_at)
                """)
                
                conn.commit()
                logger.info("Token usage database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing token usage database: {e}")
            raise
    
    def start_session(self, session_id: str, user_name: str, service_type: str, model_name: str) -> int:
        """Start a new token tracking session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO token_usage 
                    (session_id, user_name, service_type, model_name, session_start)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, user_name, service_type, model_name, datetime.now()))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Started token tracking session: {session_id} for {service_type}/{model_name}")
                return record_id
                
        except Exception as e:
            logger.error(f"Error starting token session: {e}")
            raise
    
    def update_token_usage(self, session_id: str, service_type: str, input_tokens: int, output_tokens: int):
        """Update token usage for an active session"""
        try:
            total_tokens = input_tokens + output_tokens
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update existing record by adding to current totals
                cursor.execute("""
                    UPDATE token_usage 
                    SET input_tokens = input_tokens + ?,
                        output_tokens = output_tokens + ?,
                        total_tokens = total_tokens + ?
                    WHERE session_id = ? AND service_type = ? AND session_end IS NULL
                """, (input_tokens, output_tokens, total_tokens, session_id, service_type))
                
                if cursor.rowcount == 0:
                    logger.warning(f"No active session found for {session_id}/{service_type}")
                else:
                    conn.commit()
                    logger.debug(f"Updated tokens for {session_id}/{service_type}: +{input_tokens} input, +{output_tokens} output")
                
        except Exception as e:
            logger.error(f"Error updating token usage: {e}")
            raise
    
    def end_session(self, session_id: str, service_type: str = None):
        """End token tracking session(s)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if service_type:
                    # End specific service session
                    cursor.execute("""
                        UPDATE token_usage 
                        SET session_end = ?
                        WHERE session_id = ? AND service_type = ? AND session_end IS NULL
                    """, (datetime.now(), session_id, service_type))
                else:
                    # End all sessions for this session_id
                    cursor.execute("""
                        UPDATE token_usage 
                        SET session_end = ?
                        WHERE session_id = ? AND session_end IS NULL
                    """, (datetime.now(), session_id))
                
                conn.commit()
                logger.info(f"Ended token tracking session: {session_id}" + (f"/{service_type}" if service_type else ""))
                
        except Exception as e:
            logger.error(f"Error ending token session: {e}")
            raise
    
    def get_session_usage(self, session_id: str) -> List[TokenUsageRecord]:
        """Get token usage for a specific session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, session_id, user_name, service_type, model_name,
                           input_tokens, output_tokens, total_tokens,
                           session_start, session_end, created_at
                    FROM token_usage
                    WHERE session_id = ?
                    ORDER BY created_at
                """, (session_id,))
                
                records = []
                for row in cursor.fetchall():
                    records.append(TokenUsageRecord(
                        id=row[0],
                        session_id=row[1],
                        user_name=row[2],
                        service_type=row[3],
                        model_name=row[4],
                        input_tokens=row[5],
                        output_tokens=row[6],
                        total_tokens=row[7],
                        session_start=datetime.fromisoformat(row[8]) if row[8] else None,
                        session_end=datetime.fromisoformat(row[9]) if row[9] else None,
                        created_at=datetime.fromisoformat(row[10]) if row[10] else None
                    ))
                
                return records
                
        except Exception as e:
            logger.error(f"Error getting session usage: {e}")
            return []
    
    def get_usage_summary(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Get usage summary with optional date filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                where_clause = ""
                params = []
                
                if start_date:
                    where_clause += " AND created_at >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    where_clause += " AND created_at <= ?"
                    params.append(end_date.isoformat())
                
                # Get summary by service type and model
                cursor.execute(f"""
                    SELECT service_type, model_name,
                           COUNT(*) as session_count,
                           SUM(input_tokens) as total_input_tokens,
                           SUM(output_tokens) as total_output_tokens,
                           SUM(total_tokens) as total_tokens,
                           AVG(total_tokens) as avg_tokens_per_session
                    FROM token_usage
                    WHERE 1=1 {where_clause}
                    GROUP BY service_type, model_name
                    ORDER BY total_tokens DESC
                """, params)
                
                summary = {
                    "by_service": {},
                    "totals": {
                        "sessions": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0
                    }
                }
                
                for row in cursor.fetchall():
                    service_type, model_name, session_count, input_tokens, output_tokens, total_tokens, avg_tokens = row
                    
                    if service_type not in summary["by_service"]:
                        summary["by_service"][service_type] = {}
                    
                    summary["by_service"][service_type][model_name] = {
                        "session_count": session_count,
                        "input_tokens": input_tokens or 0,
                        "output_tokens": output_tokens or 0,
                        "total_tokens": total_tokens or 0,
                        "avg_tokens_per_session": round(avg_tokens or 0, 2)
                    }
                    
                    # Add to totals
                    summary["totals"]["sessions"] += session_count
                    summary["totals"]["input_tokens"] += input_tokens or 0
                    summary["totals"]["output_tokens"] += output_tokens or 0
                    summary["totals"]["total_tokens"] += total_tokens or 0
                
                return summary
                
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {"by_service": {}, "totals": {"sessions": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}

# Global instance
token_db = TokenUsageDatabase()
