import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_default_key_123')

# --- DATABASE SETUP ---
# Render uses an ephemeral filesystem, so we ensure the DB path is absolute
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ADMIN CONFIG ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=1)
    discount = db.Column(db.Integer, default=0)

# --- INITIAL DATA ---
initial_products = [
    {"id": 1, "name_kh": "#OP01 One Piece - Sakazuki","price": 7500, "image": "https://raw.githubusercontent.com/YourUser/YourRepo/main/static/images/op01.jpg", "categories": "LEGO Anime,Toy", "subcategory": "One Piece"},
    {"id": 101, "name_kh": "NINJAGO S1 - DX Suit","price": 30000, "image": "https://raw.githubusercontent.com/YourUser/YourRepo/main/static/images/njoss1dx.jpg", "categories": "LEGO Ninjago,Toy", "subcategory": "Season 1"},
    {"id": 3101, "name_kh": "Gym Bracelet - Black","price": 5000, "image": "https://raw.githubusercontent.com/YourUser/YourRepo/main/static/images/gymblack1.jpg", "categories": "Accessories,Hot Sale", "subcategory": "Gym Bracelet"},
]

# --- DATABASE INITIALIZATION ---
def init_db():
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
            print("Database initialized successfully!")

# Initialize the DB before the first request
init_db()

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('home.html', products=Product.query.all(), cart=session.get('cart', []))

@app.route('/category/<cat>')
def category(cat):
    products = Product.query.filter(Product.categories_str.contains(cat)).all()
    return render_template('home.html', products=products, current_category=cat, cart=session.get('cart', []))

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

