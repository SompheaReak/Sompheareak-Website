import os
import json
import time
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIG (No Secrets Typed Here) ---
app.secret_key = os.environ.get('SECRET_KEY')
ADMIN_PASS = os.environ.get('ADMIN_PASS')

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
        print(f"Firebase Init Error: {e}")

# --- ULTRA-SPEED MEMORY CACHE ---
# We store EVERYTHING in RAM so the website is instant.
CACHE = {
    "products": [],
    "json_str": "[]",
    "categories": [],
    "last_update": 0,
    "ttl": 1800 # 30 minutes (Website stays fast even if DB is slow)
}

def get_ref(col):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(col)

def refresh_memory(force=False):
    """Fetches data from Taiwan to update the server's memory."""
    global CACHE
    now = time.time()
    if not force and (now - CACHE["last_update"] < CACHE["ttl"]) and CACHE["products"]:
        return

    try:
        if not db: return
        docs = get_ref('products').stream()
        p_list = [doc.to_dict() for doc in docs]
        
        # Update memory
        CACHE["products"] = p_list
        CACHE["json_str"] = json.dumps(p_list)
        CACHE["categories"] = sorted(list(set(p.get('category', 'General') for p in p_list if p.get('category'))))
        CACHE["last_update"] = now
        print("⚡ Memory Cache Updated from Cloud")
    except Exception as e:
        print(f"Cache Refresh Error: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    # Start refresh in a background thread so the user doesn't wait
    threading.Thread(target=refresh_memory).start()
    
    # Send what we already have in memory (Instant)
    return render_template('home.html', 
                           products=CACHE["products"], 
                           products_json=CACHE["json_str"],
                           subcategories=CACHE["categories"])

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/lego')
def lego_page():
    return render_template('LEGO.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if ADMIN_PASS and request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    refresh_memory(force=True) # Admin always sees fresh data
    
    grouped = {}
    for p in CACHE["products"]:
        cat = p.get('category') or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    return render_template('admin_panel.html', grouped=grouped)

# --- FAST API ---

@app.route('/api/get-data')
def get_data():
    """Returns data from memory instantly."""
    stock_map = {str(p.get('id')): p.get('stock', 999) for p in CACHE["products"]}
    return jsonify({"stock": stock_map, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
        # Force memory to update so customers see the change
        refresh_memory(force=True)
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
            p_data = {
                'id': int(p_id),
                'name': item.get('name_kh') or item['name'],
                'price': item['price'],
                'image': item['image'],
                'category': item['categories'][0] if item.get('categories') else "General",
                'stock': 999 
            }
            batch.set(doc_ref, p_data, merge=True)
        batch.commit()
        refresh_memory(force=True)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    # Pre-load memory before starting the app
    refresh_memory(force=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

