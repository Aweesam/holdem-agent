#!/usr/bin/env python3
"""
Centralized logging configuration for the holdem project.
Provides rotating file handlers and structured JSON logging.
"""

import logging
import logging.handlers
import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                              'relativeCreated', 'thread', 'threadName', 'processName', 
                              'process', 'message', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        colored_record = logging.makeLogRecord(record.__dict__)
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        colored_record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(colored_record)


def ensure_log_directories():
    """Ensure all required log directories exist."""
    base_log_dir = Path(__file__).parent.parent.parent.parent / 'logs'
    
    log_dirs = [
        base_log_dir,
        base_log_dir / 'api',
        base_log_dir / 'agent', 
        base_log_dir / 'dashboard',
        base_log_dir / 'holdemctl'
    ]
    
    for log_dir in log_dirs:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    return base_log_dir


def setup_logger(
    name: str,
    service_type: str,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        service_type: Service type (api, agent, dashboard, holdemctl)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' for structured logs, 'standard' for human-readable)
        log_file: Custom log file name (defaults to service_type.log)
    
    Returns:
        Configured logger instance
    """
    # Get configuration from environment or defaults
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = log_format or os.getenv('LOG_FORMAT', 'standard').lower()
    
    # Ensure log directories exist
    base_log_dir = ensure_log_directories()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Setup file handler with rotation
    if not log_file:
        log_file = f"{service_type}.log"
    
    file_path = base_log_dir / service_type / log_file
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    
    # Setup console handler  
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Configure formatters based on log format preference
    if log_format == 'json':
        file_formatter = JSONFormatter()
        # Console still gets human-readable format even with JSON file format
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_log_file_path(service_type: str, log_file: str = None) -> Path:
    """Get the path to a service's log file."""
    base_log_dir = ensure_log_directories()
    if not log_file:
        log_file = f"{service_type}.log"
    return base_log_dir / service_type / log_file


def setup_exception_logging(logger: logging.Logger):
    """Setup global exception handler to log uncaught exceptions."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow KeyboardInterrupt to pass through normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Also log to console for visibility
        print(f"\n🔴 FATAL ERROR: {exc_type.__name__}: {exc_value}")
        print("Check the log files for full details.")
        
        # Call the default handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception