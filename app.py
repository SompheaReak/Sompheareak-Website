import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_2025_cloud')

# --- 1. FIREBASE CLOUD SETUP ---
# You need to set an environment variable named 'FIREBASE_KEY' with your JSON key content
fb_key_json = os.environ.get('FIREBASE_KEY')

if fb_key_json:
    try:
        cred_dict = json.loads(fb_key_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase Init Error: {e}")
        firebase_admin.initialize_app()
else:
    # Fallback for local testing or if initialized elsewhere
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

db = firestore.client()
# Base path for your data
def get_ref(coll):
    # Rule 1: Use strict paths
    app_id = "somphea-reak-studio"
    return db.collection('artifacts').document(app_id).collection('public').document('data').collection(coll)

# --- 2. CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=5)
    except: pass

# --- 3. ROUTES ---

@app.route('/')
def home():
    return render_template('custom-bracelet.html')

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
    
    # Fetch products from Cloud
    docs = get_ref('products').stream()
    all_p = []
    for d in docs:
        item = d.to_dict()
        item['id'] = d.id
        all_p.append(item)
    
    grouped = {}
    for p in all_p:
        cat = p.get('category', 'General')
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
        
    # Get Master Switch
    m_ref = get_ref('settings').document('stock_override').get()
    override = m_ref.to_dict().get('value', 'off') if m_ref.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override)

# --- 4. API ---

@app.route('/api/get-data')
def get_data():
    docs = get_ref('products').stream()
    stock_map = {d.id: d.to_dict().get('stock', 0) for d in docs}
    m_ref = get_ref('settings').document('stock_override').get()
    override = m_ref.to_dict().get('value', 'off') if m_ref.exists else 'off'
    return jsonify({"stock": stock_map, "override": override})

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    batch = db.batch()
    for item in items:
        doc_id = str(item['id'])
        doc_ref = get_ref('products').document(doc_id)
        # Only create if it doesn't exist so we don't reset stock to 0
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
    doc_ref = get_ref('products').document(str(data['id']))
    doc_ref.update({"stock": int(data['amount'])})
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    get_ref('settings').document('stock_override').set({"value": val})
    return jsonify(success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

