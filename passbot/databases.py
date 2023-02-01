import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv('DATABASE_URI', ''))
SessionLocal = sessionmaker(bind=engine)
