import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import boto3


def scraping(url: str, columns: list[str], output_file: str) -> bool:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': "wikitable"})
    final_table = pd.read_html(str(tables[-1]))
    df = pd.DataFrame(final_table[0])

    # cleaning
    df.set_axis(columns, axis=1, inplace=True)

    df.loc[0, "Rank"] = 1
    df.loc[1, "Rank"] = 2
    df.loc[2, "Rank"] = 3

    df = df.applymap(lambda x: re.sub(r"\s?\(([^\)]+)\)", "", str(x)))
    df.to_csv(output_file, index=False)
    return True

def upload_to_s3(filename:str, output_path) -> bool:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("2022-msia423-luo-kunhang")
    bucket.upload_file(filename, output_path)

if __name__ == "__main__":
    scraping("https://en.wikipedia.org/wiki/Gymnastics_at_the_2020_Summer_Olympics_%E2%80%93_Women%27s_artistic_individual_all-around",
             ["Rank", "Gymnast", "Vault", "Uneven Bars", "Balance Beam", "Floor Exercise", "Total"],
             "../data/external/women_final_results.csv")
    scraping("https://en.wikipedia.org/wiki/Gymnastics_at_the_2020_Summer_Olympics_%E2%80%93_Men%27s_artistic_individual_all-around",
             ["Rank", "Gymnast", "Floor Exercise", "Horse", "Rings", "Vault", "Parallel Bars", "Horizontal Bar", "Total"],
             "../data/external/men_final_results.csv")

    upload_to_s3("../data/external/women_final_results.csv",
                 "avc-project-data/women_final_results.csv")

    upload_to_s3("../data/external/men_final_results.csv",
                 "avc-project-data/men_final_results.csv")