import pandas as pd
import os
from pathlib import Path
from kedro.pipeline import Pipeline, node
from .nodes import load_train_data, clean_data, clean_data_prod


def create_pipeline(**kwargs):
    dev_pipeline = Pipeline(
        [
            node(
                load_train_data,
                "raw_data",
                outputs="historical_data",
                name="historical_data"
            ),
            node(
                clean_data,
                "historical_data",
                outputs="cleaned_data",
                name="cleaning_data"
            ),
        ],
        tags=["de_dev"]
    )

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

