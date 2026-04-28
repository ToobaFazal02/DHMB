import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RUNTIME_DATA_DIR = DATA_DIR / "runtime"

USERS_FILE = RUNTIME_DATA_DIR / "users.json"
LISTINGS_FILE = RUNTIME_DATA_DIR / "listings.json"
MESSAGES_FILE = RUNTIME_DATA_DIR / "messages.json"
ORDERS_FILE = RUNTIME_DATA_DIR / "orders.json"

ARTISAN_SEED = [
    {
        "id": "usr-artisan-zainab",
        "full_name": "Zainab Bibi",
        "email": "zainab@dhmb.local",
        "password_hash": "",
        "role": "artisan",
        "district": "Quetta",
        "created_at": "",
    },
    {
        "id": "usr-artisan-samia",
        "full_name": "Samia Baloch",
        "email": "samia@dhmb.local",
        "password_hash": "",
        "role": "artisan",
        "district": "Turbat",
        "created_at": "",
    },
    {
        "id": "usr-admin-fatima",
        "full_name": "Fatima Rind",
        "email": "admin@dhmb.local",
        "password_hash": "",
        "role": "admin",
        "district": "Quetta",
        "created_at": "",
    },
    {
        "id": "usr-buyer-ahmed",
        "full_name": "Ahmed Khan",
        "email": "buyer@dhmb.local",
        "password_hash": "",
        "role": "buyer",
        "district": "Gwadar",
        "created_at": "",
    },
]

LISTING_SEED = [
    {
        "id": "lst-balochi-embroidery-quetta",
        "owner_id": "usr-artisan-zainab",
        "product_name": "Balochi Embroidery Quetta Panel",
        "category": "Balochi_Embroidery",
        "district": "Quetta",
        "price": 4425,
        "description": "Published from the live pricing range for Balochi embroidery and aligned with Quetta demand records.",
        "status": "published",
        "created_at": "",
        "updated_at": "",
    },
    {
        "id": "lst-marble-craft-quetta",
        "owner_id": "usr-artisan-zainab",
        "product_name": "Marble Craft Quetta Finish",
        "category": "Marble_Craft",
        "district": "Quetta",
        "price": 7782,
        "description": "Marketplace listing anchored to the current marble craft optimization range.",
        "status": "published",
        "created_at": "",
        "updated_at": "",
    },
    {
        "id": "lst-handwoven-carpet-turbat",
        "owner_id": "usr-artisan-samia",
        "product_name": "Hand Woven Carpet Turbat Weave",
        "category": "Hand_Woven_Carpet",
        "district": "Turbat",
        "price": 14050,
        "description": "Published catalog item derived from the gold layer carpet pricing record.",
        "status": "published",
        "created_at": "",
        "updated_at": "",
    },
]


app = Flask(__name__)
app.secret_key = os.environ.get("DHMB_SECRET_KEY", "dhmb-local-dev-secret")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
CORS(app, supports_credentials=True)


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DATA_DIR / name)
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df


def load_data():
    silver = load_csv("silver_results.csv")
    gold_demand = load_csv("gold_demand.csv")
    gold_price = load_csv("gold_price_optimization.csv")
    gold_segments = load_csv("gold_buyer_segments.csv")
    return silver, gold_demand, gold_price, gold_segments


def read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def ensure_storage() -> None:
    timestamp = now_iso()
    RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not USERS_FILE.exists():
        users = []
        for item in ARTISAN_SEED:
            user = dict(item)
            password = (
                "artisan123"
                if user["role"] == "artisan"
                else "admin123"
                if user["role"] == "admin"
                else "buyer123"
            )
            user["password_hash"] = generate_password_hash(password)
            user["created_at"] = timestamp
            users.append(user)
        write_json(USERS_FILE, users)

    if not LISTINGS_FILE.exists():
        listings = []
        for item in LISTING_SEED:
            listing = dict(item)
            listing["created_at"] = timestamp
            listing["updated_at"] = timestamp
            listings.append(listing)
        write_json(LISTINGS_FILE, listings)

    if not MESSAGES_FILE.exists():
        write_json(MESSAGES_FILE, [])

    if not ORDERS_FILE.exists():
        write_json(ORDERS_FILE, [])


