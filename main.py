from utils.extract import scrape_fashion
from utils.transform import clean_and_transform
from utils.load import load_data

def main():
    print("Starting product scraping from 50 pages...")
    all_products = scrape_fashion(pages=50, delay=0.5)

    if not all_products:
        print("No product data successfully retrieved. Program stopped.")
        return

    print(f"Number of products retrieved: {len(all_products)}")

    # transformation
    cleaned_data = clean_and_transform(all_products)

    # save data
    load_data(cleaned_data)

    print("Data scraping and storage process completed.")

if __name__ == "__main__":
    main()
