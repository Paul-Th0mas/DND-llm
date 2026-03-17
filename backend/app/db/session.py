from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        # Commit the transaction after the endpoint returns successfully.
        # Without this, flush() sends SQL to the DB but the transaction is
        # rolled back when the session closes, so nothing ever persists.
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
