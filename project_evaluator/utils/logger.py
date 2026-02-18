"""
Logging utility module for the AI Project Auto-Evaluator.

Provides centralized logging configuration with support for
console and file logging with rich formatting.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


class Logger:
    """
    Centralized logger with rich terminal output.
    
    Follows singleton pattern to ensure consistent logging
    across all modules.
    """
    
    _instance: Optional['Logger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Logger':
        """Ensure only one logger instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 name: str = "project_evaluator",
                 level: int = logging.INFO,
                 log_file: Optional[Path] = None):
        """
        Initialize the logger (only once).
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for file logging
        """
        if self._initialized:
            return
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()  # Clear existing handlers
        
        # Console handler with rich formatting
        console_handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_path=False
        )
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self._initialized = True
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            logging.Logger: Configured logger
        """
        return self.logger
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)


def get_logger(name: Optional[str] = None,
               level: int = logging.INFO,
               log_file: Optional[Path] = None) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name (defaults to "project_evaluator")
        level: Logging level
        log_file: Optional file path for file logging
    
    Returns:
        logging.Logger: Configured logger
    
    Example:
        >>> logger = get_logger()
        >>> logger.info("Starting analysis...")
    """
    logger_instance = Logger(
        name=name or "project_evaluator",
        level=level,
        log_file=log_file
    )
    return logger_instance.get_logger()


# Convenience function for quick logging
def log_section(title: str, console: Optional[Console] = None) -> None:
    """
    Log a section header with rich formatting.
    
    Args:
        title: Section title
        console: Optional Rich Console instance
    """
    if console is None:
        console = Console()
    
    console.rule(f"[bold blue]{title}[/bold blue]")
