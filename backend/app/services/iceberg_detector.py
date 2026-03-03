import os
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Iceberg

load_dotenv()

MIN_REPLENISH_MEDIUM = int(os.getenv("MIN_REPLENISH_MEDIUM"))
MIN_REPLENISH_HIGH = int(os.getenv("MIN_REPLENISH_HIGH"))
ICEBERG_TIMEOUT = int(os.getenv("ICEBERG_TIMEOUT"))
MAX_DB_SIZE_MB = int(os.getenv("MAX_DB_SIZE_MB"))
SYMBOL = os.getenv("SYMBOL")


class IcebergDetector:

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.levels = {}
        self.db = SessionLocal()

    async def process(self, data):

        if "data" not in data:
            return

        now = datetime.utcnow()

        for side_key, side_name in [("b", "Bid"), ("a", "Ask")]:

            for order in data["data"].get(side_key, []):

                price = round(float(order[0]), 2)
                volume = float(order[1])

                # 🔥 production фильтр шума
                if volume < 0.05:
                    continue

                key = (price, side_name)

                if key not in self.levels:
                    self.levels[key] = {
                        "initial_volume": volume,
                        "current_volume": volume,
                        "total_volume": 0,
                        "replenishments": 0,
                        "first_seen": now,
                        "last_update": now
                    }
                    continue

                level = self.levels[key]
                prev_volume = level["current_volume"]

                # частичное исполнение
                if volume < prev_volume:
                    traded = prev_volume - volume
                    level["total_volume"] += traded

                # refill
                if (
                    volume >= level["initial_volume"] * 0.98
                    and prev_volume < level["initial_volume"] * 0.7
                ):
                    level["replenishments"] += 1

                level["current_volume"] = volume
                level["last_update"] = now

        await self._check_timeouts(now)

    async def _check_timeouts(self, now):

        to_remove = []

        for key, level in self.levels.items():

            idle = (now - level["last_update"]).total_seconds()

            if idle > ICEBERG_TIMEOUT:

                repl = level["replenishments"]

                if repl >= MIN_REPLENISH_MEDIUM:

                    duration = (
                        level["last_update"] - level["first_seen"]
                    ).total_seconds()

                    confidence = (
                        "high" if repl >= MIN_REPLENISH_HIGH else "medium"
                    )

                    status = (
                        "completed"
                        if level["current_volume"] == 0
                        else "cancelled"
                    )

                    iceberg = Iceberg(
                        price=key[0],
                        side=key[1],
                        tranche_size=level["initial_volume"],
                        total_volume=level["total_volume"],
                        duration_sec=duration,
                        replenishment_count=repl,
                        first_seen=level["first_seen"],
                        last_seen=level["last_update"],
                        status=status,
                        confidence=confidence,
                        symbol=SYMBOL
                    )

                    self.db.add(iceberg)
                    self.db.commit()

                    print(
                        f"[ICEBERG] {confidence.upper()} "
                        f"{key[1]} {key[0]} "
                        f"Repl:{repl} Dur:{round(duration,1)} "
                        f"Status:{status}"
                    )

                    await self.event_bus.emit({
                        "type": "iceberg",
                        "price": key[0],
                        "side": key[1],
                        "confidence": confidence,
                        "replenishments": repl,
                        "duration": duration,
                        "status": status
                    })

                to_remove.append(key)

        for k in to_remove:
            del self.levels[k]

        await self._cleanup_db()

    async def _cleanup_db(self):

        result = self.db.execute(text("PRAGMA page_count;")).fetchone()
        page_count = result[0]

        page_size = self.db.execute(text("PRAGMA page_size;")).fetchone()[0]

        db_size_mb = (page_count * page_size) / (1024 * 1024)

        if db_size_mb > MAX_DB_SIZE_MB:
            print("[DB CLEANUP] Removing oldest records...")
            self.db.execute(text("""
                DELETE FROM icebergs
                WHERE id IN (
                    SELECT id FROM icebergs
                    ORDER BY first_seen ASC
                    LIMIT 5000
                )
            """))
            self.db.commit()