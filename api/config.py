import logging
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)
ERROR_COUNT = Counter("app_errors_total", "Total number of errors", ["endpoint"])
CHARACTER_QUERY_COUNT = Counter(
    "app_characters_returned_total",
    "Total number of characters returned from the /characters endpoint",
)

EXCLUDED_PATHS = {"/metrics", "/health"}


def setup_metrics(app):
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        endpoint = request.url.path
        if endpoint in EXCLUDED_PATHS:
            return await call_next(request)

        method = request.method
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            ERROR_COUNT.labels(endpoint=endpoint).inc()
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, http_status=status_code
            ).inc()

        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _configure_logging(name: str) -> logging.Logger:
    """
    Configure logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(name)
    return logger
