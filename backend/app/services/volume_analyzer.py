import os
from datetime import datetime
from dotenv import load_dotenv
from collections import deque

load_dotenv()

LARGE_ORDER_THRESHOLD = float(os.getenv("LARGE_ORDER_THRESHOLD"))


class VolumeAnalyzer:

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.delta_window = deque(maxlen=200)

    async def process(self, data):

        if "data" not in data:
            return

        for trade in data["data"]:

            size = float(trade["v"])
            side = trade["S"]

            if size < LARGE_ORDER_THRESHOLD:
                continue

            delta = size if side == "Buy" else -size
            self.delta_window.append(delta)

            print(
                f"[TRUE VOLUME] {side} {size} BTC"
            )

            await self.event_bus.emit({
                "type": "true_volume",
                "delta": delta,
                "size": size,
                "side": side,
                "time": datetime.utcnow().isoformat()
            })