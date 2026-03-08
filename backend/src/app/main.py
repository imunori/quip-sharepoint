import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .database import engine
from .models import Base
from .quip_api.router import router as quip_router
from .sharepoint_api.router import router as sp_router
from .websocket.manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
    logger.info("Database initialized")
    yield


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


# WebSocket for collaborative editing
@app.websocket("/ws/document/{document_id}")
async def ws_document(websocket: WebSocket, document_id: str):
    await manager.connect(document_id, websocket)
    logger.info(f"WS connected: doc={document_id}, total={manager.get_connection_count(document_id)}")
    try:
        while True:
            data = await websocket.receive_bytes()
            # Broadcast Yjs update to all other clients
            await manager.broadcast(document_id, data, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(document_id, websocket)
        logger.info(f"WS disconnected: doc={document_id}")
    except Exception as e:
        manager.disconnect(document_id, websocket)
        logger.error(f"WS error: {e}")


# WebSocket for presence (cursors, online status)
@app.websocket("/ws/presence/{document_id}")
async def ws_presence(websocket: WebSocket, document_id: str):
    await manager.connect(f"presence-{document_id}", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_json(
                f"presence-{document_id}",
                {"type": "presence", "data": data},
                exclude=websocket,
            )
    except WebSocketDisconnect:
        manager.disconnect(f"presence-{document_id}", websocket)
    except Exception:
        manager.disconnect(f"presence-{document_id}", websocket)
