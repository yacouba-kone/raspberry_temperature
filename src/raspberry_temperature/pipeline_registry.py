"""
Registre des pipelines du projet.

Kedro appelle `register_pipelines()` du `pipeline_registry.py` pour découvrir
les pipelines disponibles. Les pipelines de base sont construits dans les
modules `pipelines/*/pipeline.py`, puis assemblés et combinés ici.
"""

from kedro.pipeline import Pipeline

from raspberry_temperature.pipelines.share_data import pipeline as share
from raspberry_temperature.pipelines.data_engineering import pipeline as de
from raspberry_temperature.pipelines.data_sciences import pipeline as ds 


def register_pipelines() -> dict[str, Pipeline]:
    """Assemble et enregistre tous les pipelines du projet.

    Returns:
        dict[str, Pipeline]: dictionnaire « nom du pipeline -> objet Pipeline ».
        La clé ``__default__`` correspond au pipeline lancé par défaut
        (`kedro run` sans option `--pipeline`).
    """

    # Pipelines de data engineering : le dictionnaire contient les variantes
    # "dev" (données historiques) et "prod" (messages IoT)
    data_engineering_dict = de.create_pipeline()

    # Pipelines d'envoi des prédictions vers Azure SQL (prod / pré-prod)
    send_data_pipelines_dict = share.create_sending_data_pipeline()

    # Variante dev : nettoyage des données historiques
    de_pipeline = data_engineering_dict['dev']

    # Variante prod du nettoyage des messages IoT
    de_pipeline_prod = data_engineering_dict['prod']#.decorate(log_running_time)

    # Pipeline d'entraînement du modèle de régression linéaire
    training_pipeline = ds.create_training_pipeline()

    # Écriture des prédictions dans `training_table_prod` (production)
    send_data_pipeline_prod = send_data_pipelines_dict['prod']#.decorate(log_running_time)

    # Écriture des prédictions dans la table de pré-production
    send_data_pipeline_pprd = send_data_pipelines_dict['pprd']#.decorate(log_running_time)


    return {
        # Nettoyage des données historiques (développement)
        "de": de_pipeline,
        # Entraînement du modèle
        "training": training_pipeline,
        # Production : nettoyage prod puis écriture des prédictions
        "prod": de_pipeline_prod + send_data_pipeline_prod,
        # Pré-production : nettoyage prod puis écriture des prédictions
        "pprd": de_pipeline_prod + send_data_pipeline_pprd,
        # Pipeline par défaut : data engineering dev + entraînement
        "__default__": de_pipeline + training_pipeline,
    }

