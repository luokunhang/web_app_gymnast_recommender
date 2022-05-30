import os

import boto3

from config.flaskconfig import SQLALCHEMY_DATABASE_URI

engine_string = SQLALCHEMY_DATABASE_URI


def upload_to_s3(bucket: str,
                 local_file_location: str,
                 s3_file_location: str) -> None:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.upload_file(local_file_location, s3_file_location)


def retrieve_from_s3(bucket: str,
                     s3_file_location: str,
                     local_file_location: str) -> None:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.download_file(s3_file_location, local_file_location)
