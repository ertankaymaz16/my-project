"""
Advanced logging system with color support and file rotation
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorlog


class BotLogger:
    """Centralized logging system for the visa bot"""
    
    def __init__(self, name: str = "VisaBot", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation (10MB max, 5 backups)
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Debug level log"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Info level log"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Warning level log"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Error level log"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Critical level log"""
        self.logger.critical(message, exc_info=exc_info)
    
    def phase(self, phase_name: str, message: str):
        """Log phase transitions"""
        self.logger.info(f"🔹 [{phase_name}] {message}")
    
    def success(self, message: str):
        """Log success messages"""
        self.logger.info(f"✅ {message}")
    
    def failure(self, message: str):
        """Log failure messages"""
        self.logger.error(f"❌ {message}")


# Global logger instance
logger = BotLogger()
