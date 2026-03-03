import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

SYMBOL = os.getenv("SYMBOL")


class BybitWebSocket:

    def __init__(self, detector, volume):
        self.url = "wss://stream-testnet.bybit.com/v5/public/linear"
        self.symbol = SYMBOL
        self.detector = detector
        self.volume = volume

    async def connect(self):

        while True:
            try:
                async with websockets.connect(self.url) as ws:

                    await ws.send(json.dumps({
                        "op": "subscribe",
                        "args": [
                            f"orderbook.50.{self.symbol}",
                            f"publicTrade.{self.symbol}"
                        ]
                    }))

                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        topic = data.get("topic", "")

                        if "orderbook" in topic:
                            await self.detector.process(data)

                        if "publicTrade" in topic:
                            await self.volume.process(data)

            except Exception as e:
                print("Reconnecting WS:", e)
                await asyncio.sleep(3)