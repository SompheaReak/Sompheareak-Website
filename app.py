import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_2025_secure_key')

# --- DEBUGGING HELPERS ---
def get_debug_info():
    return {
        "firebase_key_exists": "FIREBASE_SERVICE_ACCOUNT" in os.environ,
        "admin_pass_exists": "ADMIN_PASS" in os.environ,
        "templates_folder_exists": os.path.exists('templates'),
        "home_html_exists": os.path.exists('templates/home.html')
    }

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
        db_error = f"Firebase Connection Error: {str(e)}"
else:
    db_error = "Missing FIREBASE_SERVICE_ACCOUNT in Render Environment settings."

def get_ref(collection_name):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(collection_name)

# --- ADMIN CONFIG ---
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')

# --- ROUTES ---

@app.route('/')
def home():
    debug = get_debug_info()
    if not debug["templates_folder_exists"]:
        return "<h1>Error: Folder 'templates' not found!</h1><p>Create a folder named 'templates' on GitHub and move your .html files inside it.</p>"

    if not db:
        return f"<h1>Database Not Connected</h1><p>{db_error}</p>"

    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        
        if not all_p:
            return "<h1>Shop is Empty</h1><p>Database connected! Please go to <b>/admin/login</b> and click <b>'Sync Catalog'</b> to load your products.</p>"
            
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        return render_template('home.html', products=all_p, subcategories=categories)
    except Exception as e:
        return f"<h1>Application Error</h1><p>{str(e)}</p>"

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
    except Exception as e:
        return f"Admin Error: {str(e)}"

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    if not db: return jsonify(success=False, error="No DB")
    
    # Put your product list here exactly as you have it in your catalog
    CATALOG_DATA = [
        {"id": 1, "name": "Sample Product", "price": 10.0, "image": "sample.jpg", "category": "General"},
        # Add your actual products here
    ]
    
    try:
        batch = db.batch()
        for item in CATALOG_DATA:
            doc_ref = get_ref('products').document(str(item['id']))
            # Keep existing stock if product already exists
            snap = doc_ref.get()
            item['stock'] = snap.to_dict().get('stock', 999) if snap.exists else 999
            batch.set(doc_ref, item)
        batch.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

