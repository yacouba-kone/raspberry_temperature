from raspberry_temperature.pipelines.data_engineering.nodes import clean_data#, transform_data, load_data
import pandas as pd
import os
from pathlib import Path

#ROOT_DIR = Path(__file__).resolve().parents[4]
#file_path = ROOT_DIR / "data" / "raw" / "IntroMLops-1.json"

def workflow_engineering(file_path: Path) -> pd.DataFrame:
    # import dataframe
    dataframe = pd.read_json(file_path)
    #print(dataframe.columns)
    cleaned_data = clean_data(dataframe)
    #print(cleaned_data)
    #cleaned_data.info()
    #print("Process completed for raspberry-temperature!")
    return cleaned_data

#if __name__ == "__main__":
#    workflow(file_path)

