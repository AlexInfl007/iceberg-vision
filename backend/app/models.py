from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.database import Base

class Iceberg(Base):
    __tablename__ = "icebergs"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, index=True)
    side = Column(String)
    tranche_size = Column(Float)
    total_volume = Column(Float)
    duration_sec = Column(Float)
    replenishment_count = Column(Integer)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    status = Column(String)  # active, completed, cancelled
    confidence = Column(String)  # medium, high
    symbol = Column(String)