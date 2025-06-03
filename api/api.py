from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from typing import Literal
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from api.db import RedisManager, PostgreManager

load_dotenv()

app = FastAPI(title="Character API")

# Configure Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize managers
redis_manager = RedisManager()
postgres_manager = PostgreManager()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)
ERROR_COUNT = Counter("app_errors_total", "Total number of errors", ["endpoint"])


# Middleware to track metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    method = request.method

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


# Prometheus metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
@limiter.limit("5/minute")
async def health_check(request: Request):
    db_ok = postgres_manager.check_connection()
    redis_ok = redis_manager.check_connection()

    if not db_ok or not redis_ok:
        raise HTTPException(
            status_code=503,
            detail={
                "db": "ok" if db_ok else "unreachable",
                "cache": "ok" if redis_ok else "unreachable",
            },
        )

    return {"db": "ok", "cache": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/characters")
@limiter.limit("10/minute")
async def get_characters(
    request: Request,
    sort: Literal["asc", "desc"] = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    characters = postgres_manager.fetch_all_characters(
        sort=sort, page=page, limit=limit
    )
    return characters