ensure_storage()


def get_users():
    return read_json(USERS_FILE, [])


def save_users(users) -> None:
    write_json(USERS_FILE, users)


def get_listings():
    return read_json(LISTINGS_FILE, [])


def save_listings(listings) -> None:
    write_json(LISTINGS_FILE, listings)


def get_messages():
    return read_json(MESSAGES_FILE, [])


def save_messages(messages) -> None:
    write_json(MESSAGES_FILE, messages)


def get_orders():
    return read_json(ORDERS_FILE, [])


def save_orders(orders) -> None:
    write_json(ORDERS_FILE, orders)


def public_user(user):
    return {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
        "district": user.get("district", ""),
        "created_at": user.get("created_at"),
    }


def find_user(user_id: str):
    return next((user for user in get_users() if user["id"] == user_id), None)


def find_user_by_email(email: str):
    email = email.strip().lower()
    return next((user for user in get_users() if user["email"].lower() == email), None)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return find_user(user_id)


def require_auth():
    user = current_user()
    if not user:
        return None, (jsonify({"error": "Authentication required."}), 401)
    return user, None


def require_roles(*roles):
    user, error = require_auth()
    if error:
        return None, error
    if user["role"] not in roles and user["role"] != "admin":
        return None, (jsonify({"error": "You do not have permission for this action."}), 403)
    return user, None


def listing_with_owner(listing, user_lookup=None):
    if user_lookup is None:
        user_lookup = {user["id"]: user for user in get_users()}
    owner = user_lookup.get(listing["owner_id"])
    orders = [order for order in get_orders() if order["listing_id"] == listing["id"]]
    return {
        **listing,
        "owner_name": owner["full_name"] if owner else "Unknown user",
        "owner_role": owner["role"] if owner else "artisan",
        "order_count": len(orders),
        "latest_order_status": orders[-1]["status"] if orders else "none",
    }


def buyer_summary_for_user(user):
    listings = get_listings()
    orders = get_orders()
    if user["role"] == "artisan":
        owned_ids = {listing["id"] for listing in listings if listing["owner_id"] == user["id"]}
        relevant_orders = [order for order in orders if order["listing_id"] in owned_ids]
        monthly_earnings = sum(order["total"] for order in relevant_orders if order["status"] in {"confirmed", "in_transit", "delivered"})
        return {
            "monthly_earnings": monthly_earnings,
            "listing_count": len(owned_ids),
            "order_count": len(relevant_orders),
        }

    if user["role"] == "buyer":
        my_orders = [order for order in orders if order["buyer_id"] == user["id"]]
        return {
            "monthly_earnings": 0,
            "listing_count": 0,
            "order_count": len(my_orders),
        }

    return {
        "monthly_earnings": 0,
        "listing_count": len(listings),
        "order_count": len(orders),
    }


def next_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


def compute_tracking(status: str):
    states = [
        {"code": "confirmed", "label": "Order confirmed", "note": "Payment recorded and seller notified."},
        {"code": "in_transit", "label": "In transit", "note": "Shipment is moving through the dispatch network."},
        {"code": "delivered", "label": "Delivered", "note": "Order has been handed over to the buyer."},
    ]
    status_order = {"confirmed": 0, "in_transit": 1, "delivered": 2}
    current_index = status_order.get(status, 0)
    timeline = []
    for index, item in enumerate(states):
        state = "pending"
        if index < current_index:
            state = "complete"
        elif index == current_index:
            state = "active"
        timeline.append({**item, "state": state})
    return timeline


