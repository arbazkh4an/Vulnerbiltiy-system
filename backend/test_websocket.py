import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConnectionManager:
    @pytest.mark.asyncio
    async def test_connect_adds_websocket(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        ws = MagicMock()
        ws.accept = AsyncMock()
        
        await manager.connect(ws, "scan-123")
        
        assert "scan-123" in manager.active_connections
        assert ws in manager.active_connections["scan-123"]
        ws.accept.assert_called_once()

    def test_disconnect_removes_websocket(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        ws = MagicMock()
        manager.active_connections["scan-123"] = [ws]
        
        manager.disconnect(ws, "scan-123")
        
        assert "scan-123" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_send_to_scan_sends_to_all_clients(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        manager.active_connections["scan-123"] = [ws1, ws2]
        
        message = {"type": "progress", "message": "test"}
        
        await manager.send_to_scan("scan-123", message)
        
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    def test_get_connection_count(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        ws1 = MagicMock()
        ws2 = MagicMock()
        manager.active_connections["scan-123"] = [ws1, ws2]
        
        count = manager.get_connection_count("scan-123")
        
        assert count == 2

    def test_disconnect_cleans_empty_scan_id(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        ws = MagicMock()
        manager.active_connections["scan-123"] = [ws]
        
        manager.disconnect(ws, "scan-123")
        
        assert "scan-123" not in manager.active_connections


class TestWebSocketEndpoint:
    @pytest.mark.asyncio
    async def test_invalid_scan_id_connection_closes(self):
        with patch('backend.websocket.validate_scan_exists', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = None
            
            from backend.websocket import websocket_endpoint
            from fastapi import WebSocket
            
            mock_ws = AsyncMock(spec=WebSocket)
            mock_ws.close = AsyncMock()
            
            await websocket_endpoint(mock_ws, "invalid-scan-id")
            
            mock_ws.close.assert_called_once_with(code=4004, reason="Scan not found")


class TestCompleteScan:
    @pytest.mark.asyncio
    async def test_complete_scan_sends_complete_message(self):
        with patch('backend.websocket.validate_scan_exists', new_callable=AsyncMock) as mock_validate, \
             patch('backend.websocket.get_scan_results', new_callable=AsyncMock) as mock_results:
            
            mock_validate.return_value = {
                'id': 'scan-123',
                'url': 'https://example.com',
                'status': 'complete'
            }
            mock_results.return_value = [
                {'scanner_name': 'header_scanner', 'raw_json': {}, 'duration_ms': 100}
            ]
            
            from backend.websocket import websocket_endpoint
            from fastapi import WebSocket
            
            mock_ws = AsyncMock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            mock_ws.close = AsyncMock()
            
            await websocket_endpoint(mock_ws, "scan-123")
            
            mock_ws.accept.assert_called_once()
            
            calls = mock_ws.send_json.call_args_list
            assert any(call[0][0].get("type") == "complete" for call in calls)


class TestMultipleClients:
    @pytest.mark.asyncio
    async def test_multiple_clients_receive_messages(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        ws1 = AsyncMock()
        ws1.accept = AsyncMock()
        ws2 = AsyncMock()
        ws2.accept = AsyncMock()
        
        await manager.connect(ws1, "scan-123")
        await manager.connect(ws2, "scan-123")
        
        assert manager.get_connection_count("scan-123") == 2
        
        await manager.send_to_scan("scan-123", {"type": "progress", "message": "test"})
        
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()


class TestClientDisconnect:
    @pytest.mark.asyncio
    async def test_disconnect_unregisters_cleanly(self):
        from backend.connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        ws = AsyncMock()
        ws.accept = AsyncMock()
        
        await manager.connect(ws, "scan-123")
        assert manager.get_connection_count("scan-123") == 1
        
        manager.disconnect(ws, "scan-123")
        assert manager.get_connection_count("scan-123") == 0


class TestRedisPubSub:
    @pytest.mark.asyncio
    async def test_redis_pubsub_context_manager(self):
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        
        mock_client = AsyncMock()
        mock_client.pubsub = AsyncMock(return_value=mock_pubsub)
        mock_client.close = AsyncMock()
        
        with patch('backend.websocket.get_redis_client', return_value=mock_client):
            from backend import websocket
            async with websocket.redis_pubsub("scan-123") as ps:
                mock_pubsub.subscribe.assert_called_with("scan_progress:scan-123")
            
            mock_pubsub.unsubscribe.assert_called_with("scan_progress:scan-123")
            mock_client.close.assert_called_once()


class TestConnectionAck:
    @pytest.mark.asyncio
    async def test_valid_scan_sends_connection_ack(self):
        with patch('backend.websocket.validate_scan_exists', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {
                'id': 'scan-123',
                'url': 'https://example.com',
                'status': 'scanning'
            }
            
            from backend.websocket import websocket_endpoint
            from fastapi import WebSocket
            
            mock_ws = AsyncMock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            mock_ws.receive_text = AsyncMock(side_effect=asyncio.CancelledError())
            mock_ws.close = AsyncMock()
            
            try:
                await websocket_endpoint(mock_ws, "scan-123")
            except asyncio.CancelledError:
                pass
            
            mock_ws.accept.assert_called_once()
            
            call_args = mock_ws.send_json.call_args_list[0][0][0]
            assert call_args["type"] == "connection_ack"
            assert call_args["scan_id"] == "scan-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--timeout=30"])
