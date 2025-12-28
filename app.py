import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

# --- INITIALIZATION ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025_secure')

# --- FIREBASE SETUP ---
service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

db = None
if service_account_info:
    try:
        # Step 1: Parse the JSON key
        cred_dict = json.loads(service_account_info.strip())
        
        # Step 2: Initialize Firebase (prevent double init)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        # Step 3: Connect to Firestore
        db = firestore.client()
        print("✅ Firestore Connected Successfully")
    except Exception as e:
        print(f"❌ Firebase Init Error: {e}")
else:
    print("❌ Critical: FIREBASE_SERVICE_ACCOUNT not found in Render settings.")

# Use the exact Project ID from your key
APP_ID = "somphea-reak"

def get_products_ref():
    if not db: return None
    return db.collection('artifacts').document(APP_ID).collection('public').document('data').collection('products')

def get_settings_ref():
    if not db: return None
    return db.collection('artifacts').document(APP_ID).collection('public').document('data').collection('settings')

# --- CONFIG ---
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')

# --- ROUTES ---

@app.route('/')
def home():
    if not db:
        return "Database Connection Error. Please check Render Environment Variables and Firestore Native Mode."
    
    try:
        docs = get_products_ref().stream()
        all_p = [doc.to_dict() for doc in docs]
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        return render_template('home.html', products=all_p, subcategories=categories)
    except Exception as e:
        if "database (default) does not exist" in str(e).lower():
            return "❌ ERROR: Firestore is not in 'Native Mode'. Go to the Google Cloud link provided in the previous message."
        return f"Error: {str(e)}"

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
    
    try:
        ref = get_products_ref()
        docs = ref.stream()
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
    except Exception as e:
        return f"Admin Panel Error: {str(e)}"

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    try:
        docs = get_products_ref().stream()
        stock_map = {str(doc.id): doc.to_dict().get('stock', 999) for doc in docs}
        override_doc = get_settings_ref().document('stock_override').get()
        override_val = override_doc.to_dict().get('value', 'off') if override_doc.exists else 'off'
        return jsonify({"stock": stock_map, "override": override_val})
    except:
        return jsonify({"stock": {}, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p_id = str(data['id'])
    get_products_ref().document(p_id).update({'stock': int(data['amount'])})
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

