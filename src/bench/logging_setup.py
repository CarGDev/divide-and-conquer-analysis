"""Logging configuration for benchmarks."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
import platform


def setup_logging(
    log_dir: Path,
    log_level: str = "INFO",
    log_file: str = "bench.log",
) -> None:
    """
    Configure logging to both console and rotating file.
    
    Args:
        log_dir: Directory to write log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Name of the log file
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setLevel(numeric_level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Log system information
    logger.info("=" * 80)
    logger.info("Benchmark session started")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.machine()}")
    
    # Try to get git commit if available
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            logger.info(f"Git commit: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    logger.info("=" * 80)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to calling module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

