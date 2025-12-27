import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
# SECURITY NOTE: In production on Render, set 'SECRET_KEY' in your Environment Variables.
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_safe_key_2025')

# --- FIREBASE SETUP ---
firebase_key = os.environ.get('FIREBASE_KEY')
if firebase_key:
    # Production Setup
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(firebase_key))
        firebase_admin.initialize_app(cred)
else:
    # Local Development Setup
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        except:
            print("Warning: Firebase credentials not found. App may crash if DB is accessed.")
            
db = firestore.client()

# --- ROUTES ---

@app.route('/')
def home():
    # Fetch all products
    docs = db.collection('products').stream()
    products = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        products.append(p)
    
    # Cart Session
    cart = session.get('cart', [])
    
    # FIX: Pass 'cart' (the list) instead of 'cart_len' so {{ cart|length }} works in HTML
    # FIX: Pass empty 'subcategories' list to prevent errors in HTML
    return render_template('home.html', products=products, cart=cart, subcategories=[])

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/category/<cat_name>')
def category(cat_name):
    docs = db.collection('products').where('category', '==', cat_name).stream()
    products = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        products.append(p)
        
    cart = session.get('cart', [])
    return render_template('home.html', products=products, cart=cart, subcategories=[])

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    docs = db.collection('products').stream()
    results = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        # Simple case-insensitive search
        if query in p.get('name', '').lower():
            results.append(p)
            
    cart = session.get('cart', [])
    return render_template('home.html', products=results, cart=cart, subcategories=[])

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get('product_id')
    qty = int(request.form.get('quantity', 1))
    
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item['id'] == pid:
            item['qty'] += qty
            found = True
            break
    if not found:
        cart.append({'id': pid, 'qty': qty})
        
    session['cart'] = cart
    return jsonify(success=True, cart_count=len(cart))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    # Simple placeholder for cart view
    return f"Cart has {len(cart)} items. <a href='/'>Go Back</a>"

@app.route('/lucky-draw')
def lucky_draw():
    return "Lucky Draw Game Coming Soon! <a href='/'>Go Back</a>"

# --- API FOR STUDIO ---
@app.route('/api/get-data')
def get_data():
    docs = db.collection('products').stream()
    stock_map = {d.id: d.to_dict().get('stock', 0) for d in docs}
    
    sett_ref = db.collection('settings').document('override').get()
    override = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'
    
    return jsonify({"stock": stock_map, "override": override})

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    batch = db.batch()
    count = 0
    
    for item in data.get('items', []):
        doc_ref = db.collection('products').document(str(item['id']))
        doc = doc_ref.get()
        
        if not doc.exists:
            # Note: We save the name under the key "name"
            batch.set(doc_ref, {
                "name": item.get('name_kh') or item.get('name') or "Item",
                "price": item.get('price', 0),
                "image": item.get('image', ''),
                "category": item.get('categories', ['Uncategorized'])[0],
                "stock": 0
            })
            count += 1
            
        if count >= 400:
            batch.commit()
            batch = db.batch()
            count = 0

    if count > 0:
        batch.commit()
        
    return jsonify(success=True)

# --- ADMIN ROUTES ---
@app.route('/admin/panel')
def admin_panel():
    docs = db.collection('products').stream()
    products = []
    for d in docs:
        data = d.to_dict()
        data['id'] = d.id
        products.append(data)
        
    grouped = {}
    for p in products:
        cat = p.get('category', 'Others')
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)
        
    sett_ref = db.collection('settings').document('override').get()
    override = sett_ref.to_dict().get('value', 'off') if sett_ref.exists else 'off'

    return render_template('admin_panel.html', grouped=grouped, override=override)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    data = request.json
    product_id = str(data.get('id'))
    new_amount = int(data.get('amount'))
    
    db.collection('products').document(product_id).update({
        'stock': new_amount
    })
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    data = request.json
    val = data.get('value')
    
    db.collection('settings').document('override').set({
        'value': val
    }, merge=True)
    
    return jsonify(success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