def build_auto_reply(listing, message_text):
    _, _, gold_price, _ = load_data()
    match = gold_price[gold_price["category"] == listing["category"]]
    if match.empty:
        return f"We received your message about {listing['product_name']}. The seller will review the request soon."

    row = match.iloc[0]
    return (
        f"Message received for {listing['product_name']}. "
        f"The current optimized range for {listing['category'].replace('_', ' ')} is "
        f"PKR {round(float(row['optimal_min'])):,} to PKR {round(float(row['optimal_max'])):,}. "
        f"The listing is registered in {listing['district']} and the request has been logged."
    )


def catalog_rows():
    return [listing_with_owner(item) for item in get_listings() if item["status"] == "published"]


@app.route("/")
@app.route("/admin")
@app.route("/artisan")
@app.route("/buyer")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(FRONTEND_DIR, "manifest.webmanifest")


@app.route("/offline.html")
def offline():
    return send_from_directory(FRONTEND_DIR, "offline.html")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(FRONTEND_DIR, "service-worker.js")


@app.route("/icon.svg")
def icon():
    return send_from_directory(FRONTEND_DIR, "icon.svg")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    """Rule-based buyer assistant for the Lovable shop UI (no external LLM)."""
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).lower()
    product = str(data.get("product") or "this product").strip() or "this product"
    artisan = str(data.get("artisan") or "the artisan").strip() or "the artisan"

    if any(w in message for w in ["price", "cost", "kitna", "rate"]):
        reply = (
            f"The price for {product} is clearly listed on the product page. "
            "We also offer bulk discounts — contact us for orders above 5 units!"
        )

    elif any(w in message for w in ["ship", "deliver", "uae", "uk", "usa", "dubai", "international"]):
        reply = (
            "Yes! We ship internationally via TCS Express. UAE: 5-7 days (PKR 1,200). "
            "UK: 10-14 days (PKR 2,500). USA: 12-15 days (PKR 3,000)."
        )

    elif any(w in message for w in ["handmade", "authentic", "original", "genuine", "real"]):
        reply = (
            f"Absolutely! {product} is 100% handmade by {artisan} using traditional Balochi techniques "
            "passed down through generations. Each piece is unique and verified by our quality team."
        )

    elif any(w in message for w in ["how long", "time", "days", "when", "delivery time"]):
        reply = (
            "Domestic delivery (Pakistan): 3-5 days via TCS. International: 7-15 days depending on "
            "location. You'll receive a tracking number via WhatsApp!"
        )

    elif any(w in message for w in ["discount", "offer", "sale", "cheap", "negotiate"]):
        reply = (
            "We offer 10% discount on orders above PKR 10,000 and 15% on bulk orders (5+ items). "
            "Use code BALOCHI10 at checkout!"
        )

    elif any(w in message for w in ["return", "refund", "exchange"]):
        reply = (
            "We have a 7-day return policy for damaged items. Photos required. Refund processed within "
            "3-5 business days to your original payment method."
        )

    elif any(w in message for w in ["payment", "pay", "jazzcash", "easypaisa", "card", "stripe"]):
        reply = (
            "We accept: Stripe (Credit/Debit card), JazzCash, EasyPaisa, and PayPal. "
            "All payments are PCI-DSS secure and encrypted."
        )

    elif any(w in message for w in ["custom", "customize", "order", "special", "design"]):
        reply = (
            f"Yes! {artisan} accepts custom orders. Share your design requirements and we'll provide "
            "a quote within 24 hours. Custom orders take 7-14 days."
        )

    elif any(w in message for w in ["hello", "hi", "salam", "assalam", "hey"]):
        reply = (
            f"السلام علیکم! Welcome to DHMB. I'm here to help you with {product}. "
            "Ask me about pricing, shipping, or authenticity!"
        )

    else:
        reply = (
            f"Thank you for your interest in {product}! For specific questions, I'll connect you with "
            f"{artisan} directly. They typically respond within 2 hours. Is there anything specific "
            "I can help you with?"
        )

    return jsonify({"reply": reply, "artisan": artisan, "timestamp": now_iso()})


