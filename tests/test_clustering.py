import pandas as pd
import pytest

from src import clustering


def test_standardize():
    df_in = pd.DataFrame([[1.0, 3.0],
                          [3.0, 4.0],
                          [5.0, 5.0]],
                         columns=['first', 'second'])
    df_true = pd.DataFrame([[1.0, 3.0, -1.0, -1.0],
                            [3.0, 4.0, 0.0, 0.0],
                            [5.0, 5.0, 1.0, 1.0]],
                           columns=['first',
                                    'second',
                                    'first_std',
                                    'second_std'])
    dict_true = {
        'first_avg': 3,
        'first_sd': 2,
        'second_avg': 4,
        'second_sd': 1
    }

    df_out, dict_out = clustering.standardize(df_in,
                                              ['first', 'second'])
    assert(df_out.equals(df_true))
    assert(dict_out == dict_true)


def test_standardize_unknown_column():
    df_in = pd.DataFrame([[1.0, 3.0],
                          [3.0, 4.0],
                          [5.0, 5.0]],
                         columns=['first', 'second'])

    with pytest.raises(KeyError):
        clustering.standardize(df_in,
                               ['first', 'extra'])


def test_standardize_na_entry():
    df_in = pd.DataFrame([[1.0, None],
                          [3.0, 4.0],
                          [5.0, 5.0]],
                         columns=['first', 'second'])

    with pytest.raises(ValueError):
        clustering.standardize(df_in,
                               ['first', 'second'])


def test_standardize_no_variance():
    df_in = pd.DataFrame([[1.0, 4.0],
                          [3.0, 4.0],
                          [5.0, 4.0]],
                         columns=['first', 'second'])

    with pytest.raises(ValueError):
        clustering.standardize(df_in, ['first', 'second'])


def test_center():
    df_in = pd.DataFrame([[1.0, 2.0, 3.0, 4.0]],
                         columns=['a', 'b', 'c', 'd'])
    df_true = pd.DataFrame([[-1.5, -0.5, 0.5, 1.5, 2.5]],
                           columns=['a', 'b', 'c', 'd', 'mean'])

    df_out = clustering.center(df_in, ['a', 'b', 'c', 'd'])

    assert(df_out.equals(df_true))


def test_center_na_entry():
    df_in = pd.DataFrame([[1.0, 2.0, None]],
                         columns=['a', 'b', 'c'])

    with pytest.raises(ValueError):
        clustering.center(df_in, ['a', 'b', 'c'])


def test_center_unknown_column():
    df_in = pd.DataFrame([[1.0, 2.0, 3.0]],
                         columns=['a', 'b', 'c'])

    with pytest.raises(KeyError):
        clustering.center(df_in, ['a', 'b', 'c', 'd'])
