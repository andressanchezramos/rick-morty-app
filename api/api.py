from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from typing import Literal

from api.db import RedisManager, PostgreManager
from api.config import setup_metrics
from api.config import CHARACTER_QUERY_COUNT


load_dotenv()

app = FastAPI(title="Character API")


# Setup Prometheus metrics
setup_metrics(app)

# Configure Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize DB managers
redis_manager = RedisManager()
postgres_manager = PostgreManager()


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

    characters_list = characters.get("results", [])
    CHARACTER_QUERY_COUNT.inc(len(characters_list))

    return characters
