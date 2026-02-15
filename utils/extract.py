import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
    )
}
def extract_bersih(paragraphs, keyword, pattern, fallback="N/A"):
    for p in paragraphs:
        if p.string and keyword in p.string:
            found = re.search(pattern, p.string)
            if found:
                return found.group(1).strip()
    return fallback

def extract_product(card):
    try:
        title_tag = card.select_one('.product-details h3.product-title') or card.find('h3', class_='product-title')
        title = title_tag.get_text(strip=True) if title_tag and title_tag.get_text(strip=True) else "Unknown Title"

        price_tag = card.find('div', class_='price-container')
        price = price_tag.get_text(strip=True) if price_tag else "Price Not Available"

        paragraphs = card.find_all('p')

        rating = extract_bersih(paragraphs, "Rating", r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)", "Invalid Rating")
        colors = extract_bersih(paragraphs, "Colors", r"(\d+)\s*Colors", "No Colors")
        size = extract_bersih(paragraphs, "Size", r"Size:\s*(\w+)", "Unknown")
        gender = extract_bersih(paragraphs, "Gender", r"Gender:\s*(\w+)", "Unknown")

        timestamp = datetime.now()

        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "ScrapedAt": timestamp
        }
    except Exception as e:
        print(f"Error during product extraction: {e}")
        return None
    

def ambil_content_url(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        print(f"Error fetching content from {url}")
        return None

def scrape_fashion(pages, delay=0.5):
    all_products = []
    for page_num in range(1, pages + 1):
        url = 'https://fashion-studio.dicoding.dev/' if page_num == 1 else f'https://fashion-studio.dicoding.dev/page{page_num}'
        print(f"Processing page: {url}")

        html_content = ambil_content_url(url)
        if not html_content:
            print(f"Failed to retrieve data from page {page_num}, stopping scraping.")
            break

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            cards = soup.find_all('div', class_='collection-card')

            if not cards:
                print(f"No products found on page {page_num}.")
                continue

            for card in cards:
                product = extract_product(card)
                if product:
                    all_products.append(product)

        except Exception as e:
            print(f"Error parsing page {page_num}: {e}")
            continue

        time.sleep(delay) 
    return all_products

if __name__ == "__main__":
    result = scrape_fashion(pages=2)
    for item in result:
        print(item)