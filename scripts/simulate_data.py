import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

np.random.seed(42)
n = 100000

districts = {
    'Quetta': 0.25, 'Turbat': 0.15, 'Khuzdar': 0.12,
    'Gwadar': 0.10, 'Zhob': 0.08, 'Chaman': 0.08,
    'Sibbi': 0.07, 'Kalat': 0.07, 'Nushki': 0.05, 'Panjgur': 0.03
}

categories = {
    'Balochi_Embroidery': (800, 8000),
    'Hand_Woven_Carpet': (3000, 25000),
    'Gemstones': (1000, 50000),
    'Marble_Craft': (500, 15000),
    'Mirror_Work': (400, 5000),
    'Pottery': (200, 3000),
    'Leather_Khussa': (600, 4000),
    'Woodcraft': (1000, 12000)
}

buyers = ['Local_Pakistan','UAE','UK','USA','Saudi_Arabia','Iran','Oman']
events = ['view','view','view','view','cart','cart','purchase']

district_list = list(districts.keys())
district_weights = list(districts.values())
cat_list = list(categories.keys())

print("⏳ Generating 100,000 rows...")
rows = []

for i in range(n):
    cat = random.choice(cat_list)
    price_min, price_max = categories[cat]
    event = random.choice(events)
    month = random.randint(1, 12)
    
    rows.append({
        'transaction_id': f'TXN{i+1:07d}',
        'event_type': event,
        'artisan_id': f'ART{np.random.randint(1,1501):04d}',
        'district': np.random.choice(district_list, p=district_weights),
        'product_category': cat,
        'price_pkr': np.random.randint(price_min, price_max),
        'buyer_region': random.choice(buyers),
        'units_sold': np.random.randint(1, 8),
        'rating': round(random.uniform(3.0, 5.0), 1),
        'search_volume': np.random.randint(5, 300),
        'month': month,
        'timestamp': datetime(2023, month, random.randint(1,28),
                             random.randint(0,23), random.randint(0,59))
    })

df = pd.DataFrame(rows)
df.to_csv(PROCESSED_DIR / 'dhmb_simulated.csv', index=False)
print(f"✅ Done! {len(df):,} rows generated")
print(f"📁 File: {PROCESSED_DIR / 'dhmb_simulated.csv'}")
print(f"\nSample data:")
print(df.head())
print(f"\nCategories count:")
print(df['product_category'].value_counts())