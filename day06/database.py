from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL — SQLite stores everything in one file
# Three slashes = relative path (file will appear in same folder)
DATABASE_URL = "sqlite:///./users.db"

# Engine — the connection between Python and the database
# check_same_thread=False is required for SQLite only
# SQLite normally only allows the thread that created it to use it
# FastAPI is async and uses multiple threads, so we disable that check
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

# SessionLocal — a factory that creates new database sessions
# autocommit=False — we control when to save (explicit commit)
# autoflush=False — we control when to sync memory to database
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

# Base — every database model will inherit from this
Base = declarative_base()

#Dependency - gives each request to its own session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



