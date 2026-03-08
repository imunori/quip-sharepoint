"""
Yjs WebSocket handler using pycrdt-websocket.

Handles collaborative editing sync via Yjs protocol.
"""
import logging

from pycrdt import Doc
from pycrdt_websocket import WebsocketServer
from pycrdt_websocket.stores import SQLiteYStore

from ..config import DATA_DIR

logger = logging.getLogger(__name__)

# Yjs WebSocket server instance
yjs_server = WebsocketServer(auto_clean_rooms=True)

# SQLite-backed Yjs document store for persistence
yjs_store = SQLiteYStore(path=str(DATA_DIR / "yjs.db"))


async def start_yjs_server():
    """Start the Yjs WebSocket server."""
    await yjs_server.start()
    logger.info("Yjs WebSocket server started")


async def stop_yjs_server():
    """Stop the Yjs WebSocket server."""
    await yjs_server.stop()
    logger.info("Yjs WebSocket server stopped")
