"""
Central logging configuration
"""
import os
import logging

from pathlib import Path
from dotenv import load_dotenv

from VideoSharingApp.utils.logging_filter import ContextFilter, RedactionFilter
from VideoSharingApp.utils.logging_formatter import JSONFormatter, OTelSafeFormatter

load_dotenv()

# Log message format
LOG_FORMAT = (
    "[%(asctime)s | %(levelname)s | %(module)s | "
    "user=%(user_id)s | trace_id=%(otelTraceID)s span_id=%(otelSpanID)s | %(message)s]"
)

# Global check if logger has been created
_LOGGING_INITIALIZED = False


def is_path_related(base_dir, current_file):
    """
    Check if both paths provided have a common ancestor
    """
    base = Path(base_dir).resolve()
    curr = Path(current_file).resolve()
    return (base in curr.parents) or (curr.parents in base)


def _create_logger() -> logging.Logger:
    """
    Configure root logging once for the entire app.
    """
    stage = os.getenv("STAGE", "test")

    # Getting working directory
    root_dir = os.getenv("WORKING_DIRECTORY").strip() or None
    if not root_dir or not os.path.isdir(root_dir) or not is_path_related(root_dir, os.path.dirname(__file__)):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    # Create the main logging directory if it does not exist
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Initialize logger and level
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Set propogation to false, in order to prevent double logging
    logger.propagate = False

    # Grab all the content filters
    # Prevent passwords or other sensitive information from being logger
    filters = [ContextFilter(), RedactionFilter()]

    # Add json related logging handlers
    if os.getenv("LOG_JSON_ENABLED", "true").strip().lower() == "true":
        json_log = os.path.join(log_dir, f"{stage}.json.log")
        json_handler = logging.FileHandler(json_log, encoding="utf-8")
        json_handler.setFormatter(JSONFormatter())
        for log_filter in filters:
            json_handler.addFilter(log_filter)
        logger.addHandler(json_handler)

    # Add text related logging handlers
    if os.getenv("LOG_TEXT_ENABLED", "true").strip().lower() == "true":
        text_log = os.path.join(log_dir, f"{stage}.text.log")
        text_handler = logging.FileHandler(text_log, encoding="utf-8")
        text_handler.setFormatter(OTelSafeFormatter(LOG_FORMAT))
        for log_filter in filters:
            text_handler.addFilter(log_filter)
        logger.addHandler(text_handler)

    # Adding console logging if enabled
    if os.getenv("LOG_CONSOLE_ENABLED", "false").strip().lower() == "true":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(OTelSafeFormatter(LOG_FORMAT))
        logger.addHandler(console_handler)


def setup_logger() -> None:
    global _LOGGING_INITIALIZED

    if _LOGGING_INITIALIZED:
        return
    _create_logger()

    _LOGGING_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """
    Get module-specific logger (inherits root handlers)
    """
    setup_logger()
    return logging.getLogger(name)


if __name__ == "__main__":
    logger = get_logger("running")
    logger.info(f"Initalizing and testing logger")

    logger = get_logger("test")
    logger.info(f"Initalizing and testing logger")   
    