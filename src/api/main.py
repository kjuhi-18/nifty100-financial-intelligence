
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    health,
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
)

app = FastAPI(
    title="N100 Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()

    response = await call_next(request)

    elapsed = time.time() - start

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"{elapsed:.3f}s"
    )

    return response


app.include_router(
    health.router,
    prefix="/api/v1"
)

app.include_router(
    companies.router,
    prefix="/api/v1"
)

app.include_router(
    screener.router,
    prefix="/api/v1"
)

app.include_router(
    sectors.router,
    prefix="/api/v1"
)

app.include_router(
    peers.router,
    prefix="/api/v1"
)

app.include_router(
    valuation.router,
    prefix="/api/v1"
)

app.include_router(
    portfolio.router,
    prefix="/api/v1"
)

app.include_router(
    documents.router,
    prefix="/api/v1"
)