import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import time

# directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from utils.extract import (
    extract_bersih,
    extract_product,
    ambil_content_url,
    scrape_fashion,
    HEADERS,
)

class TestExtractUtilities(unittest.TestCase):

    @patch('utils.extract.requests.get')
    def test_ambil_content_url_berhasil(self, mocked_get):
        dummy_response = MagicMock()
        dummy_response.status_code = 200
        dummy_response.content = b"<html><body>Mock Page</body></html>"
        mocked_get.return_value = dummy_response

        result = ambil_content_url("http://mock-url.com")
        self.assertEqual(result, b"<html><body>Mock Page</body></html>")
        mocked_get.assert_called_once_with("http://mock-url.com", headers=HEADERS,  timeout=5)

    @patch('utils.extract.requests.get')
    def test_ambil_content_url_gagal(self, mocked_get):
        mock_failed = MagicMock()
        mock_failed.raise_for_status.side_effect = requests.exceptions.RequestException("Error")
        mocked_get.return_value = mock_failed

        result = ambil_content_url("http://error-url.com")
        self.assertIsNone(result)
        mocked_get.assert_called_once()

    def test_extract_bersih_pola(self):
        mock_tags = [MagicMock(string="Rating: ⭐ 4.2"), MagicMock(string="Colors: 5 Colors")]
        result = extract_bersih(mock_tags, "Rating", r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)")
        self.assertEqual(result, "⭐ 4.2")

    def test_extract_bersih_tanpa_keyword(self):
        mock_tags = [MagicMock(string="Colors: 5 Colors")]
        result = extract_bersih(mock_tags, "Rating", r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)")
        self.assertEqual(result, "N/A")

    def test_extract_bersih_tanpa_pola(self):
        mock_tags = [MagicMock(string="Rating something weird")]
        result = extract_bersih(mock_tags, "Rating", r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)")
        self.assertEqual(result, "N/A")

    def test_extract_bersih_fallback(self):
        mock_tags = [MagicMock(string="Some irrelevant info")]
        result = extract_bersih(mock_tags, "NonExist", r"NonExist:\s*(.*)", fallback="Missing")
        self.assertEqual(result, "Missing")

    def test_extract_product_lengkap(self):
        html = """
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title">Cool Item</h3></div>
                <div class="price-container">$49.99</div>
                <p>Rating: ⭐ 4.7</p>
                <p>Colors: 4 Colors</p>
                <p>Size: M</p>
                <p>Gender: Unisex</p>
            </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div', class_='collection-card')
        data = extract_product(card)
        self.assertEqual(data['Title'], "Cool Item")
        self.assertEqual(data['Price'], "$49.99")
        self.assertEqual(data['Rating'], "⭐ 4.7")
        self.assertEqual(data['Colors'], "4")
        self.assertEqual(data['Size'], "M")
        self.assertEqual(data['Gender'], "Unisex")
        self.assertIsInstance(data['ScrapedAt'], datetime)

    def test_extract_product_miss(self):
        html = """
            <div class="collection-card">
                <div class="product-details"><h3 class="product-title"></h3></div>
            </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div', class_='collection-card')
        data = extract_product(card)
        self.assertEqual(data['Title'], "Unknown Title")
        self.assertEqual(data['Price'], "Price Not Available")
        self.assertEqual(data['Rating'], "Invalid Rating")
        self.assertEqual(data['Colors'], "No Colors")
        self.assertEqual(data['Size'], "Unknown")
        self.assertEqual(data['Gender'], "Unknown")
        self.assertIsInstance(data['ScrapedAt'], datetime)

    @patch('utils.extract.ambil_content_url')
    @patch('utils.extract.extract_product')
    @patch('utils.extract.time.sleep')
    def test_scrape_fashion_berhasil(self, mock_sleep, mock_extract_product, mock_ambil_content_url):
        mock_ambil_content_url.return_value = b"<html><div class='collection-card'></div></html>"
        
        dummy_card = BeautifulSoup("<div class='collection-card'></div>", 'html.parser').find('div')
        with patch('bs4.BeautifulSoup.find_all', return_value=[dummy_card]):
            mock_extract_product.return_value = {
                'Title': 'Mock Item',
                'Price': '$20',
                'Rating': '⭐ 4.5',
                'Colors': '3',
                'Size': 'L',
                'Gender': 'Unisex',
                'ScrapedAt': datetime.now()
            }
            result = scrape_fashion(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['Title'], 'Mock Item')
            mock_ambil_content_url.assert_called_once()
            mock_extract_product.assert_called_once()
            mock_sleep.assert_called_once_with(0.5)
            
if __name__ == '__main__':
    unittest.main()