import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_turbo_2025')
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

# --- TURBO CACHE SYSTEM ---
# We store the data in a global variable so it stays in RAM
GLOBAL_CACHE = {
    "products_json": "[]",
    "products_list": [],
    "last_sync": 0,
    "ttl": 900 # 15 minutes - very aggressive to keep it fast
}

def get_ref(col):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(col)

def refresh_cache_if_needed(force=False):
    """Fetches from Taiwan only if cache is old"""
    global GLOBAL_CACHE
    now = time.time()
    if not force and GLOBAL_CACHE["products_list"] and (now - GLOBAL_CACHE["last_sync"] < GLOBAL_CACHE["ttl"]):
        return
    
    try:
        if not db: return
        docs = get_ref('products').stream()
        products = [doc.to_dict() for doc in docs]
        GLOBAL_CACHE["products_list"] = products
        # Pre-stringifying JSON makes the page load much faster
        GLOBAL_CACHE["products_json"] = json.dumps(products)
        GLOBAL_CACHE["last_sync"] = now
        print("⚡ Cache Refreshed from Firebase")
    except Exception as e:
        print(f"Sync Error: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    refresh_cache_if_needed()
    products = GLOBAL_CACHE["products_list"]
    # We pass BOTH the list and the pre-built JSON string for the frontend
    categories = sorted(list(set(p.get('category', 'General') for p in products if p.get('category'))))
    return render_template('home.html', 
                           products=products, 
                           products_json=GLOBAL_CACHE["products_json"],
                           subcategories=categories)

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
    refresh_cache_if_needed(force=True)
    all_p = GLOBAL_CACHE["products_list"]
    grouped = {}
    for p in all_p:
        cat = p.get('category') or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    return render_template('admin_panel.html', grouped=grouped)

# --- FAST API ---

@app.route('/api/get-data')
def get_data():
    """Instant response from local RAM"""
    refresh_cache_if_needed()
    stock_map = {str(p.get('id')): p.get('stock', 999) for p in GLOBAL_CACHE["products_list"]}
    return jsonify({"stock": stock_map, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
        refresh_cache_if_needed(force=True) # Reset cache
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    if not db: return jsonify(success=False)
    data = request.json
    items = data.get('items', [])
    try:
        batch = db.batch()
        for item in items:
            p_id = str(item['id'])
            doc_ref = get_ref('products').document(p_id)
            # Optimization: only check DB if we really need to
            p_data = {
                'id': int(p_id),
                'name': item.get('name_kh') or item['name'],
                'price': item['price'],
                'image': item['image'],
                'category': item['categories'][0] if item.get('categories') else "General",
                'stock': 999 # Default for sync
            }
            batch.set(doc_ref, p_data, merge=True)
        batch.commit()
        refresh_cache_if_needed(force=True)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

