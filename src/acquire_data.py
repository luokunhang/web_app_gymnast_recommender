"""
acquires data from the source website, parses it,
cleans it and saves to the repo
"""
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


def scraping(config: dict) -> None:
    """
    scrapes data from the source website, cleans up
    the columns names and entries, saves it in csv
    :param config: a dictionary that contains
        url to the data source website
        column names of the dataframe
        file path to save the clean data
    :return: None
    """
    try:
        response = requests.get(config['acquire_data']['url'])
        logger.info('The source data has been processed.')
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', {'class': "wikitable"})
        final_table = pd.read_html(str(tables[-1]))
        df = pd.DataFrame(final_table[0])
        logger.info('The data has been parsed to a dataframe.')
    except requests.exceptions.ConnectionError:
        logger.error(
            "There was a connection error. The maximum number of "
            "attempts (%i) have been made to connect."
            "Please check your connection then try again")
    except requests.exceptions.MissingSchema:
        logger.error("Need to add http:// to beginning of url. "
                     "Please try again. Url provided: %s",
                     config['acquire_data']['url'])
    else:
        logger.info(response.text)

    # cleaning
    df.set_axis(config['acquire_data']['columns'], axis=1, inplace=True)

    df.loc[0, "rank"] = 1
    df.loc[1, "rank"] = 2
    df.loc[2, "rank"] = 3

    df = df.applymap(lambda x: re.sub(r"\s?\(([^\)]+)\)", "", str(x)))
    df.to_csv(config['filepath']['data'], index=False)
    logger.info('Data has been cleaned.')
