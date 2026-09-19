
import json
import logging
import pandas as pd 
logging.basicConfig(level=logging.INFO)
from typing import List, Any, Dict
import numpy as np
import re
from functools import wraps
from typing import Callable
import time
#from kedro.extras.datasets.pandas import JSONDataSet
#from kedro_datasets.json  import JSONDataset
#from kedro_datasets.pandas import CSVDataset

def log_running_time(func: Callable) -> Callable:
    """Decorator for logging node execution time.

        Args:
            func: Function to be executed.

        Returns:
            Decorator for logging the running time.

    """

    @wraps(func)
    def with_time(*args, **kwargs):
        log = logging.getLogger(__name__)
        t_start = time.time()
        result = func(*args, **kwargs)
        t_end = time.time()
        elapsed = t_end - t_start
        log.info("Running %r took %.2f seconds", func.__name__, elapsed)
        return result

    return with_time

#@log_running_time

def load_train_data(json_data) -> pd.DataFrame:
    """
    Load and normalize training data.
    """
    df = json_data.copy()

    print(df)
    print(df.dtypes)

    return df

@log_running_time
def clean_data(raspberry_data: pd.DataFrame) -> pd.DataFrame:

    clean_df: pd.DataFrame = raspberry_data.copy()
    log=logging.getLogger(__name__)
    clean_df = clean_df[clean_df['temperature'] >= 30.]
    clean_df ['ratio'] = clean_df['intensity'] / clean_df['humidity']
    #print(clean_df)
    log.info(f"taille dataframe apres nettoyage: {clean_df}")
    return clean_df


def clean_data_prod(raw_messages) -> pd.DataFrame:
    """
    Clean data from Azure Event Hub / IoT messages.

    Args:
        raw_messages: Source data (can be a JSON string, a dict, or a list of dicts/strings)
    Returns :
        Cleaned DataFrame
    """
    log = logging.getLogger(__name__)

    # 1. Conversion des messages bruts en structure Python (dict/list)
    if isinstance(raw_messages, str):
        try:
            data = json.loads(raw_messages)
        except json.JSONDecodeError:
            log.error("Échec du décodage du JSON fourni.")
            return pd.DataFrame()
    else:
        data = raw_messages

    # 2. Harmonisation sous forme de liste pour Pandas
    if isinstance(data, dict):
        data = [data]

    # 3. Création du DataFrame
    df = pd.DataFrame(data)

    # 4. Gestion de la colonne temporelle EventProcessedUtcTime
    # Si Azure ne l'a pas encore injectée, on génère un horodatage UTC courant
    if "EventProcessedUtcTime" not in df.columns:
        df["EventProcessedUtcTime"] = pd.Timestamp.now(tz="UTC")
    else:
        df["EventProcessedUtcTime"] = pd.to_datetime(df["EventProcessedUtcTime"], utc=True)

    # 5. Filtrage des colonnes requises
    required_cols = ["EventProcessedUtcTime", "temperature", "humidity", "intensity"]
    df_filtered = df[required_cols].copy()

    # 6. Traitement et calculs (Filtrage humidité >= 60% et calcul du ratio)
    clean_df = df_filtered[df_filtered["humidity"] >= 30.0].copy()

    # Calcul du ratio sans warning Pandas SettingWithCopyWarning
    clean_df["ratio"] = clean_df["intensity"] / clean_df["humidity"]

    log.info(f"Taille du dataframe après nettoyage : {len(clean_df)}")
    return clean_df

