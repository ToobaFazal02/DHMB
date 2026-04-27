from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # background mein chalega
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

search_terms = [
    'balochi embroidery',
    'pakistani handicraft', 
    'balochi dress',
    'handmade jewelry pakistan',
    'balochi carpet'
]

products = []

for term in search_terms:
    print(f"\n🔍 Searching: {term}")
    url = f"https://www.daraz.pk/catalog/?q={term.replace(' ', '+')}"
    
    try:
        driver.get(url)
        time.sleep(5)  # page load hone do
        
        # Product names
        names = driver.find_elements(By.CSS_SELECTOR, '[class*="title"]')
        prices = driver.find_elements(By.CSS_SELECTOR, '[class*="price"]')
        ratings = driver.find_elements(By.CSS_SELECTOR, '[class*="rating"]')
        
        print(f"   Found {len(names)} products")
        
        for i in range(min(len(names), 20)):
            try:
                name = names[i].text.strip()
                price = prices[i].text.strip() if i < len(prices) else 'N/A'
                rating = ratings[i].text.strip() if i < len(ratings) else 'N/A'
                
                if len(name) > 5:
                    products.append({
                        'product_name': name,
                        'price_pkr': price,
                        'rating': rating,
                        'category': term,
                        'source': 'daraz.pk'
                    })
            except:
                continue
                
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(3)

driver.quit()

df = pd.DataFrame(products)
df.drop_duplicates(subset=['product_name'], inplace=True)
df.to_csv(PROCESSED_DIR / 'daraz_scraped.csv', index=False)
print(f"\n✅ Scraped: {len(df)} products")
print(df.head())