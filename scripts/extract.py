import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def extract_data(path):
    logging.info("Extracting data...")
    df = pd.read_csv(path)
    logging.info(f"Rows: {len(df)}")
    return df