from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

import contextvars

# Async-safe request scoped values
trace_id_ctx = contextvars.ContextVar("trace_id", default="N/A")
user_id_ctx = contextvars.ContextVar("user_id", default="anonymous")


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects request-scoped metadata into contextvars.

    - trace_id comes from headers (or can be generated later)
    - user_id is pulled from request.state after authentication, or headers as a backup

    ContextVars ensure correctness across async tasks.
    """
    async def dispatch(self, request: Request, call_next):
        # Trace ID (from gateway, load balancer, or test client)
        trace_id = request.headers.get("x-trace-id", "N/A")
        
        # User is attached by auth dependency
        user = getattr(request.state, "user", None)
        user_id = getattr(user, "id", None) if user else request.headers.get("x-user-id", "anonymous")

        # Store in async-safe context
        trace_token = trace_id_ctx.set(trace_id)
        user_token = user_id_ctx.set(str(user_id))

        try:
            response = await call_next(request)
            return response
        finally:
            # Prevent context leakage across requests
            trace_id_ctx.reset(trace_token)
            user_id_ctx.reset(user_token)
            