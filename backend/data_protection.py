import os
import json
import logging
import shutil
from datetime import datetime, timezone, timedelta
import schedule
import time
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProtectionManager:
    """
    Manages data protection tasks including:
    - Automated data retention enforcement
    - Data protection impact assessment
    - Data processing records
    """
    
    def __init__(self):
        self.conversations_dir = os.path.join("data", "conversations")
        self.logs_dir = os.path.join("logs")
        self.reports_dir = os.path.join("reports", "data_protection")
        
        # Create necessary directories
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def cleanup_expired_data(self):
        """
        Remove data that has exceeded its retention period.
        This implements the storage limitation principle of GDPR.
        """
        logger.info("Starting scheduled data cleanup")
        now = datetime.now(timezone.utc)
        expired_count = 0
        
        # Clean up conversation files
        if os.path.exists(self.conversations_dir):
            for year_month_dir in os.listdir(self.conversations_dir):
                year_month_path = os.path.join(self.conversations_dir, year_month_dir)
                if os.path.isdir(year_month_path):
                    for filename in os.listdir(year_month_path):
                        if filename.endswith('.json'):
                            file_path = os.path.join(year_month_path, filename)
                            try:
                                with open(file_path, "r") as f:
                                    data = json.load(f)
                                
                                # Check if conversation has retention date
                                if "gdpr_metadata" in data and "retention_date" in data["gdpr_metadata"]:
                                    retention_date = datetime.fromisoformat(data["gdpr_metadata"]["retention_date"])
                                    if now > retention_date:
                                        logger.info(f"Deleting expired conversation: {filename}")
                                        os.remove(file_path)
                                        expired_count += 1
                            except (json.JSONDecodeError, IOError) as e:
                                logger.error(f"Error processing file {file_path}: {str(e)}")
        
        # Clean up log files
        if os.path.exists(self.logs_dir):
            for service_dir in os.listdir(self.logs_dir):
                service_path = os.path.join(self.logs_dir, service_dir)
                if os.path.isdir(service_path):
                    for year_month_dir in os.listdir(service_path):
                        year_month_path = os.path.join(service_path, year_month_dir)
                        if os.path.isdir(year_month_path):
                            for filename in os.listdir(year_month_path):
                                if filename.endswith('.jsonl') or filename.endswith('.json'):
                                    file_path = os.path.join(year_month_path, filename)
                                    
                                    # Check file age - logs older than 90 days are removed
                                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
                                    if (now - file_time).days > 90:
                                        logger.info(f"Deleting expired log file: {filename}")
                                        os.remove(file_path)
                                        expired_count += 1
        
        # Clean up empty directories
        self._cleanup_empty_directories(self.conversations_dir)
        self._cleanup_empty_directories(self.logs_dir)
        
        logger.info(f"Data cleanup completed. Removed {expired_count} expired items.")
        
        # Record the cleanup activity
        self._record_data_processing_activity("data_cleanup", {
            "expired_items_removed": expired_count,
            "timestamp": now.isoformat()
        })
        
        return expired_count
    
    def _cleanup_empty_directories(self, root_dir):
        """Remove empty directories recursively"""
        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
            if not dirnames and not filenames and dirpath != root_dir:
                try:
                    os.rmdir(dirpath)
                    logger.info(f"Removed empty directory: {dirpath}")
                except OSError:
                    pass
    
    def perform_data_protection_assessment(self):
        """
        Perform automated Data Protection Impact Assessment (DPIA).
        This helps identify and minimize data protection risks.
        """
        logger.info("Starting data protection assessment")
        now = datetime.now(timezone.utc)
        
        assessment = {
            "timestamp": now.isoformat(),
            "data_inventory": self._count_stored_data(),
            "retention_compliance": self._check_retention_compliance(),
            "anonymization_effectiveness": self._test_anonymization_effectiveness(),
            "risk_score": 0,
            "recommendations": []
        }
        
        # Calculate risk score based on findings
        if assessment["data_inventory"]["total_conversations"] > 1000:
            assessment["risk_score"] += 10
            assessment["recommendations"].append("Large volume of data - consider additional security measures")
        
        if assessment["retention_compliance"]["expired_files"] > 0:
            assessment["risk_score"] += 20
            assessment["recommendations"].append("Expired data found - run cleanup immediately")
        
        # Save assessment report
        report_file = os.path.join(self.reports_dir, f"dpia_{now.strftime('%Y%m%d')}.json")
        with open(report_file, "w") as f:
            json.dump(assessment, f, indent=2)
        
        logger.info(f"Data protection assessment completed. Risk score: {assessment['risk_score']}")
        return assessment
    
    def _count_stored_data(self):
        """Count the amount of stored data"""
        result = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_log_files": 0,
            "oldest_data": None
        }
        
        oldest_timestamp = None
        
        # Count conversations and messages
        if os.path.exists(self.conversations_dir):
            for year_month_dir in os.listdir(self.conversations_dir):
                year_month_path = os.path.join(self.conversations_dir, year_month_dir)
                if os.path.isdir(year_month_path):
                    for filename in os.listdir(year_month_path):
                        if filename.endswith('.json'):
                            result["total_conversations"] += 1
                            file_path = os.path.join(year_month_path, filename)
                            
                            try:
                                with open(file_path, "r") as f:
                                    data = json.load(f)
                                
                                # Count messages
                                if "messages" in data:
                                    result["total_messages"] += len(data["messages"])
                                
                                # Check timestamp
                                if "gdpr_metadata" in data and "creation_date" in data["gdpr_metadata"]:
                                    timestamp = datetime.fromisoformat(data["gdpr_metadata"]["creation_date"])
                                    if oldest_timestamp is None or timestamp < oldest_timestamp:
                                        oldest_timestamp = timestamp
                            except (json.JSONDecodeError, IOError):
                                pass
        
        # Count log files
        if os.path.exists(self.logs_dir):
            for root, _, files in os.walk(self.logs_dir):
                for filename in files:
                    if filename.endswith('.jsonl') or filename.endswith('.json'):
                        result["total_log_files"] += 1
        
        if oldest_timestamp:
            result["oldest_data"] = oldest_timestamp.isoformat()
        
        return result
    
    def _check_retention_compliance(self):
        """Check if any data has exceeded its retention period"""
        now = datetime.now(timezone.utc)
        result = {
            "expired_files": 0,
            "expiring_soon": 0,  # Files expiring in the next 7 days
            "compliant_files": 0
        }
        
        # Check conversations
        if os.path.exists(self.conversations_dir):
            for year_month_dir in os.listdir(self.conversations_dir):
                year_month_path = os.path.join(self.conversations_dir, year_month_dir)
                if os.path.isdir(year_month_path):
                    for filename in os.listdir(year_month_path):
                        if filename.endswith('.json'):
                            file_path = os.path.join(year_month_path, filename)
                            
                            try:
                                with open(file_path, "r") as f:
                                    data = json.load(f)
                                
                                # Check retention date
                                if "gdpr_metadata" in data and "retention_date" in data["gdpr_metadata"]:
                                    retention_date = datetime.fromisoformat(data["gdpr_metadata"]["retention_date"])
                                    if now > retention_date:
                                        result["expired_files"] += 1
                                    elif (retention_date - now).days <= 7:
                                        result["expiring_soon"] += 1
                                    else:
                                        result["compliant_files"] += 1
                                else:
                                    # No retention date specified
                                    result["expired_files"] += 1
                            except (json.JSONDecodeError, IOError):
                                # Corrupted files should be considered expired
                                result["expired_files"] += 1
        
        return result
    
    def _test_anonymization_effectiveness(self):
        """Test the effectiveness of the anonymization process"""
        # This is a simplified test - in a real system, you would use more sophisticated methods
        test_cases = [
            "My phone number is 555-123-4567",
            "Please charge it to my credit card 4111-1111-1111-1111",
            "I'm staying in room 302",
            "My email is john.doe@example.com",
            "My name is Mr. Smith"
        ]
        
        from backend.ai_agents.conversation_memory import ConversationMemory
        memory = ConversationMemory()
        
        results = {
            "total_tests": len(test_cases),
            "successful_anonymizations": 0,
            "failed_anonymizations": 0,
            "examples": []
        }
        
        for test in test_cases:
            anonymized = memory._anonymize_personal_data(test)
            success = test != anonymized
            
            results["examples"].append({
                "original": test,
                "anonymized": anonymized,
                "success": success
            })
            
            if success:
                results["successful_anonymizations"] += 1
            else:
                results["failed_anonymizations"] += 1
        
        return results
    
    def _record_data_processing_activity(self, activity_type, details):
        """Record data processing activities for GDPR Article 30 compliance"""
        now = datetime.now(timezone.utc)
        
        record = {
            "activity_type": activity_type,
            "timestamp": now.isoformat(),
            "details": details,
            "data_controller": "Hotel AI System",
            "purpose": "GDPR Compliance",
            "categories_of_data": ["conversation data", "user messages", "system logs"]
        }
        
        # Save the record
        record_dir = os.path.join(self.reports_dir, "processing_activities")
        os.makedirs(record_dir, exist_ok=True)
        
        record_file = os.path.join(record_dir, f"activity_log_{now.strftime('%Y%m')}.jsonl")
        
        with open(record_file, "a") as f:
            json.dump(record, f)
            f.write("\n")

# Singleton instance
data_protection_manager = DataProtectionManager()

def start_scheduled_tasks():
    """Start scheduled data protection tasks"""
    # Schedule daily data cleanup at 3 AM
    schedule.every().day.at("03:00").do(data_protection_manager.cleanup_expired_data)
    
    # Schedule weekly data protection assessment on Sundays at 4 AM
    schedule.every().sunday.at("04:00").do(data_protection_manager.perform_data_protection_assessment)
    
    # Run the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("Data protection scheduled tasks started")

# Run an initial data cleanup when the module is imported
def run_initial_cleanup():
    """Run an initial data cleanup when the system starts"""
    try:
        expired_count = data_protection_manager.cleanup_expired_data()
        logger.info(f"Initial data cleanup completed. Removed {expired_count} expired items.")
    except Exception as e:
        logger.error(f"Error during initial data cleanup: {str(e)}")

if __name__ == "__main__":
    # This allows running the script directly for manual cleanup
    run_initial_cleanup()
    data_protection_manager.perform_data_protection_assessment()