import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

# --- INITIALIZATION ---
app = Flask(__name__)
# Keep your secret key safe in an environment variable too
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025_secure')

# --- FIREBASE SETUP (This is the SAFE way) ---
# This line tells the code: "Look at Render's settings to find the key"
service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if service_account_info:
    # We turn the text from Render back into a proper key
    cred_dict = json.loads(service_account_info)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    # If the key isn't found (like when testing locally)
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except:
        print("Warning: Firebase key not found in Environment Variables.")

db = firestore.client()
APP_ID = "somphea-reak-studio"

# Helper functions to get database locations
def get_products_ref():
    return db.collection('artifacts').document(APP_ID).collection('public').document('data').collection('products')

def get_settings_ref():
    return db.collection('artifacts').document(APP_ID).collection('public').document('data').collection('settings')

# --- CONFIG ---
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- ROUTES ---

@app.route('/')
def home():
    docs = get_products_ref().stream()
    all_p = [doc.to_dict() for doc in docs]
    categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
    return render_template('home.html', products=all_p, subcategories=categories)

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

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
    
    docs = get_products_ref().stream()
    all_p = [doc.to_dict() for doc in docs]
    all_p.sort(key=lambda x: x.get('name', ''))
    
    grouped = {}
    for p in all_p:
        cat = p.get('category') or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
        
    override_doc = get_settings_ref().document('stock_override').get()
    override_val = override_doc.to_dict().get('value', 'off') if override_doc.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override_val)

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    docs = get_products_ref().stream()
    stock_map = {str(doc.id): doc.to_dict().get('stock', 999) for doc in docs}
    
    override_doc = get_settings_ref().document('stock_override').get()
    override_val = override_doc.to_dict().get('value', 'off') if override_doc.exists else 'off'
    
    return jsonify({"stock": stock_map, "override": override_val})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p_id = str(data['id'])
    get_products_ref().document(p_id).update({'stock': int(data['amount'])})
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    get_settings_ref().document('stock_override').set({'value': val})
    return jsonify(success=True)

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    products_ref = get_products_ref()
    batch = db.batch()
    for item in items:
        p_id = str(item['id'])
        doc_ref = products_ref.document(p_id)
        existing = doc_ref.get()
        current_stock = existing.to_dict().get('stock', 999) if existing.exists else 999
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
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    products_ref = get_products_ref()
    for item in data.get('items', []):
        p_id = str(item['id'])
        doc_ref = products_ref.document(p_id)
        doc = doc_ref.get()
        if doc.exists:
            current_stock = doc.to_dict().get('stock', 0)
            new_stock = max(0, current_stock - int(item['qty']))
            doc_ref.update({'stock': new_stock})
    return jsonify(success=True)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    docs = get_products_ref().stream()
    batch = db.batch()
    for doc in docs:
        batch.update(doc.reference, {'stock': 999})
    batch.commit()
    return jsonify(success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

