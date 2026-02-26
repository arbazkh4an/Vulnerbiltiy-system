import json
import os
import asyncio
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

import redis.asyncio as redis
import asyncpg
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from connection_manager import manager

router = APIRouter()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://scanner:scanner@localhost:5432/scannerdb"
)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


async def get_redis_client():
    return redis.from_url(REDIS_URL, decode_responses=True)


async def validate_scan_exists(scan_id: str) -> Optional[dict]:
    try:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow(
                "SELECT id, url, status FROM scans WHERE id = $1",
                scan_id
            )
            return dict(row) if row else None
        finally:
            await conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return None


async def get_scan_results(scan_id: str) -> list:
    try:
        conn = await get_db_connection()
        try:
            rows = await conn.fetch(
                "SELECT scanner_name, raw_json, duration_ms FROM scan_results WHERE scan_id = $1",
                scan_id
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return []


@asynccontextmanager
async def redis_pubsub(scan_id: str):
    redis_client = await get_redis_client()
    pubsub = await redis_client.pubsub()
    channel_name = f"scan_progress:{scan_id}"
    await pubsub.subscribe(channel_name)
    try:
        yield pubsub
    finally:
        await pubsub.unsubscribe(channel_name)
        await redis_client.close()


async def listen_redis_messages(websocket: WebSocket, scan_id: str, task_ref: list):
    try:
        async with redis_pubsub(scan_id) as pubsub:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await websocket.send_json(data)
                        if data.get("type") == "complete" or data.get("type") == "error":
                            break
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid message format"
                        })
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Redis listener error: {e}")
    finally:
        task_ref[0] = None


@router.websocket("/ws/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    scan = await validate_scan_exists(scan_id)
    
    if not scan:
        await websocket.close(code=4004, reason="Scan not found")
        return

    await manager.connect(websocket, scan_id)

    await websocket.send_json({
        "type": "connection_ack",
        "scan_id": scan_id,
        "message": "Connected to scan progress"
    })

    if scan["status"] == "complete":
        results = await get_scan_results(scan_id)
        await websocket.send_json({
            "type": "complete",
            "scan_id": scan_id,
            "status": "complete",
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
        manager.disconnect(websocket, scan_id)
        await websocket.close()
        return

    listener_task = None
    task_ref = [None]
    
    try:
        listener_task = asyncio.create_task(
            listen_redis_messages(websocket, scan_id, task_ref)
        )

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                print(f"Received from client: {data}")
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if listener_task and not listener_task.done():
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
        
        manager.disconnect(websocket, scan_id)


@router.get("/api/health")
async def health_check():
    health = {"status": "ok", "db": "unknown", "redis": "unknown"}
    
    try:
        conn = await get_db_connection()
        await conn.fetchval("SELECT 1")
        await conn.close()
        health["db"] = "ok"
    except Exception as e:
        health["db"] = f"error: {str(e)}"
        health["status"] = "degraded"

    try:
        r = await get_redis_client()
        await r.ping()
        await r.close()
        health["redis"] = "ok"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        health["status"] = "degraded"

    status_code = 200 if health["status"] == "ok" else 503
    return JSONResponse(content=health, status_code=status_code)
