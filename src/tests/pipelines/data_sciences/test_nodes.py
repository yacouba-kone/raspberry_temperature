from raspberry_temperature.pipelines.data_science.nodes import split_data, predict
import pandas as pd
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression


class Model_couple_test(LinearRegression):
    def predict(self, df: pd.DataFrame) -> float:
        return df.sum(axis=1)[0]


def test_split_data():
    # Given
    given_df = pd.DataFrame({
        'feature': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'label': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    parameters = {
        'feature': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'label': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    }
    features = ['feature']
    label = 'label'
    # When
    actual_splits = split_data(given_df, features, label)
    # Then
    expected_x_train = pd.DataFrame({'feature': [10, 2, 7, 8, 4, 1, 6]})
    expected_x_test = pd.DataFrame({'feature': [3, 9, 5]}, index=[2, 8, 4])
    expected_y_train = pd.Series([100, 20, 70, 80, 40, 10, 60])
    expected_y_test = pd.Series([30, 90, 50], index=[2, 8, 4])

    expected_splits = [
        expected_x_train,
        expected_x_test,
        expected_y_train,
        expected_y_test
    ]

    for actual, expected in zip(actual_splits, expected_splits):
        assert actual.shape == expected.shape

