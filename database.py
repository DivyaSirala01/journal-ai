from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os

#Useful for local development and deployment using docker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sqllite.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()    