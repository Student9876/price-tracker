from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Force IPv4 by adding connect_args
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
        # This helps with connection stability
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)