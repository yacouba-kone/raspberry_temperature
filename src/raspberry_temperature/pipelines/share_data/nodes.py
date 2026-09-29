# ---------------------------------------------------------------------------
# Nœud du pipeline de partage des données (share_data).
#
# Ce module applique le modèle entraîné aux données nettoyées de production
# afin de produire le DataFrame de prédictions qui sera écrit en base.
# ---------------------------------------------------------------------------

import logging
from typing import Any, Dict
from typing import Dict, List
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import datetime


def predict(regressor: LinearRegression, x_test: np.ndarray, features: List) -> pd.DataFrame:
    """Calculate the coefficient of determination and log the result.

        Args:
            regressor: Trained model.
            x_test: Testing data of independent features.
            features: Testing data for price.

    """
    # NB : la docstring historique évoque le coefficient de détermination, mais
    # la fonction retourne en réalité le DataFrame des prédictions.
    log = logging.getLogger(__name__)

    # Prédictions du modèle sur les seules colonnes attendues (`features`),
    # aplaties en un vecteur 1D
    y_pred = regressor.predict(x_test[features]).flatten()

    # Construction du DataFrame de sortie au format attendu par la table SQL
    df_pred = pd.DataFrame(y_pred, columns=["y_pred"])
    # Ajouter la colonne Time avec timestamp actuel
    df_pred["Time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f'valeur prédicte est: {y_pred}')

    return df_pred

