import os 
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key'

# --- DATABASE SETUP ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=1)

# --- SUBCATEGORIES MAP ---
subcategories_map = {
    "Hot Sale": [],
    "LEGO Ninjago": ["Dragon Rising","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8","Season 9","Season 10","Season 11","Season 12","Season 13", "Season 14","Season 15"],
    "LEGO Anime": ["One Piece","Demon Slayer"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "Keychain": ["Gun Keychains"],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece","Lego WWII", "Lego ទាហាន"],
    "Italy Bracelet": ["All","Football","Gem","Flag","Chain"],
    "Lucky Draw": ["/lucky-draw"], 
}

# --- INITIAL DATA ---
initial_products = [
    {"id": 1, "name_kh": "#OP01 One Piece - Sakazuki","price": 7500, "image": "/static/images/op01.jpg", "categories": "LEGO Anime,Toy", "subcategory": "One Piece"},
    {"id": 2, "name_kh": "#OP02 One Piece - Portgas D Ace","price": 6500, "image": "/static/images/op02.jpg", "categories": "LEGO Anime,Toy", "subcategory": "One Piece"},
    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit","price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": "LEGO Ninjago,Toy", "subcategory": "Lego Ninjago,Season 1"},
    {"id": 3101, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់រលោង(ខ្មៅ)","price": 5000, "image": "/static/images/gymblack1.jpg", "categories": "Accessories,Hot Sale", "subcategory": "Gym Bracelet"},
    {"id": 20001, "name_kh": "71049 - 1 RED BULL","price": 24000, "image": "/static/images/lego71049-01.jpg", "categories": "LEGO,Toy", "subcategory": "Formula 1"},
]

# --- AUTO-INITIALIZE DATABASE ---
with app.app_context():
    db.create_all()
    if not Product.query.first():
        for p in initial_products:
            new_p = Product(
                id=p['id'], name_kh=p['name_kh'], price=p['price'], 
                image=p['image'], categories_str=p['categories'], 
                subcategory_str=p['subcategory']
            )
            db.session.add(new_p)
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('home.html', products=Product.query.all(), subcategories=[], cart=session.get('cart', []))

@app.route('/category/<cat>')
def category(cat):
    products = Product.query.filter(Product.categories_str.contains(cat)).all()
    return render_template('home.html', products=products, subcategories=subcategories_map.get(cat, []), current_category=cat, cart=session.get('cart', []))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    p_id = int(request.form.get('product_id'))
    p = Product.query.get(p_id)
    cart = session.get('cart', [])
    cart.append({"product": {"id": p.id, "name_kh": p.name_kh, "price": p.price, "image": p.image}, "quantity": 1})
    session['cart'] = cart
    return jsonify({"success": True, "cart_count": len(cart)})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_products'))
    return render_template('admin_login.html')

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=Product.query.all())

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        new_p = Product(
            name_kh=request.form['name_kh'], price=int(request.form['price']),
            image=request.form['image'], categories_str=request.form.get('categories', ''),
            subcategory_str=request.form.get('subcategory', '')
        )
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('add_product.html', subcategories_map=subcategories_map)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

