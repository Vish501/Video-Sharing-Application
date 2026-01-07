"""
Constructs a logger to track issues.
"""

import os
import sys
import logging

# Log message format
LOG_FORMAT = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

def get_logger(log_type: str = "running") -> logging.Logger:
    """
    Returns a configured logger that writes to either running_logs.log or test_logs.log.

    Parameters:
    - log_type (str): "running" or "test", defaults to "running".

    Returns:
    - logging.Logger: Configured logger instance.
    """ 
    log_name = f"VideoSharingApp_{'running' if log_type.lower() == 'running' else 'test'}"
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create logs directory if it doesn't exist
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_filename = "running_logs.log" if log_type == "running" else "test_logs.log"
    log_path = os.path.join(log_dir, log_filename)

    # File handlers
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Stream handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


if __name__ == "__main__":
    logger = get_logger("running")
    logger.info(f"Initalizing and testing logger")

    logger = get_logger("test")
    logger.info(f"Initalizing and testing logger")   
    