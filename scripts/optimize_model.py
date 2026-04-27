import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_percentage_error
from xgboost import XGBRegressor
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Data load
df = pd.read_csv(PROCESSED_DIR / 'silver_results.csv')
df.columns = df.columns.str.strip()
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

le_cat  = LabelEncoder()
le_dist = LabelEncoder()
df['cat_code']  = le_cat.fit_transform(df['category'])
df['dist_code'] = le_dist.fit_transform(df['district'])

X = df[['cat_code','dist_code','avg_price_pkr','total_purchases']]
y = df['total_events']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("⏳ Optimizing model — thoda wait karo...")

# Better parameters
best_model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
best_model.fit(X_train, y_train)

y_pred   = best_model.predict(X_test)
mape     = mean_absolute_percentage_error(y_test, y_pred)
accuracy = (1 - mape) * 100

print(f"✅ Optimized Accuracy: {accuracy:.2f}%")
print(f"   Pehle tha:  82.93%")
print(f"   Ab hai:     {accuracy:.2f}%")
print(f"   Improvement: +{accuracy-82.93:.2f}%")