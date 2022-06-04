"""
engineers features, trains a span of models,
and chooses a final model for production
"""
import json
import logging
import pickle
from typing import Tuple

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score

logger = logging.getLogger(__name__)


def pre_processing(config: dict) -> Tuple[pd.DataFrame, list[str]]:
    """
    calculates features based on the clean dataset
    :param config: a dictionary that contains
        file path tp clean data
        features to train on
        file path to save average and sd of columns
    :return: None
    """
    data = pd.read_csv(config['filepath']['data'])
    # standardizing columns
    columns = config['clustering']['features']
    data, avg_sd_dict = standardize(data, columns)

    with open(config['filepath']['avg_sd'], "w+", encoding='utf8') as file:
        json.dump(avg_sd_dict, file)

    std_columns = [i + '_std' for i in columns]

    # centering at mean for rows
    data = center(data, std_columns)
    return data, std_columns


def standardize(data: pd.DataFrame,
                columns: list[str]
                ) -> Tuple[pd.DataFrame, dict]:
    """
    standardizes each column as sample z-scores
    :param data: the dataframe to begin with
    :param columns: columns to calculate z-scores
    :return: updated dataframe, a dictionary that
        stores the averages and standard deviations of
        target columns
    """
    if data.isnull().values.any():
        logger.error('NA values in the data.')
        raise ValueError
    avg_sd_dict = {}
    try:
        for i in columns:
            avg = data[i].mean(skipna=False)
            std = data[i].std(skipna=False)
            if not std:
                raise ValueError
            avg_sd_dict[i + '_avg'] = avg
            avg_sd_dict[i + '_sd'] = std
            data[i + '_std'] = (data[i] - avg) / std
        return data, avg_sd_dict
    except KeyError as err:
        logger.error('Unknown column name not existent'
                     'in the dataframe. %s', err)
        raise err
    except ValueError as err:
        logger.error('The standard deviation cannot'
                     'be calculated. %s', err)
        raise err


def center(data: pd.DataFrame,
           std_columns: list[str]) -> pd.DataFrame:
    """
    makes each row mean-centered
    :param data: the dataframe to begin with
    :param std_columns: columns to operate on
    :return: an updated dataframe whose columns
        are mean-centered row-wise
    """
    if data.isnull().values.any():
        logger.error('NA values in the data.')
        raise ValueError
    try:
        data['mean'] = data[std_columns].mean(axis=1,
                                              skipna=False)
        for i in std_columns:
            data[i] = data[i] - data['mean']
    except KeyError as err:
        logger.error('Unknown column name not existent'
                     'in the dataframe. %s', err)
        raise err
    return data


def try_models(data: pd.DataFrame,
               std_columns: list[str],
               config: dict) -> None:
    """
    explores K-means clustering models with
    a range of K
    :param data: the training data dataframe
    :param std_columns: columns to operate on
    :param config: a dictionary that contains
        min number of clusters to try
        max number of clusters to try
        random state for the model
        file path to save the model diagnostics
    :return: None
    """
    min_clusters = config['clustering']['try_models']['min_clusters']
    max_clusters = config['clustering']['try_models']['max_clusters']
    random_state = config['clustering']['random_state']
    with open(config['filepath']['model_diagnostics'], 'w+',
              encoding='utf8') as file:
        for i in range(min_clusters, max_clusters+1):
            logger.debug('Training K-means with %i clusters.', i)
            kmeans = KMeans(n_clusters=i,
                            random_state=random_state).fit(data[std_columns])
            # computes the pseudo F
            pseudo_f = calinski_harabasz_score(data[std_columns], kmeans.labels_)

            # computes the pseudo R-squared
            global_mean = data[std_columns].mean(axis=0)
            total_ss = 0
            between_ss = 0
            for j in range(data.shape[0]):
                total_ss += ((data.loc[j, std_columns] - global_mean) ** 2).sum()
                between_ss += ((data.loc[j, std_columns] -
                                kmeans.cluster_centers_[kmeans.labels_[j]]) ** 2).sum()
            file.write(f'{i} cluster(s), pseudo F score: {pseudo_f}, ')
            file.write(f'pseudo R-squared: {between_ss/total_ss}.\n')


def get_model(data: pd.DataFrame,
              std_columns: list[str],
              config: dict) -> None:
    """
    trains the finalized model and saves it to the repo
    :param data: the training data dataframe
    :param std_columns: columns to train with
    :param config: a dictionary that contains
        number of clusters
        random state for the model
        file path to save the labeled data
        file path to save the model object
    :return: None
    """
    n_clusters = config['clustering']['final_model']['n_clusters']
    random_state = config['clustering']['random_state']
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(data[std_columns])
    data['label'] = kmeans.labels_
    data.to_csv(config['filepath']['labeled_data'], index=False)
    logger.info('Labeled data has been saved in this repo.')
    with open(config['filepath']['model'], "wb") as file:
        pickle.dump(kmeans, file)
        logger.info('Model object has been saves in this repo.')
