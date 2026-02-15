import pandas as pd
import numpy as np

def clean_and_transform(product_data: pd.DataFrame) -> pd.DataFrame:
    if isinstance(product_data, list):
        product_data = pd.DataFrame(product_data)
        
    if product_data.empty:
        print("[Transform] Product data is empty, returning empty DataFrame.")
        return pd.DataFrame(columns=['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'ScrapedAt'])

    try:
        df = pd.DataFrame(product_data)

        # normalize column names
        df.columns = [col.strip() for col in df.columns]

        # filter invalid data 
        if 'Title' in df.columns:
            df = df[~df['Title'].str.lower().str.contains('unknown', na=False)]

        # convert price column to float (1$ = 16,000 IDR)
        df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['Price'].replace('', np.nan)
        df.dropna(subset=['Price'], inplace=True)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df.dropna(subset=['Price'], inplace=True)
        df['Price'] = (df['Price'] * 16000).round(1)

        # convert rating column to float
        df['Rating'] = df['Rating'].astype(str).str.extract(r'(\d+\.\d+|\d+)')[0]
        df['Rating'].replace('', np.nan)
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').astype(float)
        df.dropna(subset=['Rating'], inplace=True)

        # convert colors column to integer
        df['Colors'] = df['Colors'].astype(str).str.extract(r'(\d+)')[0]
        df['Colors'].replace('', np.nan)
        df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce')
        df.dropna(subset=['Colors'], inplace=True)

        # convert size and gender columns to string
        df['Size'] = df['Size'].astype(str).str.replace(r'Size:\s*', '', regex=True)
        df['Gender'] = df['Gender'].astype(str).str.replace(r'Gender:\s*', '', regex=True)

        # convert scrapedat column to datetime 
        df['ScrapedAt'] = pd.to_datetime(df['ScrapedAt'], errors='coerce')
        df.dropna(subset=['ScrapedAt'], inplace=True)
        df['ScrapedAt'] = df['ScrapedAt'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str.slice(stop=-3)

        # drop duplicates and missing values
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

    except Exception as e:
        print(f"[Transform] Error occurred during data transformation: {e}")
        return pd.DataFrame()

    return df