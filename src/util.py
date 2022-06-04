import logging

import boto3

from config.flaskconfig import SQLALCHEMY_DATABASE_URI

engine_string = SQLALCHEMY_DATABASE_URI

logger = logging.getLogger(__name__)


def upload_to_s3(bucket: str,
                 local_file_location: str,
                 s3_file_location: str) -> None:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    try:
        bucket.upload_file(local_file_location, s3_file_location)
        logger.info('File has been saved to s3 as %s .', s3_file_location)
    except Exception as e:
        logger.error('Unknown error occurred, %s .', e)
        raise e
    # except boto3.exceptions.ParamValidationError as error:
    #     raise ValueError('The parameters you provided are incorrect: %s .', error)
    # except boto3.exceptions.ClientError as error:
    #     logger.warning('API call limit exceeded %s .', error)
    #     raise error


def retrieve_from_s3(bucket: str,
                     s3_file_location: str,
                     local_file_location: str) -> None:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    try:
        bucket.download_file(s3_file_location, local_file_location)
        logger.info('File has been downloaded to this repo as %s .',
                    local_file_location)
    except Exception as e:
        logger.error('Unknown error occurred, %s .', e)
        raise e
    # except boto3.exceptions.ParamValidationError as error:
    #     raise ValueError('The parameters you provided are incorrect: %s .', error)
    # except boto3.exceptions.ClientError as error:
    #     logger.warning('API call limit exceeded %s .', error)
    #     raise error