@app.route("/api/signup", methods=["POST"])
def signup():
    payload = request.get_json(silent=True) or {}
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()
    role = str(payload.get("role", "buyer")).strip().lower()
    district = str(payload.get("district", "")).strip()

    if not full_name or not email or not password:
        return jsonify({"error": "Full name, email, and password are required."}), 400

    if role not in {"admin", "artisan", "buyer"}:
        return jsonify({"error": "Invalid role selected."}), 400

    if find_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    user = {
        "id": next_id("usr"),
        "full_name": full_name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": role,
        "district": district,
        "created_at": now_iso(),
    }
    users = get_users()
    users.append(user)
    save_users(users)
    session["user_id"] = user["id"]
    return jsonify({"user": public_user(user), "summary": buyer_summary_for_user(user)}), 201


@app.route("/api/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()
    user = find_user_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"] = user["id"]
    return jsonify({"user": public_user(user), "summary": buyer_summary_for_user(user)})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def me():
    user, error = require_auth()
    if error:
        return error
    return jsonify({"user": public_user(user), "summary": buyer_summary_for_user(user)})


@app.route("/api/pipeline", methods=["GET"])
def pipeline():
    return jsonify(
        {
            "live": True,
            "bronze": {
                "label": "Bronze Layer",
                "size_mb": 8.6,
                "rows": 100000,
                "description": "Raw browsing, search, and order capture events.",
            },
            "silver": {
                "label": "Silver Layer",
                "size_kb": 3.6,
                "rows": 81,
                "description": "MapReduce summaries ready for marketplace analytics.",
            },
            "gold": {
                "label": "Gold Layer",
                "size_mb": 5.9,
                "datasets": 3,
                "description": "Demand, pricing, and buyer segmentation datasets.",
            },
            "ml_models": {
                "label": "ML Models",
                "accuracy": 82.93,
                "description": "XGBoost, pricing optimization, and K Means outputs.",
            },
            "mapreduce": {"status": "completed", "job": "job_local921179833_0001"},
        }
    )


@app.route("/api/kpis", methods=["GET"])
def kpis():
    silver, _, _, _ = load_data()
    artisan_count = sum(1 for user in get_users() if user["role"] == "artisan")
    total_purchases = int(silver["total_purchases"].sum())
    total_events = int(silver["total_events"].sum())
    avg_price = round(float(silver["avg_price_pkr"].mean()), 2)

    return jsonify(
        {
            "total_events": total_events,
            "total_purchases": total_purchases,
            "avg_price_pkr": avg_price,
            "artisans": artisan_count,
            "accuracy": 82.93,
            "income_increase": 180,
            "districts": int(silver["district"].nunique()),
            "categories": int(silver["category"].nunique()),
        }
    )


@app.route("/api/demand", methods=["GET"])
def demand():
    silver, _, _, _ = load_data()
    data = (
        silver.groupby("category")
        .agg(
            total_events=("total_events", "sum"),
            total_purchases=("total_purchases", "sum"),
            avg_price=("avg_price_pkr", "mean"),
        )
        .reset_index()
        .sort_values("total_events", ascending=False)
    )
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/districts", methods=["GET"])
def districts():
    silver, _, _, _ = load_data()
    data = (
        silver.groupby("district")
        .agg(
            total_events=("total_events", "sum"),
            total_purchases=("total_purchases", "sum"),
            avg_price=("avg_price_pkr", "mean"),
        )
        .reset_index()
        .sort_values("total_purchases", ascending=False)
    )
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/price-optimization", methods=["GET"])
def price_optimization():
    _, _, gold_price, _ = load_data()
    data = gold_price.sort_values("mean_price", ascending=False)
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/segments", methods=["GET"])
def segments():
    _, _, _, gold_segments = load_data()
    data = gold_segments.sort_values("count", ascending=False)
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/buyers", methods=["GET"])
def buyers():
    silver, _, _, _ = load_data()
    data = (
        silver.groupby("top_buyer_region")
        .agg(total_purchases=("total_purchases", "sum"))
        .reset_index()
        .sort_values("total_purchases", ascending=False)
    )
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/top-products", methods=["GET"])
def top_products():
    silver, _, _, _ = load_data()
    data = silver.nlargest(
        18,
        "total_events",
    )[
        [
            "category",
            "district",
            "total_events",
            "avg_price_pkr",
            "total_purchases",
            "top_buyer_region",
        ]
    ]
    return jsonify(data.to_dict(orient="records"))


@app.route("/api/catalog", methods=["GET"])
def catalog():
    return jsonify(catalog_rows())


@app.route("/api/listings", methods=["GET"])
def listings_get():
    owner = request.args.get("owner")
    listings = get_listings()
    if owner == "me":
        user, error = require_auth()
        if error:
            return error
        visible = [item for item in listings if item["owner_id"] == user["id"]]
        return jsonify([listing_with_owner(item) for item in visible])
    return jsonify([listing_with_owner(item) for item in listings if item["status"] == "published"])


@app.route("/api/listings", methods=["POST"])
def listings_create():
    user, error = require_roles("artisan")
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    product_name = str(payload.get("product_name", "")).strip()
    category = str(payload.get("category", "")).strip()
    district = str(payload.get("district", "")).strip()
    description = str(payload.get("description", "")).strip()
    status = str(payload.get("status", "published")).strip().lower()

    try:
        price = int(float(payload.get("price", 0)))
    except (TypeError, ValueError):
        price = 0

    if not product_name or not category or not district or price <= 0:
        return jsonify({"error": "Product name, category, district, and price are required."}), 400

    listing = {
        "id": next_id("lst"),
        "owner_id": user["id"],
        "product_name": product_name,
        "category": category,
        "district": district,
        "price": price,
        "description": description,
        "status": status if status in {"draft", "published"} else "published",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    listings = get_listings()
    listings.append(listing)
    save_listings(listings)
    return jsonify(listing_with_owner(listing)), 201


@app.route("/api/listings/<listing_id>", methods=["PUT"])
def listings_update(listing_id):
    user, error = require_roles("artisan")
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    listings = get_listings()
    listing = next((item for item in listings if item["id"] == listing_id), None)
    if not listing:
        return jsonify({"error": "Listing not found."}), 404

    if listing["owner_id"] != user["id"] and user["role"] != "admin":
        return jsonify({"error": "You can only edit your own listings."}), 403

    for field in ["product_name", "category", "district", "description", "status"]:
        if field in payload:
            listing[field] = str(payload[field]).strip()

    if "price" in payload:
        try:
            listing["price"] = int(float(payload["price"]))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid price."}), 400

    listing["updated_at"] = now_iso()
    save_listings(listings)
    return jsonify(listing_with_owner(listing))


@app.route("/api/listings/<listing_id>", methods=["DELETE"])
def listings_delete(listing_id):
    user, error = require_roles("artisan")
    if error:
        return error

    listings = get_listings()
    listing = next((item for item in listings if item["id"] == listing_id), None)
    if not listing:
        return jsonify({"error": "Listing not found."}), 404

    if listing["owner_id"] != user["id"] and user["role"] != "admin":
        return jsonify({"error": "You can only delete your own listings."}), 403

    updated = [item for item in listings if item["id"] != listing_id]
    save_listings(updated)
    return jsonify({"ok": True})


@app.route("/api/messages", methods=["GET"])
def messages_get():
    user, error = require_auth()
    if error:
        return error

    listing_id = request.args.get("listing_id", "").strip()
    if not listing_id:
        return jsonify([])

    messages = [message for message in get_messages() if message["listing_id"] == listing_id]
    visible = []
    for message in messages:
        if message["sender_type"] == "system" or message["sender_id"] == user["id"] or user["role"] == "admin":
            visible.append(message)
        else:
            listing = next((item for item in get_listings() if item["id"] == listing_id), None)
            if listing and listing["owner_id"] == user["id"]:
                visible.append(message)
    return jsonify(visible)


@app.route("/api/messages", methods=["POST"])
def messages_post():
    user, error = require_auth()
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    listing_id = str(payload.get("listing_id", "")).strip()
    text = str(payload.get("text", "")).strip()
    if not listing_id or not text:
        return jsonify({"error": "Listing id and message text are required."}), 400

    listing = next((item for item in get_listings() if item["id"] == listing_id), None)
    if not listing:
        return jsonify({"error": "Listing not found."}), 404

    messages = get_messages()
    user_message = {
        "id": next_id("msg"),
        "listing_id": listing_id,
        "sender_id": user["id"],
        "sender_name": user["full_name"],
        "sender_role": user["role"],
        "sender_type": "user",
        "text": text,
        "created_at": now_iso(),
    }
    reply_message = {
        "id": next_id("msg"),
        "listing_id": listing_id,
        "sender_id": listing["owner_id"],
        "sender_name": "Marketplace Desk",
        "sender_role": "assistant",
        "sender_type": "system",
        "text": build_auto_reply(listing, text),
        "created_at": now_iso(),
    }
    messages.extend([user_message, reply_message])
    save_messages(messages)
    return jsonify([user_message, reply_message]), 201


@app.route("/api/orders", methods=["GET"])
def orders_get():
    user, error = require_auth()
    if error:
        return error

    listings = {item["id"]: item for item in get_listings()}
    all_orders = get_orders()

    if user["role"] == "buyer":
        relevant = [order for order in all_orders if order["buyer_id"] == user["id"]]
    elif user["role"] == "artisan":
        owned_ids = {item["id"] for item in listings.values() if item["owner_id"] == user["id"]}
        relevant = [order for order in all_orders if order["listing_id"] in owned_ids]
    else:
        relevant = all_orders

    enriched = []
    for order in relevant:
        listing = listings.get(order["listing_id"])
        buyer = find_user(order["buyer_id"])
        enriched.append(
            {
                **order,
                "listing_name": listing["product_name"] if listing else "Unknown listing",
                "category": listing["category"] if listing else "",
                "district": listing["district"] if listing else "",
                "buyer_name": buyer["full_name"] if buyer else "Unknown buyer",
                "tracking_timeline": compute_tracking(order["status"]),
            }
        )
    return jsonify(enriched)


@app.route("/api/orders", methods=["POST"])
def orders_post():
    user, error = require_roles("buyer")
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    listing_id = str(payload.get("listing_id", "")).strip()
    payment_method = str(payload.get("payment_method", "Stripe")).strip()
    listing = next((item for item in get_listings() if item["id"] == listing_id and item["status"] == "published"), None)

    if not listing:
        return jsonify({"error": "Published listing not found."}), 404

    shipping_fee = 450
    service_fee = 120
    total = int(listing["price"]) + shipping_fee + service_fee
    order = {
        "id": next_id("ord"),
        "listing_id": listing_id,
        "buyer_id": user["id"],
        "payment_method": payment_method,
        "subtotal": int(listing["price"]),
        "shipping_fee": shipping_fee,
        "service_fee": service_fee,
        "total": total,
        "status": "confirmed",
        "tracking_id": "TCS-" + uuid4().hex[:8].upper(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    orders = get_orders()
    orders.append(order)
    save_orders(orders)
    return jsonify(
        {
            **order,
            "listing_name": listing["product_name"],
            "category": listing["category"],
            "district": listing["district"],
            "tracking_timeline": compute_tracking(order["status"]),
        }
    ), 201


if __name__ == "__main__":
    print("DHMB API server starting...")
    print("Dashboard: http://localhost:5000")
    print("Health: http://localhost:5000/api/health")
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=5000)
