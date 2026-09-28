"""
Fabrique des pipelines de data engineering.

Deux variantes sont construites :
    - « dev »  : lecture des données historiques (JSON) puis nettoyage ;
    - « prod » : nettoyage des messages IoT issus du message broker.

Les fonctions métier (nœuds) sont importées depuis ``nodes.py``.
"""

import pandas as pd
import os
from pathlib import Path
from kedro.pipeline import Pipeline, node
from .nodes import load_train_data, clean_data, clean_data_prod


def create_pipeline(**kwargs) -> dict:
    """Construit les pipelines de data engineering.

    Args:
        **kwargs: arguments additionnels transmis par Kedro (ignorés ici).

    Returns:
        dict: dictionnaire « nom de variante -> Pipeline » contenant les clés
        ``dev`` et ``prod``.
    """
    # Variante développement :
    #   raw_data -> historical_data -> cleaned_data
    # `raw_data` correspond au fichier JSON historique déclaré dans catalog.yml
    dev_pipeline = Pipeline(
        [
            node(
                load_train_data,
                "raw_data",
                outputs="historical_data",
                name="historical_data"
            ),
            node(
                # Nettoyage : température >= 30 °C et calcul du ratio
                clean_data,
                "historical_data",
                outputs="cleaned_data",
                name="cleaning_data"
            ),
        ],
        tags=["de_dev"]
    )

    # Variante production : nettoyage des messages du broker IoT
    #   message_broker -> cleaned_data_prod
    prod_pipeline = Pipeline(
        [
            node(
                clean_data_prod,
                inputs="message_broker",
                outputs="cleaned_data_prod",
                name="cleaning_data_prod",
            ),
        ],
        tags=["de_prod"]
    )

    return {
        "dev": dev_pipeline,
        "prod": prod_pipeline
    }

# ---------------------------------------------------------------------------
# Code historique commenté : ancien enchaînement autonome (exécution hors
# Kedro) qui lisait directement le fichier JSON local puis le nettoyait.
# ---------------------------------------------------------------------------
#ROOT_DIR = Path(__file__).resolve().parents[4]
#file_path = ROOT_DIR / "data" / "raw" / "IntroMLops-1.json"

#def workflow_engineering(file_path: Path) -> pd.DataFrame:
#    # import dataframe
#    dataframe = pd.read_json(file_path)
#    #print(dataframe.columns)
#    cleaned_data = clean_data(dataframe)
#    #print(cleaned_data)
#    #cleaned_data.info()
#    #print("Process completed for raspberry-temperature!")
#    return cleaned_data
#
#if __name__ == "__main__":
#    workflow(file_path)

