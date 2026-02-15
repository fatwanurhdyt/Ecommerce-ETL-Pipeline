import pandas as pd
from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# save to csv
def save_to_csv(df: pd.DataFrame, filename: str = 'fashion_data.csv'):
    try:
        df.to_csv(filename, index=False)
        print(f"{filename} successfully saved")
    except Exception as e:
        print(f"Failed to save data to CSV: {e}")

# save to postgresql
def save_to_postgresql(
    df: pd.DataFrame,
    db_name: str = 'fashion_db',       
    user: str = 'wafanur',             
    password: str = 'wafanur444',    
    host: str = 'localhost',
    port: int = 5432,
    table_name: str = 'products'
):
    try:
        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        print(f"'{table_name}' successfully saved to database '{db_name}'")
    except Exception as e:
        print(f"Failed to save '{table_name}' to database '{db_name}': {e}")


# save to google sheets
def save_to_google_spreadsheet(
    df: pd.DataFrame,
    spreadsheet_id: str = '1JAnu0DVGOaoWZSxZ-q1s6M-2KtIAH16JT6_yzoZNAQs',
    range_name: str = 'Sheet1!A1',
    credential_file: str = 'etl-fashion-project-460320-9dd4cb557cc2.json'
):
    try:
        creds = Credentials.from_service_account_file(
            credential_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=creds)

        # clear spreadsheets
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()

        # format data
        values = [df.columns.tolist()] + df.values.tolist()
        body = {'values': values}

        # input data to spreadsheets
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()

        print(f"Successfully saved to Spreadsheet.")
    except Exception as e:
        print(f"Failed to save to Spreadsheets: {e}")

# load to all storages
def load_data(
    df: pd.DataFrame,
    filename_csv: str = 'fashion_data.csv',
    db_name: str = 'fashion_db',
    user: str = 'wafanur',
    password: str = 'wafanur444',
    spreadsheet_id: str = '1JAnu0DVGOaoWZSxZ-q1s6M-2KtIAH16JT6_yzoZNAQs',
    range_name: str = 'Sheet1!A1',
    table_name: str = 'products'
):
    save_to_csv(df, filename_csv)
    save_to_postgresql(df, db_name, user, password, table_name=table_name)
    save_to_google_spreadsheet(df, spreadsheet_id, range_name)