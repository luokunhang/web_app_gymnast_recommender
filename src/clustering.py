import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

from src import util

from sklearn.base import BaseEstimator
import pandas as pd


def create_model_women(filename: str) -> None:
    df = pd.read_csv(filename)
    df = pre_processing_women(df)
    filename = 'data/external/women_gym_model.sav'
    util.save_model(training(df), filename)
    util.upload_to_s3(filename, f"avc-project-data/{filename}")


def pre_processing_women(df: pd.DataFrame) -> pd.DataFrame:
    # standardizing columns
    for i in ['Vault', 'Uneven Bars', 'Balance Beam', 'Floor Exercise']:
        df[i] = (df[i] - df[i].mean()) / df[i].std()

    # centering at mean for rows
    df['mean'] = df[['Vault', 'Uneven Bars', 'Balance Beam', 'Floor Exercise']].mean(axis=1)
    df['vault'] = df['Vault'] - df['mean']
    df['bars'] = df['Uneven Bars'] - df['mean']
    df['beam'] = df['Balance Beam'] - df['mean']
    df['floor'] = df['Floor Exercise'] - df['mean']

    return df


def training(df: pd.DataFrame) -> BaseEstimator:
    dimensions = ['vault', 'bars', 'beam', 'floor']
    kmeans = KMeans(n_clusters=6, random_state=42).fit(df[dimensions])
    gymnast_labels = pd.DataFrame(df['Gymnast'], kmeans.labels)
    save_labels_women(kmeans, df['Gymnast'])
    return kmeans


def save_labels_women(kmeans: BaseEstimator, df: pd.DataFrame) -> None:
    labels_dict = {}
    for i in range(df.shape[0]):
        labels_dict[df.loc[i, 'Gymnast']] = str(kmeans.labels_[i])

    with open("data/external/labels_women.json", "w") as f:
        json.dump(labels_dict, f)

    # save it to s3
    util.upload_to_s3("data/external/labels_women.json", "avc-project-data/labels_women.json")

