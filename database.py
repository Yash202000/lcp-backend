from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from security.settings import settings


engine = create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, pool_pre_ping=True, pool_recycle=300,
    isolation_level="READ UNCOMMITTED", pool_size=500, max_overflow=100)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
