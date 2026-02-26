from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, scan_id: str):
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)
        logger.info(f"Client connected to scan {scan_id}. Total connections: {len(self.active_connections[scan_id])}")

    def disconnect(self, websocket: WebSocket, scan_id: str):
        if scan_id in self.active_connections:
            if websocket in self.active_connections[scan_id]:
                self.active_connections[scan_id].remove(websocket)
                logger.info(f"Client disconnected from scan {scan_id}. Remaining: {len(self.active_connections[scan_id])}")
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]

    async def send_to_scan(self, scan_id: str, message: dict):
        if scan_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[scan_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected.append(websocket)
            for ws in disconnected:
                self.disconnect(ws, scan_id)

    def get_connection_count(self, scan_id: str) -> int:
        return len(self.active_connections.get(scan_id, []))


manager = ConnectionManager()
