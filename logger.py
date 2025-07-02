import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from logging.handlers import RotatingFileHandler
import asyncio

class ArielLogger:
    """Enhanced logging system for ArielMatrix"""
    
    def __init__(self, name: str = "ArielMatrix"):
        self.name = name
        self.logs = []
        self.max_memory_logs = 1000
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup the logging configuration"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, f"{self.name.lower()}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, f"{self.name.lower()}_errors.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def log(self, message: str, level: str = "INFO", metadata: Optional[Dict[str, Any]] = None):
        """Log a message with optional metadata"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {},
            "component": self.name
        }
        
        # Add to memory logs
        self.logs.append(log_entry)
        if len(self.logs) > self.max_memory_logs:
            self.logs.pop(0)  # Remove oldest log
        
        # Log to standard logger
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        if metadata:
            formatted_message = f"{message} | Metadata: {json.dumps(metadata, default=str)}"
        else:
            formatted_message = message
        
        self.logger.log(log_level, formatted_message)
    
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.log(message, "INFO", metadata)
    
    def warning(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.log(message, "WARNING", metadata)
    
    def error(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.log(message, "ERROR", metadata)
    
    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.log(message, "DEBUG", metadata)
    
    def critical(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.log(message, "CRITICAL", metadata)
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log system activity with structured data"""
        self.info(f"Activity: {activity_type}", {
            "activity_type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_performance(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        perf_metadata = {
            "operation": operation,
            "duration_seconds": duration,
            "performance_category": "timing"
        }
        
        if metadata:
            perf_metadata.update(metadata)
        
        self.info(f"Performance: {operation} completed in {duration:.3f}s", perf_metadata)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with additional context"""
        error_metadata = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.error(f"Error occurred: {str(error)}", error_metadata)
    
    def get_recent_logs(self, limit: int = 50, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent logs from memory"""
        logs = self.logs.copy()
        
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
        
        return logs[-limit:] if limit else logs
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of log statistics"""
        if not self.logs:
            return {"total_logs": 0, "message": "No logs available"}
        
        level_counts = {}
        for log in self.logs:
            level = log["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_logs": len(self.logs),
            "by_level": level_counts,
            "oldest_log": self.logs[0]["timestamp"] if self.logs else None,
            "newest_log": self.logs[-1]["timestamp"] if self.logs else None,
            "memory_usage": f"{len(self.logs)}/{self.max_memory_logs}"
        }
    
    def clear_logs(self):
        """Clear all logs from memory"""
        self.logs.clear()
        self.info("Log memory cleared")
    
    def export_logs(self, filename: Optional[str] = None) -> str:
        """Export logs to JSON file"""
        if filename is None:
            filename = f"ariel_logs_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_logs": len(self.logs),
            "logs": self.logs
        }
        
        os.makedirs("exports", exist_ok=True)
        filepath = os.path.join("exports", filename)
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.info(f"Logs exported to {filepath}")
        return filepath

class Logger:
    """Simple logger class for backward compatibility"""
    
    def __init__(self):
        self.logs = []
        self.ariel_logger = ArielLogger("SimpleLogger")

    def log(self, message: str):
        """Log a message (backward compatibility)"""
        print(f"[LOG] {message}")
        self.logs.append(message)
        self.ariel_logger.info(message)

# Global logger instances
ariel_logger = ArielLogger("ArielMatrix")
simple_logger = Logger()

# Convenience functions
def log_info(message: str, metadata: Optional[Dict[str, Any]] = None):
    """Global info logging function"""
    ariel_logger.info(message, metadata)

def log_error(message: str, metadata: Optional[Dict[str, Any]] = None):
    """Global error logging function"""
    ariel_logger.error(message, metadata)

def log_warning(message: str, metadata: Optional[Dict[str, Any]] = None):
    """Global warning logging function"""
    ariel_logger.warning(message, metadata)

def log_activity(activity_type: str, details: Dict[str, Any]):
    """Global activity logging function"""
    ariel_logger.log_activity(activity_type, details)
