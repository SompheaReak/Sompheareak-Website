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
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Italy Bracelet"], "subcategory": "Charms"},
    {"id": 2001, "name_kh": "Flag Charm", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Italy Bracelet"], "subcategory": "Flags"},

    # --- LEGO ---
    {"id": 9001, "name_kh": "Kai - Ninjago", "price": 5000, "image": "https://m.media-amazon.com/images/I/51+u+A-uG+L._AC_UF894,1000_QL80_.jpg", "categories": ["LEGO", "LEGO Ninjago"], "subcategory": "Season 1"},
    {"id": 9002, "name_kh": "Luffy - One Piece", "price": 6000, "image": "https://m.media-amazon.com/images/I/61Itk-lF+PL.jpg", "categories": ["LEGO", "LEGO Anime"], "subcategory": "One Piece"},
    
    # --- KEYCHAINS ---
    {"id": 8001, "name_kh": "Gun Keychain A", "price": 2500, "image": "https://down-ph.img.susercontent.com/file/sg-11134201-22100-bf65465465iv8c", "categories": ["Keychain"], "subcategory": "Gun Keychains"},

    # --- HOT SALE ---
    {"id": 9999, "name_kh": "Special Set", "price": 10000, "image": "/static/images/special.jpg", "categories": ["Hot Sale", "LEGO"], "subcategory": "Sets"},
]

# --- 2. SUBCATEGORIES MAP (Added this back) ---
SUBCATEGORIES_MAP = {
    "Hot Sale": [],
    "LEGO": ["LEGO Ninjago", "LEGO Anime", "Formula 1", "Lego WWII"],
    "LEGO Ninjago": ["Dragon Rising", "Season 1", "Season 2", "Season 13"],
    "LEGO Anime": ["One Piece", "Demon Slayer"],
    "Keychain": ["Gun Keychains", "Anime Keychains"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet"],
    "Toy": ["General Toys"],
}

# --- MAIN NAVIGATION ---
NAV_MENU = [
    "Hot Sale",
    "LEGO", 
    "Keychain",
    "Accessories",
    "Toy",
    "Italy Bracelet", # Redirects to Studio
    "Lucky Draw"      # Redirects to Game
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
            sub_str = item.get('subcategory', 'General')
            
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

    # 3. Get Subcategories (Added this logic back)
    subs = SUBCATEGORIES_MAP.get(category_name, [])

    return render_template('home.html', 
                           products=filtered_products, 
                           current_category=category_name, 
                           menu=NAV_MENU,
                           subcategories=subs)

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


