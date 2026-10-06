import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
books = []

# Fake browser header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

print("Starting scraping... Please wait.")

for page in range(1, 51):  # Scraping 50 pages
    url = BASE_URL.format(page)
    
    # Try up to 3 times per page
    success = False
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            success = True
            break
        except Exception as e:
            print(f"Page {page} failed (Attempt {attempt+1}/3). Retrying...")
            time.sleep(2)  # Wait 2 seconds before retrying
            
    if not success:
        print(f"Skipping page {page} due to errors.")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    for article in soup.select("article.product_pod"):
        title = article.h3.a["title"]
        price = article.select_one("p.price_color").get_text(strip=True)
        rating = article.select_one("p.star-rating")["class"][1]
        availability = article.select_one("p.instock.availability").get_text(strip=True)
        product_url = article.h3.a["href"]

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "product_url": product_url
        })

    print(f"✅ Scraped page {page}")
    time.sleep(1)  # Wait 1 second between pages

# Create DataFrame
df = pd.DataFrame(books)

# Clean the price column
df["price"] = df["price"].str.replace(r'[^\d.]', '', regex=True).astype(float)

# Save to CSV
df.to_csv("books.csv", index=False)

print("\n✅ Scraping complete!")
print(df.head())
print("Total books scraped:", df.shape[0])
