"""
defines the data models for the relational database
completes the functions of the database: inserting, selecting
"""
import logging
import typing
import random
from typing import Tuple
import pandas as pd

import flask
import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
logger = logging.getLogger(__name__)


class Results(Base):
    """
    defines the results_labels table
    """
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
    """
    defines the user_input_matching table
    """
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
    """
    defines functions to interact with the database
    """
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
        """
        closes the connection to the db
        :return: None
        """
        self.session.close()

    def add_result(self, result) -> None:
        """
        adds a row to the results table
        :param result: a dictionary that contains
            necessary fields for the Results table
        :return: None
        """
        session = self.session
        logger.info(result)
        result_obj = Results(**result)
        try:
            session.add(result_obj)
            session.commit()
            logger.info("The result for %s has been added to the table.", result['gymnast'])
        except OperationalError as err:
            logger.error('Optional error %s .', err)
            raise err
        except Exception as err:
            logger.error(err)
            raise err

    def add_user_input(self, user_input) -> None:
        """
        adds a row to the user_input_matching table
        :param user_input: a dictionary that contains
            necessary fields for user_input_matching table
        :return: None
        """
        session = self.session
        user_input_obj = UserInputs(**user_input)
        try:
            session.add(user_input_obj)
            session.commit()
            logger.info("The user input for %s has been added to the table.",
                        user_input['gymnast'])
        except OperationalError as err:
            logger.error('Optional error %s .', err)
            raise err
        except Exception as err:
            logger.error(err)
            raise err

    def get_matched_gymnast(self,
                            user_label: int,
                            different: bool,
                            ) -> Tuple[str, str]:
        """
        returns a gymnast based on given label
        :param user_label: the label of user input
        :param different: returns the gymnast in the same
            group if true, different group if false
        :return: name of the similar and different gymnast
        """
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
    """
    creates the tables in the database
    :param engine_string: database uri
    :return: None
    """
    engine = create_engine(engine_string)

    Base.metadata.create_all(engine)
    logger.info("Tables created!")


def add_results(engine_string: str,
                filename: str,
                columns: list[str]) -> None:
    """
    adds multiple rows to the table results
    :param engine_string: database uri
    :param filename: file path for input
    :param columns: columns to ingest to database
    :return: None
    """
    results_data = pd.read_csv(filename)
    results = results_data[columns].to_dict(orient='records')
    result_manager = ResultsManager(app=None, engine_string=engine_string)
    for i in range(len(results)):
        try:
            result_manager.add_result(results[i])
        except sqlalchemy.exc.OperationalError as err:
            logger.error(
                "Error page returned. Not able to add song to MySQL database.  "
                "Please check engine string and VPN. Error: %s ", err)
        except Exception as err:
            logger.error("Error occurred %s", err)
        result_manager.close()
