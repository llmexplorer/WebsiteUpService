from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"
    url = Column(String, primary_key=True)
    creation_date = Column(DateTime, server_default=func.now())
