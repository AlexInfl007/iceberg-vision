from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.iceberg import Iceberg


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

        return {
            "total": total,
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate": (
                completed / total * 100 if total else 0
            ),
            "avg_size": avg_size,
            "avg_duration": avg_duration
        }