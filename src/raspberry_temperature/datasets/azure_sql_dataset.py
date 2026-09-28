from pathlib import Path

import pandas as pd
from kedro.io import AbstractDataset

from raspberry_temperature.azure_sql import create_azure_sql_engine


class AzureSQLTableDataset(AbstractDataset[pd.DataFrame, None]):

    def __init__(
        self,
        table_name: str,
        if_exists: str = "append",
    ):
        self.table_name = table_name
        self.if_exists = if_exists

    def _load(self) -> pd.DataFrame:
        engine = create_azure_sql_engine()

        query = f"SELECT * FROM dbo.{self.table_name}"

        return pd.read_sql(query, engine)

    def _save(self, data: pd.DataFrame) -> None:
        engine = create_azure_sql_engine()

        data.to_sql(
            self.table_name,
            engine,
            schema="dbo",
            if_exists=self.if_exists,
            index=False,
        )

    def _describe(self) -> dict:
        return {
            "table_name": self.table_name,
            "if_exists": self.if_exists,
        }