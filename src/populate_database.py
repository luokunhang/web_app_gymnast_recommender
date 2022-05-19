# current progress: created table schemas, tables are not populated
import argparse
import logging
import os
import typing
import pandas as pd

import flask
import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy

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
    vault = Column(Float, unique=False, nullable=True)
    uneven_bars = Column(Float, unique=False, nullable=True)
    balance_beam = Column(Float, unique=False, nullable=True)
    floor_exercise = Column(Float, unique=False, nullable=True)
    total = Column(Float, unique=False, nullable=True)

    def __repr__(self):
        return f"<Results (women) {self.rank}>"


class ResultsMen(Base):
    __tablename__ = "results_men"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, unique=True, nullable=False)
    gymnast = Column(String(100), unique=False, nullable=False)
    horse = Column(Float, unique=False, nullable=True)
    rings = Column(Float, unique=False, nullable=True)
    vault = Column(Float, unique=False, nullable=True)
    parallel_bars = Column(Float, unique=False, nullable=True)
    horizontal_bar = Column(Float, unique=False, nullable=True)
    total = Column(Float, unique=False, nullable=True)

    def __repr__(self):
        return f"<Results (men) {self.rank}>"


class ResultsManager:

    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None):
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        self.session.close()

    def add_women_result(self,
                         # rank: int,
                         # gymnast: str,
                         # vault: float,
                         # uneven_bars: float,
                         # balance_beam: float,
                         # floor_exercise: float,
                         # total: float
                         **kwargs
                         ) -> None:
        session = self.session
        result = ResultsWomen(kwargs
                              # rank=rank,
                              # gymnast=gymnast,
                              # vault=vault,
                              # uneven_bars=uneven_bars,
                              # balance_beam=balance_beam,
                              # floor_exercise=floor_exercise,
                              # total=total
                              )
        session.add(result)
        session.commit()
        logger.info("The result for %s has been added to the table.", kwargs['gymnast'])

    def add_men_result(self,
                       # rank: int,
                       # gymnast: str,
                       # vault: float,
                       # uneven_bars: float,
                       # balance_beam: float,
                       # floor_exercise: float,
                       # total: float
                       **kwargs
                       ) -> None:
        session = self.session
        result = ResultsWomen(kwargs
                              # rank=rank,
                              # gymnast=gymnast,
                              # vault=vault,
                              # uneven_bars=uneven_bars,
                              # balance_beam=balance_beam,
                              # floor_exercise=floor_exercise,
                              # total=total,
                              # ...
                              )
        session.add(result)
        session.commit()
        logger.info("The result for %s has been added to the table.", kwargs['gymnast'])


def create_db(engine_string: str) -> None:
    engine = create_engine(engine_string)

    Base.metadata.create_all(engine)
    logger.info("Database created!")


def add_result_women(engine_string: str, result: dict) -> None:

    result_women_manager = ResultsManager(engine_string=engine_string)
    try:
        result_women_manager.add_women_result(result)
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to MySQL database.  "
            "Please check engine string and VPN. Error: %s ", e)
    except Exception as e:
        logger.error(e)
    result_women_manager.close()


def add_result_men(engine_string: str, result: dict) -> None:

    result_women_manager = ResultsManager(engine_string=engine_string)
    try:
        result_women_manager.add_men_result(result)
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to MySQL database.  "
            "Please check engine string and VPN. Error: %s ", e)
    except Exception as e:
        logger.error(e)
    result_women_manager.close()


def add_results_women(engine_string: str, filename: str) -> None:
    women_results = pd.read_csv(filename, header=True).to_dict(orient='records')
    for i in len(women_results):
        add_result_women(engine_string, women_results[i])


def add_results_men(engine_string: str, filename: str) -> None:
    men_results = pd.read_csv(filename, header=True).to_dict(orient='records')
    for i in len(men_results):
        add_result_men(engine_string, men_results[i])


if __name__ == "__main__":
    # Create the tracks table
    Base.metadata.create_all(engine)
    logger.info("Database created!")