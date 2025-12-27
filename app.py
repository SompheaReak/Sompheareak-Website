import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_safe_key_2025')

# --- 1. CLOUD DATABASE CONNECTION ---
# We use an environment variable for the key to keep it safe
firebase_key = os.environ.get('FIREBASE_KEY')

if firebase_key:
    # Use the key if provided in deployment settings
    cred = credentials.Certificate(json.loads(firebase_key))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
else:
    # Fallback: If no key is found, app won't crash but won't save permanently
    # You MUST add the FIREBASE_KEY in your Render/Host settings
    print("WARNING: No Firebase Key found. Data will not persist.")
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

db = firestore.client()

# --- CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- 2. ROUTES ---

@app.route('/')
def home():
    # Fix: Homepage is now the Shop Menu
    docs = db.collection('products').stream()
    products = [d.to_dict() for d in docs]
    
    # Extract unique categories
    cats = list(set(p.get('category') for p in products if p.get('category')))
    return render_template('home.html', menu=cats)

@app.route('/studio')
def studio():
    # Fix: This is the design tool
    return render_template('custom_bracelet.html')

# --- 3. CLOUD API ---

@app.route('/api/get-data')
def get_data():
    # Read stock from Cloud
    docs = db.collection('products').stream()
    stock_map = {d.id: d.to_dict().get('stock', 0) for d in docs}
    
    # Read Master Switch
    sett_ref = db.collection('settings').document('override').get()
    override = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'
    
    return jsonify({"stock": stock_map, "override": override})

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    # This saves your 500 items to the Cloud (Only runs once per item)
    data = request.json
    items = data.get('items', [])
    batch = db.batch()
    
    for item in items:
        doc_ref = db.collection('products').document(str(item['id']))
        # Only create if it doesn't exist (prevents overwriting stock)
        if not doc_ref.get().exists:
            name = item.get('name_kh') or item.get('name') or "Item"
            batch.set(doc_ref, {
                "name": name,
                "price": item['price'],
                "image": item['image'],
                "category": item['categories'][0],
                "stock": 0 # Default stock
            })
    
    batch.commit()
    return jsonify(success=True)

# --- 4. ADMIN ROUTES ---

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
    
    # Fetch all from Cloud
    docs = db.collection('products').stream()
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
        
    sett_ref = db.collection('settings').document('override').get()
    override = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'
    
    return render_template('admin_panel.html', grouped=grouped, override=override)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    # Update Cloud
    db.collection('products').document(str(data['id'])).update({"stock": int(data['amount'])})
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    db.collection('settings').document('override').set({"value": val})
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    items_list = []
    total_bill = 0
    
    for item in data['items']:
        ref = db.collection('products').document(str(item['id']))
        doc = ref.get()
        if doc.exists:
            current_stock = doc.to_dict().get('stock', 0)
            new_stock = max(0, current_stock - int(item['qty']))
            ref.update({"stock": new_stock})
            
            p_data = doc.to_dict()
            items_list.append(f"• {p_data.get('name')} x{item['qty']}")
            total_bill += (p_data.get('price', 0) * item['qty'])
            
    # Send Telegram
    try:
        msg = f"<b>🔔 NEW SALE</b>\n" + "\n".join(items_list) + f"\n<b>Total: {total_bill}៛</b>"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except: pass
    
    return jsonify(success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


