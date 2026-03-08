import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .database import engine
from .models import Base
from .quip_api.router import router as quip_router
from .sharepoint_api.router import router as sp_router
from .websocket.yjs_handler import websocket_server, start_yjs, stop_yjs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_yjs_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _yjs_task
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
    logger.info("Database initialized")

    # Start Yjs server as background task (start() blocks until stopped)
    _yjs_task = asyncio.create_task(start_yjs())
    logger.info("Yjs server started")

    yield

    # Shutdown
    await stop_yjs()
    if _yjs_task:
        _yjs_task.cancel()


app = FastAPI(title="Quip-SharePoint", version="0.1.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(quip_router)
app.include_router(sp_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Yjs collaborative editing WebSocket
@app.websocket("/ws/yjs/{document_id}")
async def ws_yjs(websocket: WebSocket, document_id: str):
    """Handle Yjs sync protocol for collaborative editing."""
    await websocket.accept()
    room = websocket_server.get_room(document_id)
    # Wrap FastAPI WebSocket for pycrdt-websocket compatibility
    ws = _FastAPIWebsocketAdapter(websocket, document_id)
    try:
        await websocket_server.serve(ws)
    except Exception as e:
        logger.debug(f"Yjs WS closed: doc={document_id}, reason={e}")


class _FastAPIWebsocketAdapter:
    """Adapt FastAPI WebSocket to pycrdt-websocket Channel interface."""

    def __init__(self, websocket: WebSocket, path: str):
        self._ws = websocket
        self._path = path

    @property
    def path(self) -> str:
        return self._path

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        try:
            return await self._ws.receive_bytes()
        except (WebSocketDisconnect, Exception):
            raise StopAsyncIteration

    async def send(self, message: bytes):
        await self._ws.send_bytes(message)

    async def recv(self) -> bytes:
        return await self._ws.receive_bytes()


# Serve frontend static files (production: built frontend in /app/static)
_static_dir = Path(__file__).resolve().parent.parent.parent / "static"
if _static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve SPA - return index.html for all non-API routes."""
        file_path = _static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_static_dir / "index.html"))
