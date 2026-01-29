import logging
import re

from VideoSharingApp.utils.logging_context import trace_id_ctx, user_id_ctx

class ContextFilter(logging.Filter):
    """
    Enrich every log record with request-scoped metadata.

    This runs inside the logging system — not inside FastAPI —
    so logs from background tasks and deep libraries still get context.
    """
    def filter(self, record):
        # Pull current async context values
        record.trace_id = trace_id_ctx.get() or "N/A"
        record.user_id = user_id_ctx.get() or "anonymous"

        return True

class RedactionFilter(logging.Filter):
    """
    Scrubs sensitive values from log messages before they are written.

    This prevents accidental leakage of:
    - passwords
    - auth tokens
    - authorization headers

    IMPORTANT:
    This runs at logging time, so even deep library logs are sanitized.
    """
    # Matches:
    # password=secret
    # "password": "secret"
    # 'password': 'secret'
    # token=..., authorization: ...
    PATTERNS = [
        r'("password"\s*:\s*")[^"]+(")',
        r"('password'\s*:\s*')[^']+(')",
        r"(password\s*=\s*)(\S+)",

        r'("token"\s*:\s*")[^"]+(")',
        r"('token'\s*:\s*')[^']+(')",
        r"(token\s*=\s*)(\S+)",

        r"(authorization:\s*)(\S+)",
    ]

    def filter(self, record):
        """
        Intercepts the log message and replaces sensitive values with placeholders.

        Runs on every log record before formatting and output.
        """
        # Get the fully rendered message (not raw format string)
        msg = record.getMessage()
        
        # Apply redaction for each known sensitive pattern
        for p in self.PATTERNS:
            msg = re.sub(p, r"\1***REDACTED***", msg, flags=re.IGNORECASE)

        # Replace message on the record so formatters see the cleaned version
        record.msg = msg

        # Clear args to avoid re-formatting with original sensitive values
        record.args = ()

        return True
    