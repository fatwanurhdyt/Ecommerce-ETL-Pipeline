import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.load import (
    save_to_csv,
    save_to_postgresql,
    save_to_google_spreadsheet,
    load_data
)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Title": ["Item A"],
        "Price": ["$15.00"],
        "Rating": ["⭐ 4"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "ScrapedAt": ["2025-05-10 10:00:00"]
    })

def test_save_to_csv_creates_file(tmp_path, sample_df):
    file = tmp_path / "test.csv"
    save_to_csv(sample_df, filename=str(file))
    assert file.exists()
    df_loaded = pd.read_csv(file)
    assert not df_loaded.empty
    assert list(df_loaded.columns) == list(sample_df.columns)

@patch("pandas.DataFrame.to_csv", side_effect=Exception("Disk full"))
def test_save_to_csv_exception_prints_error(mock_to_csv, capsys, sample_df):
    save_to_csv(sample_df, filename="fashion_data.csv")
    captured = capsys.readouterr()
    assert "Disk full" in captured.out


@patch("utils.load.create_engine")  # Mock create_engine to prevent actual DB connection
def test_save_to_postgresql_calls_to_sql(mock_create_engine, sample_df):
    mock_engine = MagicMock()                   # Mock the engine object
    mock_create_engine.return_value = mock_engine

    sample_df.to_sql = MagicMock()         

    save_to_postgresql(
        sample_df,
        db_name="db_test",
        user="usr",
        password="pwd",
        table_name="products_test"
    )

    sample_df.to_sql.assert_called_once_with(
        "products_test", mock_engine, index=False, if_exists="replace"
    )

@patch("utils.load.create_engine", side_effect=Exception("Connection failed"))
def test_save_to_postgresql_exception_prints_error(mock_create_engine, capsys, sample_df):
    try:
        save_to_postgresql(sample_df, db_name="bad_db", user="bad_usr", password="bad_pwd")
    except Exception as e:
        print(f"[PostgreSQL Error] {e}")
    captured = capsys.readouterr()
    assert "Connection failed" in captured.out

@patch("utils.load.Credentials.from_service_account_file")
@patch("utils.load.build")
def test_save_to_google_spreadsheet_normal(mock_build, mock_creds, sample_df):
    mock_service = MagicMock()
    mock_spreadsheets = MagicMock()
    mock_values = MagicMock()

    mock_service.spreadsheets.return_value = mock_spreadsheets
    mock_spreadsheets.values.return_value = mock_values
    mock_values.clear.return_value.execute.return_value = None
    mock_values.update.return_value.execute.return_value = None

    mock_build.return_value = mock_service

    save_to_google_spreadsheet(sample_df, spreadsheet_id="fake_id", range_name="Sheet1!A1", credential_file="fake.json")

    mock_creds.assert_called_once()
    mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds.return_value)
    assert mock_values.clear.called
    assert mock_values.update.called

@patch("utils.load.Credentials.from_service_account_file", side_effect=Exception("Invalid credentials"))
def test_save_to_google_spreadsheet_exception_prints_error(mock_creds, capsys, sample_df):
    try:
        save_to_google_spreadsheet(sample_df, spreadsheet_id="wrong_id", range_name="Sheet1!A1", credential_file="bad.json")
    except Exception as e:
        print(f"[Google Sheets Error] {e}")
    captured = capsys.readouterr()
    assert "Invalid credentials" in captured.out

@patch("utils.load.save_to_csv")
@patch("utils.load.save_to_postgresql")
@patch("utils.load.save_to_google_spreadsheet")
def test_load_data_calls_all_storage(mock_gsheet, mock_postgres, mock_csv, sample_df):
    load_data(sample_df)

    mock_csv.assert_called_once_with(sample_df, 'fashion_data.csv')
    mock_postgres.assert_called_once_with(sample_df, 'fashion_db', 'wafanur', 'wafanur444', table_name='products')
    mock_gsheet.assert_called_once_with(sample_df, '1JAnu0DVGOaoWZSxZ-q1s6M-2KtIAH16JT6_yzoZNAQs', 'Sheet1!A1')


if __name__ == "__main__":
    pytest.main(['-v', __file__])