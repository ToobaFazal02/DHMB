import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

headers_list = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
]

search_terms = [
    'balochi embroidery',
    'balochi dress',
    'pakistani handicraft',
    'balochi jewelry',
    'handmade pakistan',
    'balochi carpet',
    'pakistani handcraft',
    'sindhi ajrak'
]

products = []

for term in search_terms:
    print(f"\n🔍 Searching: {term}")
    url = f"https://www.daraz.pk/catalog/?q={term.replace(' ', '+')}"
    
    try:
        headers = random.choice(headers_list)
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Product cards dhundho
        items = soup.find_all('div', {'class': lambda x: x and 'product' in x.lower()})
        
        print(f"   Found {len(items)} items")
        
        for item in items[:20]:  # har search se 20 products
            try:
                # Price
                price_el = item.find(class_=lambda x: x and 'price' in str(x).lower())
                price = price_el.get_text(strip=True) if price_el else 'N/A'
                
                # Name  
                name_el = item.find(['h2', 'h3', 'a', 'span'], 
                                   class_=lambda x: x and ('title' in str(x).lower() or 'name' in str(x).lower()))
                name = name_el.get_text(strip=True) if name_el else 'N/A'
                
                # Rating
                rating_el = item.find(class_=lambda x: x and 'rating' in str(x).lower())
                rating = rating_el.get_text(strip=True) if rating_el else 'N/A'
                
                if name != 'N/A' and len(name) > 3:
                    products.append({
                        'product_name': name,
                        'price': price,
                        'rating': rating,
                        'search_term': term,
                        'source': 'daraz.pk'
                    })
            except:
                continue
        
        # Polite delay — bot detection se bachne ke liye
        time.sleep(random.uniform(3, 6))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

# Save karo
df = pd.DataFrame(products)
df.drop_duplicates(subset=['product_name'], inplace=True)
df.to_csv(PROCESSED_DIR / 'daraz_scraped.csv', index=False)
print(f"\n✅ Total scraped: {len(df)} products")
print(df.head(10))