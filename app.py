import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_ultimate_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# ==========================================
# 1. PRODUCT CATALOG
# ==========================================
PRODUCT_CATALOG = [
    # --- ITALY BRACELET ---
    # --- Charm
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Italy Bracelet", "Charm"], "subcategory": "Charms"},
]

# --- SUBCATEGORIES MAP ---
SUBCATEGORIES_MAP = {
    "Hot Sale": [],
    "LEGO": ["LEGO Ninjago", "LEGO Anime", "Formula 1", "Lego WWII"],
    "LEGO Ninjago": ["Dragon Rising", "Season 1", "Season 2", "Season 13"],
    "LEGO Anime": ["One Piece", "Demon Slayer"],
    "Keychain": ["Gun Keychains", "Anime Keychains"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet"],
    "Toy": ["General Toys"],
}

# --- NAVIGATION MENU ---
NAV_MENU = [
    "Hot Sale",
    "LEGO", 
    "Keychain",
    "Accessories",
    "Toy",
    "Italy Bracelet", 
    "Lucky Draw"      
]

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=0)

# --- SYNC ENGINE ---
def sync_catalog():
    try:
        inspector = db.inspect(db.engine)
        if not inspector.has_table("product"): db.create_all()
        
        print("🔄 Syncing Catalog...")
        for item in PRODUCT_CATALOG:
            existing = Product.query.get(item['id'])
            cat_str = ", ".join(item.get('categories', []))
            
            # Handle subcategory (string or list)
            sub_val = item.get('subcategory', 'General')
            if isinstance(sub_val, list):
                sub_str = ", ".join(sub_val)
            else:
                sub_str = str(sub_val)
            
            if existing:
                existing.name_kh = item['name_kh']
                existing.price = item['price']
                existing.image = item['image']
                existing.categories_str = cat_str
                existing.subcategory_str = sub_str
            else:
                new_p = Product(
                    id=item['id'], name_kh=item['name_kh'], price=item['price'],
                    image=item['image'], categories_str=cat_str, subcategory_str=sub_str, stock=0
                )
                db.session.add(new_p)
        db.session.commit()
        print("✅ Sync Complete!")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('category_view', category_name='Hot Sale'))

@app.route('/category/<category_name>')
def category_view(category_name):
    # 1. Special Redirects
    if category_name == 'Italy Bracelet': return redirect(url_for('custom_bracelet'))
    if category_name == 'Lucky Draw': return redirect(url_for('lucky_draw'))

    # 2. Get Products
    all_products = Product.query.all()
    # Filter: Show product if category_name matches ANY of its categories
    filtered_products = [p for p in all_products if category_name in p.categories_str]

    # 3. Get Subcategories
    subs = SUBCATEGORIES_MAP.get(category_name, [])

    return render_template('home.html', 
                           products=filtered_products, 
                           current_category=category_name, 
                           menu=NAV_MENU,
                           subcategories=subs,
                           cart=session.get('cart', []))

@app.route('/subcategory/<sub_name>')
def subcategory_view(sub_name):
    # Route for clicking subcategory pills (e.g., /subcategory/LEGO%20Ninjago)
    all_products = Product.query.all()
    # Filter by checking if sub_name is in categories_str OR subcategory_str
    # This ensures items tagged with "LEGO Ninjago" in categories OR subcategory show up
    filtered = [p for p in all_products if sub_name in p.categories_str or sub_name in p.subcategory_str]
    
    return render_template('home.html', 
                           products=filtered, 
                           current_category=sub_name, 
                           menu=NAV_MENU,
                           subcategories=[], # Clear subs when inside a sub
                           cart=session.get('cart', []))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    all_products = Product.query.all()
    filtered = [p for p in all_products if query in p.name_kh.lower()]
    return render_template('home.html', 
                           products=filtered, 
                           current_category=f"Search: {query}", 
                           menu=NAV_MENU,
                           subcategories=[],
                           cart=session.get('cart', []))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    p_id = request.form.get('product_id')
    if p_id:
        cart = session.get('cart', [])
        cart.append(p_id)
        session['cart'] = cart
        return jsonify({"success": True, "cart_count": len(cart)})
    return jsonify({"success": False})

@app.route('/cart')
def view_cart():
    # Basic Cart View logic - for now redirect to home or render simple template
    cart_ids = session.get('cart', [])
    cart_items = []
    total = 0
    for pid in cart_ids:
        p = Product.query.get(pid)
        if p: 
            cart_items.append(p)
            total += p.price
    # If you have a cart.html, render it. If not, just show a basic list or redirect.
    # For this fix, I'll return a simple JSON dump or redirect back to shop if no template exists.
    return render_template('home.html', products=cart_items, current_category="My Cart", menu=NAV_MENU, subcategories=[], cart=cart_ids)

@app.route('/custom-bracelet')
def custom_bracelet():
    all_products = Product.query.all()
    studio_items = [p for p in all_products if "Italy Bracelet" in p.categories_str]
    
    products_json = [{
        "id": p.id, "name_kh": p.name_kh, "price": p.price, 
        "image": p.image, "stock": p.stock, 
        "categories": p.categories_str.split(', ')
    } for p in studio_items]
    
    return render_template('custom_bracelet.html', products=products_json)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('lucky_draw.html') 

# --- ADMIN ROUTES ---
@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    all_products = Product.query.all()
    stats = {
        "total": len(all_products),
        "out": len([p for p in all_products if p.stock <= 0]),
        "low": len([p for p in all_products if 0 < p.stock <= 5])
    }
    
    grouped = {}
    for p in all_products:
        cat = p.categories_str.split(', ')[0] if p.categories_str else "Uncategorized"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
        
    return render_template('admin_panel.html', grouped=grouped, stats=stats)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

# --- STARTUP ---
with app.app_context():
    try:
        db.create_all()
        sync_catalog()
    except: pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


