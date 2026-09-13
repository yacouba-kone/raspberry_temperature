
import logging
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import datetime
logging.basicConfig(level=logging.INFO)
import numpy as np
from raspberry_temperature.pipelines.data_sciences.nodes import split_data
from raspberry_temperature.pipelines.data_sciences.nodes import (
    split_data,
    train_model,
    scoring,
)
def test_split_data():
    X = np.array([[1, 10],[2, 20],[3, 30],[4, 40],[5, 50],[6, 60],
        [7, 70],[8, 80],[9, 90],[10, 100],])

    y = np.array([
        1, 2, 3, 4, 5,
        6, 7, 8, 9, 10,
    ])

    X_train, X_test, y_train, y_test = split_data(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    assert len(X_train) == 8
    assert len(X_test) == 2

    assert len(y_train) == 8
    assert len(y_test) == 2

# tests/raspberry_temperature/pipelines/data_sciences/test_nodes.py

def test_split_data():

    X = np.array([[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],])

    y = np.array([2,4,6,8,10,12,14,16,18,20,])

    X_train, X_test, y_train, y_test = split_data(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    assert len(X_train) == 8
    assert len(X_test) == 2
    assert len(y_train) == 8
    assert len(y_test) == 2


def test_train_model():

    X_train = np.array([[1],[2],[3],[4],[5],])
    y_train = np.array([2,4,6,8,10,])

    params = {
        "fit_intercept": True
    }
    model = train_model(True, X_train, y_train)

    assert model is not None
    assert hasattr(model, "coef_")
    assert hasattr(model, "intercept_")

    assert np.isclose(
        model.coef_[0],
        2.0,
    )

    assert np.isclose(
        model.intercept_,
        0.0,
    )


def test_scoring():

    X_train = np.array([[1],[2],[3],[4],[5],])
    y_train = np.array([2,4, 6,8,10,])

    X_test = np.array([[6],[7],[8],])
    y_test = np.array([12,14,16,])

    params = {
        "fit_intercept": True
    }
    model = train_model(True, X_train, y_train)

    score = scoring(
        model,
        X_test,
        y_test,
    )

    assert np.isclose(score["r2_score"], 1.0)


def test_train_model_coefficients():
    X_train = np.array([[1],[2],[3],[4],[5],])
    y_train = np.array([2,4, 6,8,10,])

    params = {
        "fit_intercept": True
    }
    model = train_model(True, X_train, y_train)

    assert np.isclose(model.coef_[0], 2.0)
    assert np.isclose(model.intercept_, 0.0)

    


