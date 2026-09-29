"""
Fabrique des pipelines d'envoi des prédictions.

Deux variantes sont construites, avec le même nœud et les mêmes entrées, mais
une table de destination différente :
    - « prod » : écriture dans ``output_table_prod`` (Azure SQL
      ``dbo.training_table_prod``) ;
    - « pprd » : écriture dans ``output_table_pprd`` (pré-production).

Ces pipelines supposent que le modèle (``model_temperature``) et les données
nettoyées (``cleaned_data_prod``) existent déjà dans le catalogue Kedro.
"""

from kedro.pipeline import Pipeline, node

from .nodes import predict


def create_sending_data_pipeline(**kwargs) -> dict:
    """Construit les pipelines d'envoi des prédictions.

    Args:
        **kwargs: arguments additionnels transmis par Kedro (ignorés ici).

    Returns:
        dict: dictionnaire « nom de variante -> Pipeline » avec les clés
        ``prod`` et ``pprd``.
    """
    # Variante production
    prod_pipeline = Pipeline(
        [
            node(
                # Entrées : modèle entraîné, données IoT nettoyées et features
                predict,
                inputs=["model_temperature", "cleaned_data_prod", "params:features"],
                outputs="output_table_prod",
                name="send_prod_data"
            )
        ],
        tags=["send_data_prod"]
    )

    # Variante pré-production (mêmes entrées, table de sortie différente)
    pprd_pipeline = Pipeline(
        [
            node(
                predict,
                inputs=["model_temperature", "cleaned_data_prod", "params:features"],
                outputs="output_table_pprd",
                name="send_pprd_data"
            )
        ],
        tags=["send_data_pprd"]
    )

    return {
        "prod": prod_pipeline,
        "pprd": pprd_pipeline
    }
