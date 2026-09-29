# ---------------------------------------------------------------------------
# Tests unitaires des nœuds de data sciences.
#
# Les tests suivent la convention « Given / When / Then ».
# ---------------------------------------------------------------------------

from raspberry_temperature.pipelines.data_sciences.nodes import split_data, predict
import pandas as pd
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression


class Model_couple_test(LinearRegression):
    """Faux modèle de test : `predict` renvoie la somme de la première ligne.

    Il permet de tester le nœud `predict` sans avoir à entraîner un vrai modèle.
    """

    def predict(self, df: pd.DataFrame) -> float:
        return df.sum(axis=1)[0]

def test_split_data():
    """Vérifie les tailles et les colonnes produites par `split_data`."""
    # Given : 10 observations avec une variable explicative et une cible
    given_df = pd.DataFrame({
        "feature": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "label": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    })

    features = ["feature"]
    label = "label"

    # When : découpage 70 % / 30 %
    x_train, x_test, y_train, y_test = split_data(
        given_df,
        features,
        label,
        test_size=0.3,
        random_state=42,
    )

    # Then : 7 lignes d'entraînement et 3 lignes de test, colonnes conservées
    assert len(x_train) == 7
    assert len(x_test) == 3
    assert len(y_train) == 7
    assert len(y_test) == 3

    assert list(x_train.columns) == ["feature"]
    assert list(x_test.columns) == ["feature"]
    assert list(y_train.columns) == ["label"]
    assert list(y_test.columns) == ["label"]

# ---------------------------------------------------------------------------
# Ancienne version commentée du même test : elle était écrite pour une API
# différente de `split_data` (liste de résultats, index conservés).
# ---------------------------------------------------------------------------
#def test_split_data():
#    # Given
#    given_df = pd.DataFrame({
#        'feature': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#        'label': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#    })
#    parameters = {
#        'feature': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#        'label': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#    }
#    features = ['feature']
#    label = 'label'
#    # When
#    actual_splits = split_data(given_df, features, label)
#    # Then
#    expected_x_train = pd.DataFrame({'feature': [10, 2, 7, 8, 4, 1, 6]})
#    expected_x_test = pd.DataFrame({'feature': [3, 9, 5]}, index=[2, 8, 4])
#    expected_y_train = pd.Series([100, 20, 70, 80, 40, 10, 60])
#    expected_y_test = pd.Series([30, 90, 50], index=[2, 8, 4])
#
#    expected_splits = [
#        expected_x_train,
#        expected_x_test,
#        expected_y_train,
#        expected_y_test
#    ]
#
#    for actual, expected in zip(actual_splits, expected_splits):
#        assert actual.shape == expected.shape

