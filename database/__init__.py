from config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

database_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
