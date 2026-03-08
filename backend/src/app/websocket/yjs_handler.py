"""
Yjs WebSocket handler integrated with FastAPI.

Uses pycrdt for Yjs sync protocol + SQLite persistence.
"""
import logging

from pycrdt.websocket import WebsocketServer
from pycrdt.store import SQLiteYStore

from ..config import DATA_DIR

logger = logging.getLogger(__name__)

# Persistent Yjs store
ystore = SQLiteYStore(path=str(DATA_DIR / "yjs.db"))

# WebSocket server managing rooms per document
websocket_server = WebsocketServer(auto_clean_rooms=True)


async def start_yjs():
    """Initialize Yjs server and store."""
    await websocket_server.start()
    logger.info("Yjs WebSocket server started")


async def stop_yjs():
    """Shutdown Yjs server."""
    await websocket_server.stop()
    logger.info("Yjs WebSocket server stopped")
