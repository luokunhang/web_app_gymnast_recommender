"""
Configures the clustering recommender pipeline and saves
the files needed for an online model recommending app
"""
import os.path

from src import util
from src import acquire_data
from src import populate_database
from src import clustering

import argparse
import yaml
import logging.config

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('gymnast-matching-pipeline')


if __name__ == '__main__':
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Prepare data for the app.")

    parser.add_argument('action',
                        help='Specify the step in the pipeline.',
                        choices=['acquire',
                                 'train',
                                 'create_database',
                                 'populate_database',
                                 'save_to_s3',
                                 'pipeline',
                                 'all'])
    parser.add_argument('--s3_bucket_name',
                        help='Provide your own bucket name or default will be used.',
                        default='2022-msia423-luo-kunhang')
    args = parser.parse_args()
    logger.debug('The arguments are parsed.')

    with open('config/config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        logger.debug('The yaml file is processed.')

    if not os.path.exists('data/intermediate'):
        os.mkdir('data/intermediate')

    if args.action in ['acquire_to_s3', 'all']:
        logger.debug('You are in the step of acquiring data from'
                     'data source and uploading them to s3 bucket.')
        # data acquisition: from wiki page to this repo
        acquire_data.scraping(config)
        # from this repo to s3
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['data'],
                          config['s3_path']['data'])

    if args.action in ['train_from_s3', 'pipeline', 'all']:
        # download data from s3
        util.retrieve_from_s3(args.s3_bucket_name,
                              config['s3_path']['data'],
                              config['filepath']['data'])
        # ml pipeline: processing data and trying models
        df, std_columns = clustering.pre_processing(config)
        clustering.try_models(df, std_columns, config)
        clustering.get_model(df, std_columns, config)

    if args.action in ['create_database', 'pipeline', 'all']:
        # add the tables to RDS
        populate_database.create_db(util.engine_string)

    if args.action in ['populate_database', 'pipeline', 'all']:
        # populates the tables
        populate_database.add_results(util.engine_string,
                                      config['filepath']['labeled_data'])

    if args.action in ['model_to_s3', 'pipeline', 'all']:
        # add averages and sds, data, model obj to s3
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['labeled_data'],
                          config['s3_path']['labeled_data'])
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['model'],
                          config['s3_path']['model'])
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['avg_sd'],
                          config['s3_path']['avg_sd'])
