import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key'
app.debug = True

# ---------------- DATABASE ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- CONFIG ----------------
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"
BANNED_IPS = ['123.45.67.89', '45.119.135.70']

# ---------------- MODEL ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="")
    subcategory_str = db.Column(db.String(500), default="")
    stock = db.Column(db.Integer, default=1)

    @property
    def categories(self):
        return self.categories_str.split(',') if self.categories_str else []

    @property
    def subcategory(self):
        return self.subcategory_str.split(',') if self.subcategory_str else []

# ---------------- INITIAL DATA ----------------
initial_products = [
    {
        "id": 20012,
        "name_kh": "71049 - 12 GENERIC",
        "price": 24000,
        "image": "/static/images/lego71049-12.jpg",
        "categories": "LEGO,Toy",
        "subcategory": "Formula 1",
        "stock": 1
    }
]

# ---------------- SUBCATEGORIES ----------------
subcategories_map = {
    "Hot Sale": [],
    "LEGO Ninjago": ["Dragon Rising", "Building Set", "Season 1", "Season 2"],
    "LEGO Anime": ["One Piece", "Demon Slayer"],
    "Accessories": ["Bracelet"],
    "Keychain": ["Gun Keychains"],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece"],
    "Lucky Draw": ["/lucky-draw"]
}

# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()
    if not Product.query.first():
        for p in initial_products:
            db.session.add(Product(
                id=p.get('id'),
                name_kh=p['name_kh'],
                price=p['price'],
                image=p['image'],
                categories_str=p.get('categories', ''),
                subcategory_str=p.get('subcategory', ''),
                stock=p.get('stock', 1)
            ))
        db.session.commit()

# ---------------- SECURITY ----------------
def notify_telegram(ip, ua):
    try:
        msg = f"📦 New Visitor\nIP: {ip}\nDevice: {ua}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

@app.before_request
def protect():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip in BANNED_IPS:
        abort(403)
    if not session.get("notified"):
        notify_telegram(ip, request.headers.get("User-Agent"))
        session["notified"] = True

# ---------------- PUBLIC ROUTES ----------------
@app.route('/')
def home():
    return render_template('home.html', products=Product.query.all(), cart=session.get('cart', []))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    return render_template('product.html', product=Product.query.get_or_404(product_id))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    p = Product.query.get(request.form.get('product_id'))
    if not p:
        return jsonify(success=False)
    cart = session.get('cart', [])
    cart.append({"product": {"id": p.id, "name_kh": p.name_kh, "price": p.price, "image": p.image}, "quantity": 1})
    session['cart'] = cart
    return jsonify(success=True, cart_count=len(cart))

@app.route('/cart')
def cart_page():
    return render_template('cart.html', cart=session.get('cart', []))

# ---------------- ADMIN ----------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_products'))
    return render_template('admin_login.html')

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=Product.query.all())

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        db.session.add(Product(
            name_kh=request.form['name_kh'],
            price=int(request.form['price']),
            image=request.form['image'],
            categories_str=request.form.get('categories', ''),
            subcategory_str=request.form.get('subcategory', ''),
            stock=int(request.form.get('stock', 1))
        ))
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('add_product.html', subcategories_map=subcategories_map)

@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    p = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        p.name_kh = request.form['name_kh']
        p.price = int(request.form['price'])
        p.image = request.form['image']
        p.categories_str = request.form.get('categories', '')
        p.subcategory_str = request.form.get('subcategory', '')
        p.stock = int(request.form.get('stock', 1))
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('edit_product.html', product=p, subcategories_map=subcategories_map)

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('admin'):
        p = Product.query.get(product_id)
        if p:
            db.session.delete(p)
            db.session.commit()
    return redirect(url_for('admin_products'))

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))