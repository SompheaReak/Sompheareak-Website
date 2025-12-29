import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- SECURE CONFIGURATION ---
# We use os.environ.get() so NO secrets are hardcoded in the file
app.secret_key = os.environ.get('SECRET_KEY', 'default-secure-key-123')
ADMIN_PASS = os.environ.get('ADMIN_PASS') # No default here to prevent leaks
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

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
        print(f"Firebase Init Error: {e}")

def get_ref(collection_name):
    if not db: return None
    return db.collection('artifacts').document(PROJECT_ID).collection('public').document('data').collection(collection_name)

# --- ROUTES ---

@app.route('/')
def home():
    if not db:
        return "<h1>Database Error</h1><p>Ensure FIREBASE_SERVICE_ACCOUNT is set in Render Environment.</p>"
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
        if not all_p:
            return "<h1>Shop is Empty</h1><p>Go to /admin/login and Sync Catalog.</p>"
        categories = sorted(list(set(p.get('category', 'General') for p in all_p if p.get('category'))))
        return render_template('home.html', products=all_p, subcategories=categories)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Check against the secret password in Render
        if ADMIN_PASS and request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    try:
        docs = get_ref('products').stream()
        all_p = [doc.to_dict() for doc in docs]
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
    if not db: return jsonify(success=False)
    # Put your product list here
    CATALOG = [
        {"id": 1, "name": "Classic Bracelet", "price": 15.0, "image": "bracelet1.jpg", "category": "Bracelets"},
    ]
    try:
        batch = db.batch()
        for item in CATALOG:
            doc_ref = get_ref('products').document(str(item['id']))
            snap = doc_ref.get()
            item['stock'] = snap.to_dict().get('stock', 999) if snap.exists else 999
            batch.set(doc_ref, item)
        batch.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

