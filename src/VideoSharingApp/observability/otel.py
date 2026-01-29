from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor, ConsoleSpanExporter

import os
from dotenv import load_dotenv
from VideoSharingApp.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

SERVICE_NAME = "video-sharing-app"

def setup_tracing() -> None:
    """
    Initialize OpenTelmetry tracing for the application.

    This should be called ONCE during application startup.
    """
    logger.info("Setting up OpenTelementry Tracing...")

    # Create service identity
    resource = Resource.create({"service.name": SERVICE_NAME})

    # Setup tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Setup and add span exporter (stdout/console for now)
    span_exporter = ConsoleSpanExporter()

    if os.environ.get("STAGE") == "test":
        span_processor = SimpleSpanProcessor(span_exporter)
        logger.info("Using `SimpleSpanProcessor` due to environment flag")
    else:
        span_processor = BatchSpanProcessor(span_exporter)
        logger.info("Using `BatchSpanProcessor` due to environment flag")

    tracer_provider.add_span_processor(span_processor)

    logger.info("OpenTelementry Tracing setup completed...")
