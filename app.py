import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

# --- INITIALIZATION ---
app = Flask(__name__)

# --- SECURE CONFIG (Fetched from Render Environment Variables) ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025_secure')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- FIREBASE CLOUD SETUP ---
service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
db = None
PROJECT_ID = "somphea-reak-website" # Will be updated by your key

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

# Helper to get Firestore references
def get_ref(collection_name):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(collection_name)

# --- ROUTES ---

@app.route('/')
def home():
    if not db:
        return "<h1>Database Connection Error</h1><p>Ensure FIREBASE_SERVICE_ACCOUNT is set in Render.</p>"
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        return render_template('home.html', products=all_p, subcategories=categories)
    except Exception as e:
        return f"Home Error: {str(e)}"

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
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        all_p.sort(key=lambda x: x.get('name', ''))
        
        grouped = {}
        for p in all_p:
            cat = p.get('category') or "General"
            if cat not in grouped: grouped[cat] = []
            grouped[cat].append(p)
            
        # Get Stock Override setting
        settings_doc = get_ref('settings').document('stock_override').get()
        override_val = settings_doc.to_dict().get('value', 'off') if settings_doc.exists else 'off'
        
        return render_template('admin_panel.html', grouped=grouped, override=override_val)
    except:
        return render_template('admin_panel.html', grouped={}, override="off")

# --- API ENDPOINTS (Updated for Firebase) ---

@app.route('/api/get-data')
def get_data():
    try:
        docs = get_ref('products').stream()
        stock_map = {str(doc.id): doc.to_dict().get('stock', 999) for doc in docs}
        settings_doc = get_ref('settings').document('stock_override').get()
        override_val = settings_doc.to_dict().get('value', 'off') if settings_doc.exists else 'off'
        return jsonify({"stock": stock_map, "override": override_val})
    except:
        return jsonify({"stock": {}, "override": "off"})

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    get_ref('settings').document('stock_override').set({'value': val})
    return jsonify(success=True)

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
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    """Syncs the product list from the website UI to the Cloud database"""
    if not db: return jsonify(success=False)
    data = request.json
    items = data.get('items', [])
    try:
        batch = db.batch()
        for item in items:
            p_id = str(item['id'])
            doc_ref = get_ref('products').document(p_id)
            
            # Check if product exists to preserve stock
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
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    try:
        docs = get_ref('products').stream()
        batch = db.batch()
        for doc in docs:
            batch.update(doc.reference, {'stock': 999})
        batch.commit()
        return jsonify(success=True)
    except:
        return jsonify(success=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

