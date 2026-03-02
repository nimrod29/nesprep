"""FastAPI app and uvicorn entry point for the WebSocket agent service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent_websocket.routers import websocket
from app.config import settings
from app.dal.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Create database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NesPrep Shift Planning Agent",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(websocket.router)


def main() -> None:
    """Run the WebSocket server."""
    import uvicorn

    uvicorn.run(
        "app.agent_websocket.main:app",
        host="0.0.0.0",
        port=settings.WEBSOCKET_PORT,
        reload=False,
    )
