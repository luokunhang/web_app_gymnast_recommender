"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import yaml
import logging.config

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('gymnast-matching-pipeline')

# my code
from src import util, acquire_data, populate_database, clustering
from config.flaskconfig import SQLALCHEMY_DATABASE_URI


if __name__ == '__main__':
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Prepare data for the app.")

    parser.add_argument('action',
                        help='Specify the step in the pipeline.',
                        choices=['acquire',
                                 'train',
                                 'populate_database',
                                 'save_to_s3',
                                 'all'])
    parser.add_argument('--database_uri',
                        help='provide a database uri if none exists in the environment'
                             'or your wanna use otherwise',
                        default='sqlite:///data/tracks.db')
    parser.add_argument('--s3_bucket_name',
                        help='Provide your own bucket name or default will be used.',
                        default='2022-msia423-luo-kunhang')
    #
    args = parser.parse_args()

    with open('config/config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if SQLALCHEMY_DATABASE_URI:
        engine_string = SQLALCHEMY_DATABASE_URI
    else:
        engine_string = args.database_uri

    if args.action in ['acquire', 'all']:
        # data acquisition: from wiki page to this repo
        acquire_data.scraping(config)

    if args.action in ['train', 'all']:
        # ml pipeline
        df, std_columns = clustering.pre_processing(config)
        clustering.try_models(df, std_columns, config)
        clustering.get_model(df, std_columns, config)

    if args.action in ['populate_database', 'all']:
        # add the table to RDS
        populate_database.create_db(util.engine_string)
        populate_database.add_results(util.engine_string,
                                      config['filepath']['labeled_data'])

    if args.action in ['save_to_s3', 'all']:
        # add averages and sds, data, model obj
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['labeled_data'],
                          config['s3_path']['labeled_data'])
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['model'],
                          config['s3_path']['model'])
        util.upload_to_s3(args.s3_bucket_name,
                          config['filepath']['avg_sd'],
                          config['s3_path']['avg_sd'])
