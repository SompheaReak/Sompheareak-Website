import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. CLOUD STORAGE SETUP (Firestore) ---
# Use the environment variables provided by the platform
firebase_config_raw = os.environ.get('__firebase_config')
app_id = os.environ.get('__app_id', 'somphea-reak-studio')

if firebase_config_raw:
    fb_config = json.loads(firebase_config_raw)
    # Note: In a real Render/PythonAnywhere env, you would use a service_account.json
    # For this environment, we initialize with the provided config.
    if not firebase_admin._apps:
        cred = credentials.Certificate(fb_config) # Assumes config is service account format
        firebase_admin.initialize_app(cred)
else:
    # Fallback for local testing if no config exists
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

db = firestore.client()

# Paths (Rule 1: Strict Paths)
# Public data: artifacts/{appId}/public/data/{collection}
def get_coll(name):
    return db.collection('artifacts').document(app_id).collection('public').document('data').collection(name)

# --- 2. CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})
    except: pass

# --- 3. MAIN ROUTES ---

@app.route('/')
def home():
    return render_template('custom_bracelet.html')

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
    
    # Get all products from Cloud
    docs = get_coll('products').stream()
    all_p = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        all_p.append(p)
        
    grouped = {}
    for p in all_p:
        cat = p.get('category', 'General')
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
        
    # Get Master Switch from Cloud
    sett_ref = get_coll('settings').document('stock_override').get()
    override_val = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override_val)

# --- 4. API (STUDIO CONNECTION) ---

@app.route('/api/get-data')
def get_data():
    docs = get_coll('products').stream()
    stock_map = {d.id: d.to_dict().get('stock', 0) for d in docs}
    
    sett_ref = get_coll('settings').document('stock_override').get()
    override = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'
    
    return jsonify({"stock": stock_map, "override": override})

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    batch = db.batch()
    for item in data.get('items', []):
        doc_id = str(item['id'])
        doc_ref = get_coll('products').document(doc_id)
        
        # Check if exists to avoid overwriting stock
        if not doc_ref.get().exists:
            name = item.get('name_kh') or item.get('name') or "Item"
            batch.set(doc_ref, {
                "name": name,
                "price": item['price'],
                "image": item['image'],
                "category": item['categories'][0],
                "stock": 0
            })
    batch.commit()
    return jsonify(success=True)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    doc_ref = get_coll('products').document(str(data['id']))
    doc_ref.update({"stock": int(data['amount'])})
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    get_coll('settings').document('stock_override').set({"value": val})
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

