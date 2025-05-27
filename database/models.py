from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    tokens = Column(Integer, nullable=False)
    prizes = Column(JSON, nullable=False)
