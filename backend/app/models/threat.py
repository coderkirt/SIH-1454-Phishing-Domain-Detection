from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    threat_type = Column(String(50))  # phishing, malware, etc
    threat_data = Column(Text)  # URL or domain
    severity = Column(String(20))  # low, medium, high, critical
    last_updated = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Threat(type={self.threat_type}, severity={self.severity})>"
