import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_studio_pro_2025_fast')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')

# --- FIREBASE SETUP ---
service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
db = None
PROJECT_ID = "somphea-reak-website"

if service_account_info:
    try:
        cred_dict = json.loads(service_account_info.strip())
        PROJECT_ID = cred_dict.get("project_id", PROJECT_ID)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print(f"Firebase Error: {e}")

# --- HIGH PERFORMANCE CACHE ---
# This saves trips to Taiwan by remembering data in the server's memory
cache = {
    "products": None,
    "last_update": 0,
    "ttl": 300 # Remember data for 5 minutes (300 seconds)
}

def get_ref(col):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(col)

def get_cached_products():
    """Fetch products from memory if fresh, otherwise go to Taiwan"""
    now = time.time()
    if cache["products"] and (now - cache["last_update"] < cache["ttl"]):
        return cache["products"]
    
    # Cache expired or empty, fetch from Firebase
    try:
        docs = get_ref('products').stream()
        products = [doc.to_dict() for doc in docs]
        cache["products"] = products
        cache["last_update"] = now
        return products
    except:
        return cache["products"] or []

# --- ROUTES ---

@app.route('/')
def home():
    products = get_cached_products()
    categories = sorted(list(set(p.get('category', 'General') for p in products if p.get('category'))))
    return render_template('home.html', products=products, subcategories=categories)

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/lego')
def lego_page():
    return render_template('LEGO.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    # Admin always gets fresh data (no cache)
    docs = get_ref('products').stream()
    all_p = [doc.to_dict() for doc in docs]
    all_p.sort(key=lambda x: x.get('name', ''))
    grouped = {cat: [p for p in all_p if p.get('category') == cat] for cat in set(p.get('category', 'General') for p in all_p)}
    return render_template('admin_panel.html', grouped=grouped)

# --- API (Clears cache when data changes) ---

@app.route('/api/get-data')
def get_data():
    products = get_cached_products()
    stock_map = {str(p['id']): p.get('stock', 999) for p in products}
    return jsonify({"stock": stock_map, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
    cache["products"] = None # Force refresh on next load
    return jsonify(success=True)

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    if not db: return jsonify(success=False)
    data = request.json
    items = data.get('items', [])
    batch = db.batch()
    for item in items:
        doc_ref = get_ref('products').document(str(item['id']))
        snap = doc_ref.get()
        item['stock'] = snap.to_dict().get('stock', 999) if snap.exists else 999
        batch.set(doc_ref, item)
    batch.commit()
    cache["products"] = None # Clear cache
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

