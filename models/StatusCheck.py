from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StatusCheck(Base):
    __tablename__ = "status_check"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    response_code = Column(Integer)
    creation_time = Column(DateTime, server_default=func.now())
