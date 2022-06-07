"""
acquires data from the source website, parses it,
cleans it and saves to the repo
"""
import logging
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

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
        data = pd.DataFrame(final_table[0])
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
    except Exception as err:
        logger.error('Unknown error occurred %s .', err)
        raise err

    # cleaning
    data.set_axis(config['acquire_data']['columns'], axis=1, inplace=True)

    data.loc[0, "rank"] = 1
    data.loc[1, "rank"] = 2
    data.loc[2, "rank"] = 3

    data = data.applymap(lambda x: re.sub(r"\s?\(([^\)]+)\)", "", str(x)))
    data.to_csv(config['filepath']['data'], index=False)
    logger.info('Data has been parsed and saved.')
