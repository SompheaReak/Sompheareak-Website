import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIG (Fetched from Render) ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_2025')
ADMIN_PASS = os.environ.get('ADMIN_PASS')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- FIREBASE CLOUD SETUP ---
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
        print(f"✅ Cloud Database Connected: {PROJECT_ID}")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")

# --- TURBO CACHE (Solves Lag) ---
CACHE = {
    "products": [],
    "last_sync": 0,
    "ttl": 600  # Refresh every 10 minutes
}

def get_ref(col):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(col)

def fetch_all(force=False):
    global CACHE
    now = time.time()
    if not force and CACHE["products"] and (now - CACHE["last_sync"] < CACHE["ttl"]):
        return CACHE["products"]
    try:
        docs = get_ref('products').stream()
        p_list = [doc.to_dict() for doc in docs]
        CACHE["products"] = p_list
        CACHE["last_sync"] = now
        return p_list
    except:
        return CACHE["products"] or []

# --- ROUTES (Your Preferred Logic) ---

@app.route('/')
def home():
    all_p = fetch_all()
    # Extract unique categories
    subcategories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
    return render_template('home.html', products=all_p, subcategories=subcategories)

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if ADMIN_PASS and request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = fetch_all(force=True)
    all_p.sort(key=lambda x: x.get('name', ''))
    
    grouped = {}
    for p in all_p:
        cat = p.get('category') or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    
    # Get Safety Lock setting
    sett = get_ref('settings').document('stock_override').get()
    override = sett.to_dict().get('value', 'off') if sett.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override)

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    all_p = fetch_all()
    sett = get_ref('settings').document('stock_override').get()
    override = sett.to_dict().get('value', 'off') if sett.exists else 'off'
    return jsonify({
        "stock": {str(p['id']): p.get('stock', 999) for p in all_p},
        "override": override
    })

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    try:
        get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
        CACHE["products"] = [] # Force refresh
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
                curr = doc.to_dict().get('stock', 0)
                doc_ref.update({'stock': max(0, curr - int(item['qty']))})
        CACHE["products"] = []
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
            # Check for existing to preserve stock
            snap = doc_ref.get()
            stock = snap.to_dict().get('stock', 999) if snap.exists else 999
            
            p_data = {
                'id': int(p_id),
                'name': item.get('name_kh') or item['name'],
                'price': item['price'],
                'image': item['image'],
                'category': item['categories'][0] if item.get('categories') else "General",
                'stock': stock
            }
            batch.set(doc_ref, p_data)
        batch.commit()
        CACHE["products"] = []
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    try:
        docs = get_ref('products').stream()
        batch = db.batch()
        for doc in docs:
            batch.update(doc.reference, {'stock': 999})
        batch.commit()
        CACHE["products"] = []
        return jsonify(success=True)
    except:
        return jsonify(success=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

