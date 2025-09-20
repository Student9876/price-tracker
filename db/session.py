from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# This now points to the simpler DATABASE_URL setting
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)