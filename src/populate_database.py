
import logging
import typing
import random
from typing import Tuple
import pandas as pd

import flask
import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
logger = logging.getLogger(__file__)


class Results(Base):
    __tablename__ = 'results_labels'

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, unique=True, nullable=False)
    gymnast = Column(String(100), unique=False, nullable=False)
    vault = Column(Float, unique=False, nullable=True)
    uneven_bars = Column(Float, unique=False, nullable=True)
    balance_beam = Column(Float, unique=False, nullable=True)
    floor_exercise = Column(Float, unique=False, nullable=True)
    total = Column(Float, unique=False, nullable=True)
    label = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return f"<Results {self.gymnast}>"


class UserInputs(Base):
    __tablename__ = 'user_input_matching'

    id = Column(Integer, primary_key=True)
    gymnast = Column(String(100), unique=False, nullable=False)
    vault = Column(Float, unique=False, nullable=True)
    uneven_bars = Column(Float, unique=False, nullable=True)
    balance_beam = Column(Float, unique=False, nullable=True)
    floor_exercise = Column(Float, unique=False, nullable=True)
    label = Column(Integer, unique=False, nullable=True)
    similar = Column(String(100), unique=False, nullable=False)
    different = Column(String(100), unique=False, nullable=False)

    def __repr__(self):
        return f"<Results by user: {self.gymnast}>"


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

    def add_result(self, **kwargs) -> None:
        session = self.session
        result = Results(rank=kwargs['rank'],
                         gymnast=kwargs['gymnast'],
                         vault=kwargs['vault'],
                         uneven_bars=kwargs['uneven_bars'],
                         balance_beam=kwargs['balance_beam'],
                         floor_exercise=kwargs['floor_exercise'],
                         total=kwargs['total'],
                         label=kwargs['label']
                         )
        try:
            session.add(result)
            session.commit()
            logger.info("The result for %s has been added to the table.", kwargs['gymnast'])
        except Exception as e:
            logger.error(e)
            raise e

    def add_user_input(self, **kwargs) -> None:
        session = self.session
        user_input = UserInputs(gymnast=kwargs['gymnast'],
                                vault=kwargs['vault'],
                                uneven_bars=kwargs['uneven_bars'],
                                balance_beam=kwargs['balance_beam'],
                                floor_exercise=kwargs['floor_exercise'],
                                label=kwargs['label'],
                                similar=kwargs['similar'],
                                different=kwargs['different'])
        session.add(user_input)
        session.commit()
        logger.info("The user input for %s has been added to the table.",
                    kwargs['gymnast'])

    def get_matched_gymnast(self,
                            user_label: int,
                            different: bool,
                            ) -> Tuple[str, str]:
        session = self.session
        if different:
            gymnast = (
                session.query(Results).filter(Results.label != user_label).all()
            )
        else:
            gymnast = (
                session.query(Results).filter(Results.label == user_label).all()
            )
        if gymnast:
            return random.choice(gymnast)
        return None


def create_db(engine_string: str) -> None:
    engine = create_engine(engine_string)
    Base.metadata.create_all(engine)
    logger.info("Tables created!")


# def add_result(engine_string: str, result: dict) -> None:
#     result_manager = ResultsManager(app=None, engine_string=engine_string)
#     try:
#         result_manager.add_result(**result)
#     except sqlalchemy.exc.OperationalError as e:
#         logger.error(
#             "Error page returned. Not able to add song to MySQL database.  "
#             "Please check engine string and VPN. Error: %s ", e)
#     except Exception as e:
#         logger.error("Error occurred %s", e)
#     result_manager.close()


def add_results(engine_string: str, filename: str) -> None:
    results = pd.read_csv(filename).to_dict(orient='records')
    result_manager = ResultsManager(app=None, engine_string=engine_string)
    for i in range(len(results)):
        try:
            result_manager.add_result(**results[i])
        except sqlalchemy.exc.OperationalError as e:
            logger.error(
                "Error page returned. Not able to add song to MySQL database.  "
                "Please check engine string and VPN. Error: %s ", e)
        except Exception as e:
            logger.error("Error occurred %s", e)
        result_manager.close()
