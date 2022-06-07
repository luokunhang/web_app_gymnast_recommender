"""
Configures the clustering recommender pipeline and saves
the files needed for an online model recommending app
"""
import os.path
import argparse
import logging.config
import yaml

from src import util
from src import acquire_data
from src import populate_database
from src import clustering

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('gymnast-matching-pipeline')


if __name__ == '__main__':
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Prepare data for the app.")

    parser.add_argument('action',
                        help='Specify the step in the pipeline.',
                        choices=['acquire',
                                 'load_clean',
                                 'features',
                                 'train',
                                 'score',
                                 'evaluate',
                                 'create_database',
                                 'populate_database'
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

    # creates the folder for all files in the ml pipeline
    if not os.path.exists('data/intermediate'):
        os.mkdir('data/intermediate')

    if args.action in ['acquire', 'all']:
        logger.debug('You are in the step of acquiring data from'
                     'data source and uploading them to s3 bucket.')
        # data acquisition: from wiki page to this repo
        acquire_data.scraping(config)
        # from this repo to s3
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['data'],
                          config['s3_path']['data'])

    if args.action in ['load_clean', 'pipeline', 'all']:
        # download data from s3
        util.retrieve_from_s3(args.s3_bucket_name,
                              config['s3_path']['data'],
                              config['filepath']['data'])

    if args.action in ['features', 'pipeline', 'all']:
        # generate features for clustering
        clustering.pre_processing(config)

    if args.action in ['train', 'pipeline', 'all']:
        # train the model
        clustering.get_model(config)
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['model'],
                          config['s3_path']['model'])
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['avg_sd'],
                          config['s3_path']['avg_sd'])

    if args.action in ['score', 'pipeline', 'all']:
        # generate data with labels
        clustering.score(config)

    if args.action in ['evaluate', 'pipeline', 'all']:
        # generate the model diagnostics
        clustering.try_models(config)

    if args.action in ['create_database', 'pipeline', 'all']:
        # add the tables to RDS
        populate_database.create_db(util.engine_string)

    if args.action in ['populate_database', 'pipeline', 'all']:
        # populates the tables
        populate_database.add_results(util.engine_string,
                                      config['filepath']['labeled_data'],
                                      config['database']['results'])
