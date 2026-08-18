from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class URLCheck(Base):
    __tablename__ = "url_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    url = Column(String(500), index=True)
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float)
    ml_confidence = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<URLCheck(url={self.url[:30]}..., risk={self.risk_level})>"
