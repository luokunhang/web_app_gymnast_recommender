import json
import pickle
from sklearn.cluster import KMeans
from typing import Tuple
import pandas as pd
from sklearn.metrics import calinski_harabasz_score


def pre_processing(config: dict) -> Tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(config['filepath']['data'])
    # standardizing columns
    avg_sd_dict = dict()
    columns = config['clustering']['features']
    for i in columns:
        avg = df[i].mean()
        sd = df[i].std()
        avg_sd_dict[i + '_avg'] = avg
        avg_sd_dict[i + '_sd'] = sd
        df[i + '_std'] = (df[i] - avg) / sd

    with open(config['filepath']['avg_sd'], "w+") as file:
        json.dump(avg_sd_dict, file)

    std_columns = [i + '_std' for i in columns]

    # centering at mean for rows
    df['mean'] = df[std_columns].mean(axis=1)
    for i in std_columns:
        df[i] = df[i] - df['mean']
    return df, std_columns


def try_models(df: pd.DataFrame,
               std_columns: list[str],
               config: dict) -> None:
    min_clusters = config['clustering']['try_models']['min_clusters']
    max_clusters = config['clustering']['try_models']['max_clusters']
    random_state = config['clustering']['random_state']
    with open(config['filepath']['model_diagnostics'], 'w+') as file:
        for i in range(min_clusters, max_clusters+1):
            kmeans = KMeans(n_clusters=i, random_state=random_state).fit(df[std_columns])
            pseudo_f = calinski_harabasz_score(df[std_columns], kmeans.labels_)
            # add pseudo R2
            file.write(f'{i} cluster(s), pseudo F score: {pseudo_f}.\n')


def get_model(df: pd.DataFrame,
              std_columns: list[str],
              config: dict) -> None:
    n_clusters = config['clustering']['final_model']['n_clusters']
    random_state = config['clustering']['random_state']
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(df[std_columns])
    df['label'] = kmeans.labels_
    df.to_csv(config['filepath']['labeled_data'], index=False)
    with open(config['filepath']['model'], "wb") as f:
        pickle.dump(kmeans, f)
