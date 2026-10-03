import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reads DATABASE_URL from environment if available (Render Postgres or cloud DB),
# otherwise defaults to local SQLite deadtime_b2b.db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./deadtime_b2b.db")

# Render uses postgres:// in DATABASE_URL, which SQLAlchemy 1.4+ deprecated in favor of postgresql://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
