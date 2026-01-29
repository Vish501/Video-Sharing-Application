import json
import logging

class JSONFormatter(logging.Formatter):
    """
    Outputs logs as structured JSON.

    Designed for:
    - ELK
    - OpenSearch
    - Datadog
    - Loki
    - Cloud logging

    Keeps logs machine-readable while preserving context.
    """
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "trace_id": getattr(record, "trace_id", None),
            "user_id": getattr(record, "user_id", None),
            "message": record.getMessage(),
        })


class OTelSafeFormatter(logging.Formatter):
    """
    Formatter wrapper that guarantees OpenTelemetry fields exist.

    Some log records (tests, startup logs, background tasks) may not
    include OTel context. Without this, formatting would raise KeyError.

    This ensures logs always render safely.
    """
    def format(self, record):
        # Inject safe defaults if OpenTelemetry has not populated them
        record.otelTraceID = getattr(record, "otelTraceID", "0")
        record.otelSpanID = getattr(record, "otelSpanID", "0")

        # Delegate to the normal formatter logic
        return super().format(record)
    