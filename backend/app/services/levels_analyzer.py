from collections import defaultdict


class LevelsAnalyzer:

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.touches = defaultdict(int)
        self.volume = defaultdict(float)
        self.icebergs = defaultdict(int)

    async def record_touch(self, price):
        self.touches[price] += 1

    async def record_volume(self, price, vol):
        self.volume[price] += vol

    async def record_iceberg(self, price):
        self.icebergs[price] += 1

    async def calculate(self):

        levels = []

        for price in self.touches:

            if self.touches[price] < 2:
                continue

            weight = (
                self.touches[price] * 0.4 +
                self.volume[price] * 0.3 +
                self.icebergs[price] * 0.3
            )

            levels.append({
                "price": price,
                "weight": weight
            })

        levels.sort(key=lambda x: x["weight"], reverse=True)

        await self.event_bus.emit({
            "type": "levels",
            "data": levels[:20]
        })