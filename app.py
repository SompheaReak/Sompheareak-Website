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
        # Cleanup potential formatting issues from copy-pasting
        clean_info = service_account_info.strip()
        cred_dict = json.loads(clean_info)
        
        # Check if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
    except Exception as e:
        print(f"❌ Firebase Init Error: {e}")
else:
    print("❌ Critical: FIREBASE_SERVICE_ACCOUNT not found in Render settings.")

APP_ID = "somphea-reak-studio"

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
    try:
        ref = get_products_ref()
        if ref:
            docs = ref.stream()
            all_p = [doc.to_dict() for doc in docs]
        else:
            all_p = []
        
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        # Ensure your html files are in the /templates folder
        return render_template('home.html', products=all_p, subcategories=categories)
    except Exception as e:
        return f"Home Page Error: {str(e)}. Make sure home.html is in the 'templates' folder."

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
        all_p = [doc.to_dict() for doc in ref.stream()] if ref else []
        all_p.sort(key=lambda x: x.get('name', ''))
        
        grouped = {}
        for p in all_p:
            cat = p.get('category') or "General"
            if cat not in grouped: grouped[cat] = []
            grouped[cat].append(p)
            
        settings_ref = get_settings_ref()
        override_val = 'off'
        if settings_ref:
            override_doc = settings_ref.document('stock_override').get()
            if override_doc.exists:
                override_val = override_doc.to_dict().get('value', 'off')
        
        return render_template('admin_panel.html', grouped=grouped, override=override_val)
    except Exception as e:
        return f"Admin Panel Error: {str(e)}"

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    try:
        ref = get_products_ref()
        stock_map = {}
        if ref:
            docs = ref.stream()
            stock_map = {str(doc.id): doc.to_dict().get('stock', 999) for doc in docs}
        
        settings_ref = get_settings_ref()
        override_val = 'off'
        if settings_ref:
            doc = settings_ref.document('stock_override').get()
            if doc.exists: override_val = doc.to_dict().get('value', 'off')
            
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
    if not products_ref: return jsonify(success=False, error="No DB")
    
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

# ... Other admin routes (reset_all, process_receipt) follow the same ref logic

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

