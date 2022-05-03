# current progress: created table schemas, tables are not populated

import logging
import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

Base = declarative_base()

# Set up logging config
# logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__file__)

# Set up RDS connection
conn_type = "mysql+pymysql"
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
db_name = os.getenv("DATABASE_NAME")
engine_string = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"
try:
    engine = create_engine(engine_string)
except OperationalError as e:
    logger.error(f"Connection failed {e}")
    raise e


# Create a db session
Session = sessionmaker(bind=engine)


class ResultsWomen(Base):
    __tablename__ = "results_women"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, unique=True, nullable=False)
    gymnast = Column(String(100), unique=False, nullable=False)
    vault = Column(Integer, unique=False, nullable=True)
    uneven_bars = Column(Integer, unique=False, nullable=True)
    balance_beam = Column(Integer, unique=False, nullable=True)
    floor_exercise = Column(Integer, unique=False, nullable=True)
    total = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return f"<Results (women) {self.rank}>"


class ResultsMen(Base):
    __tablename__ = "results_men"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, unique=True, nullable=False)
    gymnast = Column(String(100), unique=False, nullable=False)
    horse = Column(Integer, unique=False, nullable=True)
    rings = Column(Integer, unique=False, nullable=True)
    vault = Column(Integer, unique=False, nullable=True)
    parallel_bars = Column(Integer, unique=False, nullable=True)
    horizontal_bar = Column(Integer, unique=False, nullable=True)
    total = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return f"<Results (men) {self.rank}>"


if __name__ == "__main__":
    # Create the tracks table
    Base.metadata.create_all(engine)
    logger.info("Database created!")