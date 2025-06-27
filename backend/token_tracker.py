#!/usr/bin/env python3
"""
Token Tracking Service
Centralized service for tracking Azure OpenAI token usage across transcriber and agent services
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from db_token_usage import token_db, TokenUsageRecord

logger = logging.getLogger("token-tracker")

class TokenTracker:
    def __init__(self):
        self.active_sessions = {}  # session_id -> session_info
    
    def start_session(self, room_name: str, user_name: str, participant_identity: str) -> str:
        """Start a new token tracking session for a user"""
        # First, clean up any existing sessions for this room/user combination
        self.cleanup_existing_sessions(room_name, participant_identity)
        
        # Create unique session ID with timestamp to avoid conflicts
        timestamp = int(datetime.now().timestamp())
        session_id = f"{room_name}_{participant_identity}_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        session_info = {
            "session_id": session_id,
            "room_name": room_name,
            "user_name": user_name,
            "participant_identity": participant_identity,
            "created_at": datetime.now(),
            "services": {}  # service_type -> service_info
        }
        
        self.active_sessions[session_id] = session_info
        logger.info(f"Started token tracking session: {session_id} for user: {user_name}")
        
        return session_id
    
    def register_service(self, session_id: str, service_type: str, model_name: str) -> bool:
        """Register a service (transcriber or agent) for token tracking"""
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found for service registration")
            return False
        
        session_info = self.active_sessions[session_id]
        user_name = session_info["user_name"]
        
        try:
            # Create database record for this service
            record_id = token_db.start_session(session_id, user_name, service_type, model_name)
            
            # Track service in memory
            session_info["services"][service_type] = {
                "model_name": model_name,
                "record_id": record_id,
                "total_input_tokens": 0,
                "total_output_tokens": 0
            }
            
            logger.info(f"Registered {service_type} service for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering service {service_type} for session {session_id}: {e}")
            return False
    
    def track_tokens(self, session_id: str, service_type: str, input_tokens: int, output_tokens: int):
        """Track token usage for a specific service in a session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found for token tracking")
            return
        
        session_info = self.active_sessions[session_id]
        
        if service_type not in session_info["services"]:
            logger.warning(f"Service {service_type} not registered for session {session_id}")
            return
        
        try:
            # Update database
            token_db.update_token_usage(session_id, service_type, input_tokens, output_tokens)
            
            # Update in-memory tracking
            service_info = session_info["services"][service_type]
            service_info["total_input_tokens"] += input_tokens
            service_info["total_output_tokens"] += output_tokens
            
            logger.debug(f"Tracked tokens for {session_id}/{service_type}: +{input_tokens} input, +{output_tokens} output")
            
        except Exception as e:
            logger.error(f"Error tracking tokens for {session_id}/{service_type}: {e}")
    
    def end_session(self, session_id: str, service_type: str = None) -> Dict[str, Any]:
        """End token tracking session and return usage summary"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found for ending")
            return {}
        
        session_info = self.active_sessions[session_id]
        
        try:
            # End database session(s)
            token_db.end_session(session_id, service_type)
            
            # Get final usage summary
            usage_records = token_db.get_session_usage(session_id)
            
            # Create summary
            summary = {
                "session_id": session_id,
                "user_name": session_info["user_name"],
                "room_name": session_info["room_name"],
                "services": {},
                "totals": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            for record in usage_records:
                summary["services"][record.service_type] = {
                    "model_name": record.model_name,
                    "input_tokens": record.input_tokens,
                    "output_tokens": record.output_tokens,
                    "total_tokens": record.total_tokens,
                    "session_start": record.session_start.isoformat() if record.session_start else None,
                    "session_end": record.session_end.isoformat() if record.session_end else None
                }
                
                summary["totals"]["input_tokens"] += record.input_tokens
                summary["totals"]["output_tokens"] += record.output_tokens
                summary["totals"]["total_tokens"] += record.total_tokens
            
            # Clean up in-memory session if ending all services
            if not service_type:
                del self.active_sessions[session_id]
                logger.info(f"Ended complete token tracking session: {session_id}")
            else:
                # Remove specific service
                if service_type in session_info["services"]:
                    del session_info["services"][service_type]
                logger.info(f"Ended {service_type} service for session: {session_id}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return {}
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get current session summary without ending it"""
        if session_id not in self.active_sessions:
            return {}
        
        session_info = self.active_sessions[session_id]
        
        summary = {
            "session_id": session_id,
            "user_name": session_info["user_name"],
            "room_name": session_info["room_name"],
            "services": {},
            "totals": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
        }
        
        for service_type, service_info in session_info["services"].items():
            summary["services"][service_type] = {
                "model_name": service_info["model_name"],
                "input_tokens": service_info["total_input_tokens"],
                "output_tokens": service_info["total_output_tokens"],
                "total_tokens": service_info["total_input_tokens"] + service_info["total_output_tokens"]
            }
            
            summary["totals"]["input_tokens"] += service_info["total_input_tokens"]
            summary["totals"]["output_tokens"] += service_info["total_output_tokens"]
            summary["totals"]["total_tokens"] += service_info["total_input_tokens"] + service_info["total_output_tokens"]
        
        return summary
    
    def find_session_by_room_and_user(self, room_name: str, participant_identity: str) -> Optional[str]:
        """Find active session by room name and participant identity"""
        for session_id, session_info in self.active_sessions.items():
            if (session_info["room_name"] == room_name and 
                session_info["participant_identity"] == participant_identity):
                return session_id
        return None
    
    def cleanup_existing_sessions(self, room_name: str, participant_identity: str):
        """Clean up any existing sessions for the same room/user combination"""
        sessions_to_remove = []
        
        for session_id, session_info in self.active_sessions.items():
            if (session_info["room_name"] == room_name and 
                session_info["participant_identity"] == participant_identity):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            logger.info(f"Cleaning up existing session: {session_id}")
            try:
                # End the database session
                token_db.end_session(session_id)
                # Remove from memory
                del self.active_sessions[session_id]
            except Exception as e:
                logger.error(f"Error cleaning up session {session_id}: {e}")
    
    def cleanup_stale_sessions(self, max_age_hours: int = 24):
        """Clean up sessions that may have been left open due to ungraceful disconnections"""
        current_time = datetime.now()
        stale_sessions = []
        
        for session_id, session_info in self.active_sessions.items():
            created_at = session_info.get("created_at")
            if created_at:
                age_hours = (current_time - created_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    stale_sessions.append(session_id)
                    logger.warning(f"Found stale session: {session_id} (age: {age_hours:.1f} hours)")
        
        # Clean up stale sessions
        for session_id in stale_sessions:
            try:
                logger.info(f"Cleaning up stale session: {session_id}")
                token_db.end_session(session_id)
                del self.active_sessions[session_id]
            except Exception as e:
                logger.error(f"Error cleaning up stale session {session_id}: {e}")
        
        return len(stale_sessions)

# Global instance
token_tracker = TokenTracker()
