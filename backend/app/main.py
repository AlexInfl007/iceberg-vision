import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.services.bybit_ws import BybitWebSocket
from app.services.iceberg_detector import IcebergDetector
from app.services.volume_analyzer import VolumeAnalyzer
from app.services.levels_analyzer import LevelsAnalyzer
from app.services.stats_service import StatsService
from app.utils.event_bus import EventBus

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Iceberg Vision API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

event_bus = EventBus()
detector = IcebergDetector(event_bus)
volume = VolumeAnalyzer(event_bus)
levels = LevelsAnalyzer(event_bus)
stats_service = StatsService()

bybit = BybitWebSocket(detector, volume)


@app.on_event("startup")
async def startup():
    asyncio.create_task(bybit.connect())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    async def listener(event):
        await ws.send_json(event)

    event_bus.register(listener)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        event_bus.unregister(listener)
    except Exception:
        event_bus.unregister(listener)


@app.get("/stats")
def get_stats():
    return stats_service.get_24h_stats()


@app.get("/dashboard")
def dashboard():
    return stats_service.get_24h_stats()


@app.get("/health")
def health():
    return {"status": "ok"}
