
import pickle
import json

import pandas as pd

from src import util


def get_label_for_input(user_input: dict,
                        config: dict,
                        bucket: str) -> int:
    #
    util.retrieve_from_s3(bucket,
                          config['s3_path']['model'],
                          config['filepath']['model'])
    with open(config['filepath']['model'], 'rb') as file:
        kmeans = pickle.load(file)

    util.retrieve_from_s3(bucket,
                          config['s3_path']['avg_sd'],
                          config['filepath']['avg_sd'])
    with open('data/external/avg_sd.json', 'r') as file:
        avg_sd = json.load(file)

    # get std of scores
    data = []
    columns = config['clustering']['features']
    for i in columns:
        score = (user_input[i] - avg_sd[i+'_avg']) / avg_sd[i+'_sd']
        data.append(score)
    std_columns = [i + '_std' for i in columns]

    # pd df of test data
    test = pd.DataFrame([data], columns=std_columns)

    pred_label = kmeans.predict(test)[0]
    return pred_label
