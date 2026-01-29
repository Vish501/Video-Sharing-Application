from fastapi import FastAPI

from VideoSharingApp.schemas import UserRead, UserCreate, UserUpdate
from VideoSharingApp.users import auth_backend_v1, fastapi_users

from VideoSharingApp.core.lifespan import lifespan
from VideoSharingApp.routers import health          # Validates if a connection has been made to the API (debug)
from VideoSharingApp.routers.v1 import posts, feed
from VideoSharingApp.constants.auth import AuthPaths, APIVersion

from VideoSharingApp.database import get_engine
from VideoSharingApp.utils.logger import setup_logger, get_logger
from VideoSharingApp.utils.logging_context import LoggingContextMiddleware
from VideoSharingApp.observability.otel import setup_tracing

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Setting up Observability and logging
setup_logger()
setup_tracing()

# Initalizing Application after Observability
app = FastAPI(lifespan=lifespan)

# Adding middleware context to logging
app.add_middleware(LoggingContextMiddleware)

# Setting up additional Instrumentors for observability
if not FastAPIInstrumentor().is_instrumented_by_opentelemetry:
    FastAPIInstrumentor.instrument_app(app)

SQLAlchemyInstrumentor().instrument(engine=get_engine().sync_engine)
LoggingInstrumentor().instrument(set_logging_format=False)

logger = get_logger(__name__)

# Connecting auth endpoints
base_prefix = AuthPaths.base_prefix(APIVersion.V1)    #/api/v1
auth_prefix = AuthPaths.router_prefix(APIVersion.V1)    #/api/v1/auth
user_prefix = AuthPaths.user_prefix(APIVersion.V1)      #/api/v1/users

app.include_router(fastapi_users.get_auth_router(auth_backend_v1), prefix=auth_prefix, tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix=auth_prefix, tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix=auth_prefix, tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix=auth_prefix, tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix=user_prefix, tags=["users"])

# --- V1 API ---
app.include_router(health.router)
app.include_router(posts.router, prefix=base_prefix)
app.include_router(feed.router, prefix=base_prefix)
