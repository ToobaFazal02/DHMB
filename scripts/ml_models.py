import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

print("=" * 50)
print("DHMB - Big Data Analytics Engine")
print("=" * 50)

# ── 1. DATA LOAD ──────────────────────────────────
print("\n📂 Loading Silver layer data...")
df = pd.read_csv(PROCESSED_DIR / 'silver_results.csv')

# Tab/space fix karo column names mein
df.columns = df.columns.str.strip()

# String columns bhi strip karo
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

print(f"✅ Loaded: {len(df)} rows")
print(f"✅ Columns: {list(df.columns)}")

# ── 2. ENCODING ───────────────────────────────────
le_cat   = LabelEncoder()
le_dist  = LabelEncoder()
le_buyer = LabelEncoder()

df['cat_code']   = le_cat.fit_transform(df['category'])
df['dist_code']  = le_dist.fit_transform(df['district'])
df['buyer_code'] = le_buyer.fit_transform(df['top_buyer_region'])

# ── 3. DEMAND FORECASTING (XGBoost) ───────────────
print("\n" + "=" * 50)
print("📈 MODEL 1: Demand Forecasting (XGBoost)")
print("=" * 50)

X = df[['cat_code','dist_code','avg_price_pkr','total_purchases']]
y = df['total_events']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred   = model.predict(X_test)
mape     = mean_absolute_percentage_error(y_test, y_pred)
accuracy = (1 - mape) * 100

print(f"✅ Model trained!")
print(f"🎯 Forecast Accuracy: {accuracy:.2f}%")

df['predicted_demand'] = model.predict(X)
top5 = df.nlargest(5, 'predicted_demand')[
    ['category','district','predicted_demand','avg_price_pkr']
]
print("\n🔥 Top 5 High Demand:")
print(top5.to_string(index=False))

# ── 4. PRICE OPTIMIZATION ─────────────────────────
print("\n" + "=" * 50)
print("💰 MODEL 2: Price Optimization")
print("=" * 50)

price_stats = df.groupby('category').agg(
    mean_price    = ('avg_price_pkr',   'mean'),
    std_price     = ('avg_price_pkr',   'std'),
    total_sales   = ('total_purchases', 'sum')
).reset_index()

price_stats['optimal_min'] = (
    price_stats['mean_price'] - price_stats['std_price'] * 0.1
).round(2)
price_stats['optimal_max'] = (
    price_stats['mean_price'] + price_stats['std_price'] * 0.1
).round(2)

print("✅ Optimal Price Ranges:")
print(price_stats[['category','mean_price',
                   'optimal_min','optimal_max',
                   'total_sales']].to_string(index=False))

# ── 5. BUYER SEGMENTATION (K-Means) ───────────────
print("\n" + "=" * 50)
print("👥 MODEL 3: Buyer Segmentation (K-Means)")
print("=" * 50)

seg_X  = df[['avg_price_pkr','total_events',
             'total_purchases','buyer_code']]
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['segment'] = kmeans.fit_predict(seg_X)

seg_map = {0:'Budget_Buyers', 1:'Premium_Buyers', 2:'Bulk_Buyers'}
df['segment_name'] = df['segment'].map(seg_map)

seg_sum = df.groupby('segment_name').agg(
    avg_price       = ('avg_price_pkr',   'mean'),
    total_purchases = ('total_purchases', 'sum'),
    count           = ('segment',         'count')
).reset_index()

print("✅ Buyer Segments:")
print(seg_sum.to_string(index=False))

# ── 6. GOLD LAYER SAVE ────────────────────────────
print("\n" + "=" * 50)
print("💾 Saving Gold Layer CSVs...")
print("=" * 50)

df.to_csv(PROCESSED_DIR / 'gold_demand.csv', index=False)
price_stats.to_csv(PROCESSED_DIR / 'gold_price_optimization.csv', index=False)
seg_sum.to_csv(PROCESSED_DIR / 'gold_buyer_segments.csv', index=False)

print("✅ gold_demand.csv")
print("✅ gold_price_optimization.csv")
print("✅ gold_buyer_segments.csv")
print("\n🎉 ALL 3 ML MODELS COMPLETE!")
