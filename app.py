import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_safe_key_2025')

# --- FIREBASE SETUP ---
firebase_key = os.environ.get('FIREBASE_KEY')
if firebase_key:
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(firebase_key))
        firebase_admin.initialize_app(cred)
else:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
db = firestore.client()

# --- ROUTES ---

@app.route('/')
def home():
    # Fetch all products for the grid
    docs = db.collection('products').stream()
    products = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        products.append(p)
    
    # Get cart count
    cart = session.get('cart', [])
    
    return render_template('home.html', products=products, cart_len=len(cart))

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
    return render_template('home.html', products=products, cart_len=len(cart))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    docs = db.collection('products').stream()
    results = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        if query in p.get('name', '').lower():
            results.append(p)
    cart = session.get('cart', [])
    return render_template('home.html', products=results, cart_len=len(cart))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get('product_id')
    qty = int(request.form.get('quantity', 1))
    
    cart = session.get('cart', [])
    cart.append({'id': pid, 'qty': qty})
    session['cart'] = cart
    
    return jsonify(success=True, cart_count=len(cart))

@app.route('/cart')
def view_cart():
    # Simple cart view (expand later if needed)
    cart = session.get('cart', [])
    return f"Cart has {len(cart)} items. <a href='/'>Go Back</a>"

@app.route('/lucky-draw')
def lucky_draw():
    return "Lucky Draw Game Coming Soon! <a href='/'>Go Back</a>"

# --- API FOR STUDIO (Keep this for the custom bracelet page) ---
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
    for item in data.get('items', []):
        doc_ref = db.collection('products').document(str(item['id']))
        if not doc_ref.get().exists:
            batch.set(doc_ref, {
                "name": item.get('name_kh') or item.get('name') or "Item",
                "price": item['price'],
                "image": item['image'],
                "category": item['categories'][0],
                "stock": 0
            })
    batch.commit()
    return jsonify(success=True)

# --- ADMIN ROUTES ---
@app.route('/admin/panel')
def admin_panel():
    # (Simplified for brevity, assumes you have admin_panel.html)
    return render_template('admin_panel.html', grouped={}, override='off')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


