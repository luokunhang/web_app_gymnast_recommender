"""
useful functions for the web app
"""
import pickle
import json

import pandas as pd

from src import util


def get_label_for_input(user_input: dict,
                        config: dict,
                        bucket: str) -> int:
    """
    returns the label of the user input
    :param user_input: a dictionary that contains
        fields for the clustering model
    :param config: a dictionary that contains
        s3 path to model object
        file path to model object
        s3 path to the average and sd
        file path to the average and sd
    :param bucket: s3 bucket name
    :return: an integer label
    """
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

    # pd df of tests data
    test = pd.DataFrame([data], columns=std_columns)

    pred_label = kmeans.predict(test)[0]
    return pred_label
