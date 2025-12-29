import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

# --- INITIALIZATION ---
app = Flask(__name__)

# --- SECURE CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_fast_secure_2025')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

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
        print(f"✅ Connected to Cloud Database: {PROJECT_ID}")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")

# --- SPEED OPTIMIZATION: CACHE SYSTEM ---
# This saves the product list in the server's RAM so it doesn't have to fetch from Taiwan every time.
PRODUCT_CACHE = {
    "data": None,
    "last_fetch": 0,
    "ttl": 300 # Refresh data every 300 seconds (5 minutes)
}

def get_ref(collection_name):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(collection_name)

def fetch_products(force_refresh=False):
    """Smart fetch: Uses memory cache if available and fresh"""
    global PRODUCT_CACHE
    now = time.time()
    
    # If we have data in memory and it's less than 5 minutes old, return it instantly
    if not force_refresh and PRODUCT_CACHE["data"] and (now - PRODUCT_CACHE["last_fetch"] < PRODUCT_CACHE["ttl"]):
        return PRODUCT_CACHE["data"]
    
    # Otherwise, go to Taiwan to get the latest data
    try:
        if not db: return []
        docs = get_ref('products').stream()
        products = [doc.to_dict() for doc in docs]
        
        # Save to cache
        PRODUCT_CACHE["data"] = products
        PRODUCT_CACHE["last_fetch"] = now
        return products
    except Exception as e:
        print(f"Fetch Error: {e}")
        return PRODUCT_CACHE["data"] or []

# --- ROUTES ---

@app.route('/')
def home():
    products = fetch_products()
    # Extract unique categories for the filter
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

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Admin Panel always gets FRESH data (no cache) to ensure accurate stock management
    products = fetch_products(force_refresh=True)
    products.sort(key=lambda x: x.get('name', ''))
    
    grouped = {}
    for p in products:
        cat = p.get('category') or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    
    # Get Override settings
    settings_doc = get_ref('settings').document('stock_override').get()
    override_val = settings_doc.to_dict().get('value', 'off') if settings_doc.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override_val)

# --- API ENDPOINTS (Optimized) ---

@app.route('/api/get-data')
def get_data():
    # Uses cache for speed when updating stock icons/indicators
    products = fetch_products()
    stock_map = {str(p.get('id')): p.get('stock', 999) for p in products}
    return jsonify({"stock": stock_map, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
        # Clear cache so users see the change immediately
        PRODUCT_CACHE["data"] = None 
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        for item in data.get('items', []):
            doc_ref = get_ref('products').document(str(item['id']))
            doc = doc_ref.get()
            if doc.exists:
                current_stock = doc.to_dict().get('stock', 0)
                new_stock = max(0, current_stock - int(item['qty']))
                doc_ref.update({'stock': new_stock})
        PRODUCT_CACHE["data"] = None # Clear cache
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
            snap = doc_ref.get()
            current_stock = snap.to_dict().get('stock', 999) if snap.exists else 999
            
            p_data = {
                'id': int(p_id),
                'name': item.get('name_kh') or item['name'],
                'price': item['price'],
                'image': item['image'],
                'category': item['categories'][0] if item.get('categories') else "General",
                'stock': current_stock
            }
            batch.set(doc_ref, p_data)
        batch.commit()
        PRODUCT_CACHE["data"] = None # Clear cache
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

