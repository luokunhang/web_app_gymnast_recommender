import os

import boto3
from sklearn.base import BaseEstimator
import pickle

## Set up RDS connection string
conn_type = "mysql+pymysql"
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
db_name = os.getenv("DATABASE_NAME")
engine_string = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"


def upload_to_s3(local_file_location: str, s3_file_location: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("2022-msia423-luo-kunhang")
    bucket.upload_file(local_file_location, s3_file_location)


def retrieve_from_s3(s3_file_location: str, local_file_location: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("2022-msia423-luo-kunhang")
    bucket.download_file(s3_file_location, local_file_location)


def save_model(model: BaseEstimator, filename: str) -> None:
    with open(filename, "w+") as f:
        pickle.dump(model, f)