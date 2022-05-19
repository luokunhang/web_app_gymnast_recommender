"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.add_songs import create_db, add_song

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('penny-lane-pipeline')

# my code


from src import util, acquire_data, populate_database

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sp_ingest = subparsers.add_parser("ingest",
                                      description="Add data to database")
    sp_ingest.add_argument("--artist", default="Emancipator",
                           help="Artist of song to be added")
    sp_ingest.add_argument("--title", default="Minor Cause",
                           help="Title of song to be added")
    sp_ingest.add_argument("--album", default="Dusk to Dawn",
                           help="Album of song being added")
    sp_ingest.add_argument("--engine_string",
                           default='sqlite:///data/tracks.db',
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        add_song(args)
    else:
        parser.print_help()

    # data acquisition: from wiki page to s3
    acquire_data.scraping("https://en.wikipedia.org/wiki/Gymnastics_at_the_2020_Summer_Olympics_%E2%80%93_Women%27s_artistic_individual_all-around",
                          ["Rank", "Gymnast", "Vault", "Uneven Bars", "Balance Beam", "Floor Exercise", "Total"],
                          "../data/external/women_final_results.csv")
    acquire_data.scraping("https://en.wikipedia.org/wiki/Gymnastics_at_the_2020_Summer_Olympics_%E2%80%93_Men%27s_artistic_individual_all-around",
                          ["Rank", "Gymnast", "Floor Exercise", "Horse", "Rings", "Vault", "Parallel Bars", "Horizontal Bar", "Total"],
                          "../data/external/men_final_results.csv")
    util.upload_to_s3("../data/external/women_final_results.csv",
                              "avc-project-data/women_final_results.csv")
    util.upload_to_s3("../data/external/men_final_results.csv",
                              "avc-project-data/men_final_results.csv")

    # data acquisition: from s3 to RDS

    # create db
    populate_database.create_db(util.engine_string)

    # populate tables
    ## getting data in the local folder data/
    acquire_data.retrieve_from_s3("avc-project-data/women_final_results.csv",
                                  "data/external/women_final_results.csv")
    acquire_data.retrieve_from_s3("avc-project-data/men_final_results.csv",
                                  "data/external/men_final_results.csv")

    ## moving the data to RDS
    populate_database.add_results_women(util.engine_string, "data/external/women_final_results.csv")
    populate_database.add_results_men(util.engine_string, "data/external/men_final_results.csv")



