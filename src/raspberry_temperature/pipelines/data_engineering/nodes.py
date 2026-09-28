
# ---------------------------------------------------------------------------
# Nœuds (fonctions métier) du pipeline de data engineering.
#
# Ce module expose trois fonctions appelées par Kedro via des `node` :
#   - load_train_data  : chargement des mesures historiques (pipeline « dev »)
#   - clean_data       : nettoyage des mesures historiques (pipeline « dev »)
#   - clean_data_prod  : nettoyage des messages IoT (pipeline « prod »)
#
# Le décorateur `log_running_time` (ci-dessous) mesure le temps d'exécution.
# ---------------------------------------------------------------------------

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

    # `wraps` préserve le nom, la docstring et les métadonnées de la fonction
    # décorée (indispensable pour que Kedro identifie correctement le nœud)
    @wraps(func)
    def with_time(*args, **kwargs):
        log = logging.getLogger(__name__)
        t_start = time.time()
        # Appel effectif de la fonction métier
        result = func(*args, **kwargs)
        t_end = time.time()
        elapsed = t_end - t_start
        # Journalisation du temps d'exécution sous la forme :
        # « Running <nom de la fonction> took <durée> seconds »
        log.info("Running %r took %.2f seconds", func.__name__, elapsed)
        return result

    return with_time

# Décorateur désactivé : à décommenter pour tracer le temps d'exécution
#@log_running_time

def load_train_data(json_data) -> pd.DataFrame:
    """
    Load and normalize training data.
    """
    # Copie du DataFrame d'entrée pour ne pas altérer le dataset chargé par Kedro
    df = json_data.copy()

    # Affichage de contrôle (contenu puis types des colonnes)
    print(df)
    print(df.dtypes)

    return df

@log_running_time
def clean_data(raspberry_data: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les mesures historiques du Raspberry Pi (pipeline « dev »).

    Le traitement applique deux règles métier :
        1. ne conserver que les températures supérieures ou égales à 30 °C ;
        2. créer la variable explicative `ratio = intensity / humidity`.

    Args:
        raspberry_data: données brutes chargées depuis le fichier JSON.

    Returns:
        pd.DataFrame: copie filtrée, enrichie de la colonne `ratio`.
    """

    clean_df: pd.DataFrame = raspberry_data.copy()
    log=logging.getLogger(__name__)
    # Règle 1 : filtre sur la température (seuil métier de 30 °C)
    clean_df = clean_df[clean_df['temperature'] >= 30.]
    # Règle 2 : nouvelle variable explicative utilisée par le modèle
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
            # Message illisible : on retourne un DataFrame vide plutôt que de
            # faire échouer l'ensemble du pipeline de production
            log.error("Échec du décodage du JSON fourni.")
            return pd.DataFrame()
    else:
        data = raw_messages

    # 2. Harmonisation sous forme de liste pour Pandas
    # (un dictionnaire seul devient une liste d'une seule observation)
    if isinstance(data, dict):
        data = [data]

    # 3. Création du DataFrame
    df = pd.DataFrame(data)

    # 4. Gestion de la colonne temporelle EventProcessedUtcTime
    # Si Azure ne l'a pas encore injectée, on génère un horodatage UTC courant
    if "EventProcessedUtcTime" not in df.columns:
        df["EventProcessedUtcTime"] = pd.Timestamp.now(tz="UTC")
    else:
        # Conversion explicite en datetime UTC pour uniformiser les types
        df["EventProcessedUtcTime"] = pd.to_datetime(df["EventProcessedUtcTime"], utc=True)

    # 5. Filtrage des colonnes requises
    # On ne garde que les colonnes utiles au modèle, dans un ordre fixe
    required_cols = ["EventProcessedUtcTime", "temperature", "humidity", "intensity"]
    df_filtered = df[required_cols].copy()

    # 6. Traitement et calculs (Filtrage humidité >= 60% et calcul du ratio)
    # NB : le seuil réellement appliqué est 30 (le commentaire historique
    # ci-dessus mentionnait 60 %)
    clean_df = df_filtered[df_filtered["humidity"] >= 30.0].copy()

    # Calcul du ratio sans warning Pandas SettingWithCopyWarning
    clean_df["ratio"] = clean_df["intensity"] / clean_df["humidity"]

    # Journalisation du nombre de lignes conservées après nettoyage
    log.info(f"Taille du dataframe après nettoyage : {len(clean_df)}")
    return clean_df

