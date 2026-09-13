
import logging
import pandas as pd 
logging.basicConfig(level=logging.INFO)


def clean_data(raspberry_data: pd.DataFrame) -> pd.DataFrame:

    clean_df: pd.DataFrame = raspberry_data.copy()
    log=logging.getLogger(__name__)
    clean_df = clean_df[clean_df['temperature'] >= 30.]
    clean_df ['ratio'] = clean_df['intensity'] / clean_df['humidity']
    #print(clean_df)
    #log.info(f"taille dataframe apres nettoyage: {clean_df}")
    return clean_df

