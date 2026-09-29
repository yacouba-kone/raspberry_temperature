"""
Dataset Kedro personnalisé pour Azure SQL Database.

Kedro ne fournit pas nativement de dataset authentifié par token Entra ID : ce
module comble ce manque en s'appuyant sur `create_azure_sql_engine`.
Il est référencé dans `conf/base/catalog.yml` sous la clé `output_table_prod`.
"""

from pathlib import Path

import pandas as pd
from kedro.io import AbstractDataset

from raspberry_temperature.azure_sql import create_azure_sql_engine


class AzureSQLTableDataset(AbstractDataset[pd.DataFrame, None]):
    """Dataset Kedro de lecture/écriture d'une table Azure SQL.

    Le type générique `AbstractDataset[pd.DataFrame, None]` indique que le
    dataset charge un DataFrame pandas et n'expose pas de données sauvegardées
    exploitables (`_save` retourne toujours `None`).
    """

    def __init__(
        self,
        table_name: str,
        if_exists: str = "append",
    ):
        """Initialise le dataset.

        Args:
            table_name: nom de la table Azure SQL visée (sans le schéma, le
                schéma `dbo` étant appliqué par défaut).
            if_exists: comportement lors de l'écriture, transmis à
                `pandas.DataFrame.to_sql` : "append", "replace" ou "fail".
        """
        self.table_name = table_name
        self.if_exists = if_exists

    def _load(self) -> pd.DataFrame:
        """Charge l'intégralité de la table dans un DataFrame."""
        # Un nouveau moteur est créé à chaque appel afin de rafraîchir le token
        # Entra ID (celui-ci expire au bout d'une heure environ)
        engine = create_azure_sql_engine()

        # Lecture complète de la table : le schéma est fixé à `dbo`
        query = f"SELECT * FROM dbo.{self.table_name}"

        return pd.read_sql(query, engine)

    def _save(self, data: pd.DataFrame) -> None:
        """Écrit le DataFrame fourni dans la table Azure SQL.

        Args:
            data: DataFrame à persister (colonnes `y_pred` et `Time` pour le
                cas d'usage actuel).
        """
        engine = create_azure_sql_engine()

        data.to_sql(
            self.table_name,
            engine,
            schema="dbo",
            if_exists=self.if_exists,
            # L'index pandas n'a pas de sens en base : il n'est pas écrit
            index=False,
        )

    def _describe(self) -> dict:
        """Décrit le dataset (utilisé par Kedro pour la journalisation)."""
        return {
            "table_name": self.table_name,
            "if_exists": self.if_exists,
        }