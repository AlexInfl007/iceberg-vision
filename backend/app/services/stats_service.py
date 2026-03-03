from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import SessionLocal
from app.models import Iceberg


class StatsService:

    def __init__(self):
        self.db = SessionLocal()

    def get_24h_stats(self):
        since = datetime.utcnow() - timedelta(hours=24)

        icebergs = self.db.query(Iceberg).filter(
            Iceberg.first_seen >= since
        ).all()

        total = len(icebergs)
        completed = len([i for i in icebergs if i.status == "completed"])
        cancelled = len([i for i in icebergs if i.status == "cancelled"])

        avg_size = (
            sum(i.total_volume for i in icebergs) / total
            if total else 0
        )

        avg_duration = (
            sum(i.duration_sec for i in icebergs) / total
            if total else 0
        )

        high_confidence_share = (
            len([i for i in icebergs if i.confidence == "high"]) / total * 100
            if total else 0
        )

        top_levels = self._get_top_levels(icebergs)
        recent_icebergs = self._get_recent_icebergs()

        return {
            "total": total,
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate": (
                completed / total * 100 if total else 0
            ),
            "avg_size": avg_size,
            "avg_duration": avg_duration,
            "high_confidence_share": high_confidence_share,
            "top_levels": top_levels,
            "recent_icebergs": recent_icebergs
        }

    def _get_top_levels(self, icebergs):
        level_score = defaultdict(float)

        for item in icebergs:
            level_score[item.price] += item.total_volume + item.replenishment_count * 5

        levels = [
            {"price": price, "score": round(score, 2)}
            for price, score in level_score.items()
        ]
        levels.sort(key=lambda x: x["score"], reverse=True)

        return levels[:10]

    def _get_recent_icebergs(self):
        rows = self.db.query(Iceberg).order_by(Iceberg.first_seen.desc()).limit(25).all()

        return [
            {
                "id": row.id,
                "price": row.price,
                "side": row.side,
                "confidence": row.confidence,
                "status": row.status,
                "replenishment_count": row.replenishment_count,
                "duration_sec": row.duration_sec,
                "total_volume": row.total_volume,
                "first_seen": row.first_seen.isoformat() if row.first_seen else None
            }
            for row in rows
        ]
