"""Main FastAPI app combining REST API and WebSocket endpoints."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent_websocket.routers import websocket
from app.api.routers import auth_router, sessions_router
from app.dal.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NesPrep Shift Planning",
    description="AI-powered shift planning with chat interface",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routes
app.include_router(auth_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")

# WebSocket route
app.include_router(websocket.router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


def main() -> None:
    """Run the server."""
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
