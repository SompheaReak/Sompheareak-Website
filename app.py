import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_2025_secure')
ADMIN_PASS = os.environ.get('ADMIN_PASS')

# --- FIREBASE SETUP ---
service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
db = None
PROJECT_ID = "somphea-reak"

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

def get_ref(col):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(col)

# --- 1. PAGE ROUTES (Add all your HTML files here) ---

@app.route('/')
def home():
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        return render_template('home.html', products=all_p, subcategories=categories)
    except:
        return render_template('home.html', products=[], subcategories=[])

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/lego')
def lego_page():
    return render_template('LEGO.html')

# --- ADD MORE PAGES HERE ---
# If you have a file named 'rings.html', you would add:
# @app.route('/rings')
# def rings_page():
#     return render_template('rings.html')

# --- 2. ADMIN & AUTH ---

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
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        all_p.sort(key=lambda x: x.get('name', ''))
        grouped = {}
        for p in all_p:
            cat = p.get('category') or "General"
            if cat not in grouped: grouped[cat] = []
            grouped[cat].append(p)
        return render_template('admin_panel.html', grouped=grouped)
    except:
        return render_template('admin_panel.html', grouped={})

# --- 3. DATABASE SYNC & STOCK ---

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    if not db: return jsonify(success=False)
    
    # MASTER CATALOG: Add EVERY item from EVERY page here
    # This is how the database knows what to track
    CATALOG_DATA = [
        {"id": 1, "name": "Classic Bracelet", "price": 15.0, "image": "bracelet1.jpg", "category": "Bracelets"},
        {"id": 2, "name": "Lego Set A", "price": 45.0, "image": "lego1.jpg", "category": "LEGO"},
        # Add all your items here...
    ]
    
    try:
        batch = db.batch()
        for item in CATALOG_DATA:
            doc_ref = get_ref('products').document(str(item['id']))
            snap = doc_ref.get()
            item['stock'] = snap.to_dict().get('stock', 999) if snap.exists else 999
            batch.set(doc_ref, item)
        batch.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    get_ref('products').document(str(data['id'])).update({'stock': int(data['amount'])})
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    for item in data.get('items', []):
        doc_ref = get_ref('products').document(str(item['id']))
        doc = doc_ref.get()
        if doc.exists:
            new_stock = max(0, doc.to_dict().get('stock', 0) - int(item['qty']))
            doc_ref.update({'stock': new_stock})
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

