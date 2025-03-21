"""
Database service for the Hotel AI Assistant.

This module provides functions to interact with the database.
"""

import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from ..config import DATABASE_URL, DATA_RETENTION_DAYS, ANONYMIZE_DATA

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for interacting with the database."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize the database service.
        
        Args:
            database_url: The URL of the database to connect to
        """
        self.database_url = database_url
        self.connection = None
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection to the database.
        
        Returns:
            A connection to the database
        """
        if self.connection is None:
            # Extract the path from the URL (for SQLite)
            if self.database_url.startswith("sqlite:///"):
                path = self.database_url[10:]
                self.connection = sqlite3.connect(path)
                self.connection.row_factory = sqlite3.Row
            else:
                raise ValueError(f"Unsupported database URL: {self.database_url}")
        
        return self.connection
    
    def initialize_database(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create agent_actions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_data TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create agent_conversations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            user_id TEXT,
            agent_id TEXT NOT NULL,
            message TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create agent_approvals table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id INTEGER NOT NULL,
            approved_by TEXT,
            status TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (action_id) REFERENCES agent_actions (id)
        )
        """)
        
        # Create user_consent table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_consent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            service_improvement BOOLEAN DEFAULT FALSE,
            analytics BOOLEAN DEFAULT FALSE,
            model_training BOOLEAN DEFAULT FALSE,
            marketing BOOLEAN DEFAULT FALSE,
            consent_version TEXT NOT NULL,
            ip_address TEXT,
            consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create anonymized_conversations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS anonymized_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anonymized_user_id TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            message_type TEXT NOT NULL,
            message_content TEXT NOT NULL,
            intent_category TEXT,
            sentiment_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            retention_expires_at TIMESTAMP
        )
        """)
        
        # Create data_deletion_requests table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_deletion_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            request_type TEXT NOT NULL,
            status TEXT NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            verification_token TEXT,
            notes TEXT
        )
        """)
        
        # Create data_access_log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT NOT NULL,
            user_id TEXT,
            accessed_by TEXT NOT NULL,
            access_reason TEXT NOT NULL,
            access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
        """)
        
        conn.commit()
        logger.info("Database initialized")
    
    def log_agent_action(self, agent_id: str, action_type: str, action_data: Dict[str, Any], status: str = "pending") -> int:
        """Log an agent action in the database.
        
        Args:
            agent_id: The ID of the agent
            action_type: The type of action
            action_data: The data associated with the action
            status: The status of the action
            
        Returns:
            The ID of the created action
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO agent_actions (agent_id, action_type, action_data, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (agent_id, action_type, json.dumps(action_data), status)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def update_agent_action_status(self, action_id: int, status: str) -> None:
        """Update the status of an agent action.
        
        Args:
            action_id: The ID of the action
            status: The new status
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE agent_actions
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (status, action_id)
        )
        
        conn.commit()
    
    def log_conversation_message(self, conversation_id: str, agent_id: str, message: str, role: str, user_id: Optional[str] = None) -> int:
        """Log a conversation message in the database.
        
        Args:
            conversation_id: The ID of the conversation
            agent_id: The ID of the agent
            message: The message content
            role: The role of the message sender (user or assistant)
            user_id: The ID of the user (optional)
            
        Returns:
            The ID of the created message
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO agent_conversations (conversation_id, user_id, agent_id, message, role, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (conversation_id, user_id, agent_id, message, role)
        )
        
        conn.commit()
        
        # If anonymization is enabled, also store an anonymized version
        if ANONYMIZE_DATA:
            self.store_anonymized_conversation(conversation_id, message, role, user_id)
        
        return cursor.lastrowid
    
    def store_anonymized_conversation(self, conversation_id: str, message: str, message_type: str, user_id: Optional[str] = None) -> int:
        """Store an anonymized version of a conversation message.
        
        Args:
            conversation_id: The ID of the conversation
            message: The message content
            message_type: The type of message (user or assistant)
            user_id: The ID of the user (optional)
            
        Returns:
            The ID of the created anonymized message
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate an anonymized user ID (hash of the original ID)
        anonymized_user_id = f"anon_{hash(user_id) % 10000000}" if user_id else "anon_unknown"
        
        # Calculate retention expiration date
        retention_expires_at = (datetime.now() + timedelta(days=DATA_RETENTION_DAYS)).isoformat()
        
        # TODO: Implement more sophisticated anonymization (e.g., remove PII)
        # For now, we're just using a simple anonymized user ID
        
        cursor.execute(
            """
            INSERT INTO anonymized_conversations (
                anonymized_user_id, conversation_id, message_type, message_content,
                created_at, retention_expires_at
            )
            VALUES (?, ?, ?, ?, datetime('now'), ?)
            """,
            (anonymized_user_id, conversation_id, message_type, message, retention_expires_at)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get the history of a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            A list of messages in the conversation
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM agent_conversations
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,)
        )
        
        # Convert rows to dictionaries
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "user_id": row["user_id"],
                "agent_id": row["agent_id"],
                "message": row["message"],
                "role": row["role"],
                "created_at": row["created_at"]
            })
        
        return messages
    
    def record_user_consent(self, user_id: str, consent_data: Dict[str, bool], consent_version: str, ip_address: Optional[str] = None) -> int:
        """Record user consent for data collection.
        
        Args:
            user_id: The ID of the user
            consent_data: Dictionary of consent options (service_improvement, analytics, etc.)
            consent_version: The version of the consent policy
            ip_address: The IP address of the user (optional)
            
        Returns:
            The ID of the created consent record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if consent already exists for this user
        cursor.execute(
            """
            SELECT id FROM user_consent
            WHERE user_id = ?
            """,
            (user_id,)
        )
        
        existing_consent = cursor.fetchone()
        
        if existing_consent:
            # Update existing consent
            cursor.execute(
                """
                UPDATE user_consent
                SET service_improvement = ?, analytics = ?, model_training = ?, marketing = ?,
                    consent_version = ?, ip_address = ?, last_updated = datetime('now')
                WHERE user_id = ?
                """,
                (
                    consent_data.get("service_improvement", False),
                    consent_data.get("analytics", False),
                    consent_data.get("model_training", False),
                    consent_data.get("marketing", False),
                    consent_version,
                    ip_address,
                    user_id
                )
            )
            
            conn.commit()
            return existing_consent["id"]
        else:
            # Create new consent record
            cursor.execute(
                """
                INSERT INTO user_consent (
                    user_id, service_improvement, analytics, model_training, marketing,
                    consent_version, ip_address, consent_timestamp, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    user_id,
                    consent_data.get("service_improvement", False),
                    consent_data.get("analytics", False),
                    consent_data.get("model_training", False),
                    consent_data.get("marketing", False),
                    consent_version,
                    ip_address
                )
            )
            
            conn.commit()
            return cursor.lastrowid
    
    def get_user_consent(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the consent settings for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The consent settings, or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM user_consent
            WHERE user_id = ?
            """,
            (user_id,)
        )
        
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "service_improvement": bool(row["service_improvement"]),
                "analytics": bool(row["analytics"]),
                "model_training": bool(row["model_training"]),
                "marketing": bool(row["marketing"]),
                "consent_version": row["consent_version"],
                "ip_address": row["ip_address"],
                "consent_timestamp": row["consent_timestamp"],
                "last_updated": row["last_updated"]
            }
        
        return None
    
    def request_data_deletion(self, user_id: str, request_type: str = "all") -> int:
        """Request deletion of user data.
        
        Args:
            user_id: The ID of the user
            request_type: The type of data to delete (all, conversations, etc.)
            
        Returns:
            The ID of the created deletion request
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate a verification token
        verification_token = f"verify_{hash(user_id + datetime.now().isoformat()) % 10000000}"
        
        cursor.execute(
            """
            INSERT INTO data_deletion_requests (
                user_id, request_type, status, requested_at, verification_token
            )
            VALUES (?, ?, ?, datetime('now'), ?)
            """,
            (user_id, request_type, "pending", verification_token)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def execute_data_deletion(self, request_id: int) -> bool:
        """Execute a data deletion request.
        
        Args:
            request_id: The ID of the deletion request
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the deletion request
        cursor.execute(
            """
            SELECT * FROM data_deletion_requests
            WHERE id = ?
            """,
            (request_id,)
        )
        
        request = cursor.fetchone()
        
        if not request:
            logger.error(f"Deletion request not found: {request_id}")
            return False
        
        user_id = request["user_id"]
        request_type = request["request_type"]
        
        try:
            # Delete data based on request type
            if request_type == "all":
                # Delete all user data
                cursor.execute("DELETE FROM agent_conversations WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM anonymized_conversations WHERE anonymized_user_id LIKE ?", (f"anon_{hash(user_id) % 10000000}",))
                cursor.execute("DELETE FROM user_consent WHERE user_id = ?", (user_id,))
            elif request_type == "conversations":
                # Delete only conversation data
                cursor.execute("DELETE FROM agent_conversations WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM anonymized_conversations WHERE anonymized_user_id LIKE ?", (f"anon_{hash(user_id) % 10000000}",))
            
            # Update the deletion request status
            cursor.execute(
                """
                UPDATE data_deletion_requests
                SET status = ?, completed_at = datetime('now')
                WHERE id = ?
                """,
                ("completed", request_id)
            )
            
            conn.commit()
            logger.info(f"Data deletion completed for user {user_id}, request type: {request_type}")
            return True
        
        except Exception as e:
            logger.error(f"Error executing data deletion: {e}")
            
            # Update the deletion request status
            cursor.execute(
                """
                UPDATE data_deletion_requests
                SET status = ?, notes = ?
                WHERE id = ?
                """,
                ("failed", str(e), request_id)
            )
            
            conn.commit()
            return False
    
    def log_data_access(self, data_type: str, accessed_by: str, access_reason: str, user_id: Optional[str] = None, ip_address: Optional[str] = None) -> int:
        """Log access to user data.
        
        Args:
            data_type: The type of data accessed
            accessed_by: The ID of the user or system that accessed the data
            access_reason: The reason for accessing the data
            user_id: The ID of the user whose data was accessed (optional)
            ip_address: The IP address of the accessor (optional)
            
        Returns:
            The ID of the created access log
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO data_access_log (
                data_type, user_id, accessed_by, access_reason, access_timestamp, ip_address
            )
            VALUES (?, ?, ?, ?, datetime('now'), ?)
            """,
            (data_type, user_id, accessed_by, access_reason, ip_address)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


# Create a singleton instance
db_service = DatabaseService()