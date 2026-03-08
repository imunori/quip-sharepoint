import json
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections per document."""

    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, document_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[document_id].append(websocket)

    def disconnect(self, document_id: str, websocket: WebSocket):
        self.connections[document_id].remove(websocket)
        if not self.connections[document_id]:
            del self.connections[document_id]

    async def broadcast(self, document_id: str, data: bytes, exclude: WebSocket | None = None):
        for ws in self.connections.get(document_id, []):
            if ws != exclude:
                try:
                    await ws.send_bytes(data)
                except Exception:
                    pass

    async def broadcast_json(self, document_id: str, data: dict, exclude: WebSocket | None = None):
        for ws in self.connections.get(document_id, []):
            if ws != exclude:
                try:
                    await ws.send_json(data)
                except Exception:
                    pass

    def get_connection_count(self, document_id: str) -> int:
        return len(self.connections.get(document_id, []))


manager = ConnectionManager()
