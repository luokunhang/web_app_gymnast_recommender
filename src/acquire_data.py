import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def scraping(config: dict) -> None:
    response = requests.get(config['acquire_data']['url'])
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': "wikitable"})
    final_table = pd.read_html(str(tables[-1]))
    df = pd.DataFrame(final_table[0])

    # cleaning
    df.set_axis(config['acquire_data']['columns'], axis=1, inplace=True)

    df.loc[0, "rank"] = 1
    df.loc[1, "rank"] = 2
    df.loc[2, "rank"] = 3

    df = df.applymap(lambda x: re.sub(r"\s?\(([^\)]+)\)", "", str(x)))
    df.to_csv(config['filepath']['data'], index=False)
