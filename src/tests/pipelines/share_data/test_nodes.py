from raspberry_temperature.pipelines.share_data.nodes import predict
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


class Model_couple_test(LinearRegression):
    def predict(self, df: pd.DataFrame) -> float:
        return df.sum(axis=1)[0]


def test_predict():
    # Given
    # Une seule observation pour simplifier :
    x_test_df = pd.DataFrame({'humidity': [61.0], 'intensity': [44.0], 'ratio': [0.7]}, index=[0])
    features = ['humidity', 'intensity', 'ratio']  # r2/mse seront calculés mais non vérifiés ici
    model = Model_couple_test()

    # When: la fonction attend des ndarrays → on lui passe .values
    df_pred = predict(model, x_test_df, features)

    # Then: vérifications de base