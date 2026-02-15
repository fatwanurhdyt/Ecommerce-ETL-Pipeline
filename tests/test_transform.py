import pytest
import pandas as pd
import sys
import os

# directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.transform import clean_and_transform

def test_valid_transformation():
    data = {
        "Title": ["A", "B"],
        "Price": ["$5.00", "$10.00"],
        "Rating": ["⭐ 3", "⭐ 4"],
        "Colors": ["3 Colors", "5 Colors"],
        "Size": ["S", "M"],
        "Gender": ["Male", "Female"],
        "ScrapedAt": ["2025-10-18 09:00:00", "2025-10-18 10:00:00"]
    }
    df = pd.DataFrame(data)
    transformed = clean_and_transform(df)

    assert transformed.shape[0] > 0
    assert transformed["Rating"].dtype == float
    assert transformed["Price"].dtype == float
    assert transformed["Colors"].dtype == int
    assert transformed["Size"].dtype == object
    assert transformed["Gender"].dtype == object
    assert transformed["ScrapedAt"].str.contains("T").all()

def test_invalid_rating():
    data = {
        "Title": ["A"],
        "Price": ["$5.00"],
        "Rating": ["Invalid Rating"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "ScrapedAt": ["2025-10-18 09:00:00"]
    }
    df = pd.DataFrame(data)
    transformed = clean_and_transform(df)
    assert transformed.empty

def test_invalid_price():
    data = {
        "Title": ["Product A"],
        "Price": ["INVALID"],
        "Rating": ["⭐ 4.0"],
        "Colors": ["3 Colors"],
        "Size": ["M"],
        "Gender": ["Male"],
        "ScrapedAt": ["2025-05-10 10:00:00"]
    }
    df = pd.DataFrame(data)
    transformed = clean_and_transform(df)
    assert transformed.empty

if __name__ == "__main__":
    pytest.main(['-v', __file__])