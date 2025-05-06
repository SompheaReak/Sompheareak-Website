# Reconstruct and output the full fixed code for the Flask app
fixed_code = """
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort

# Admin login credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.debug = True

# Sample products
products = [
    {"id": 1, "name_kh": "M416 - ប្រាក់មាស", "name_en": "M416 - Gold Plate", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 2, "name_kh": "M416 - ពណ៌ដើម", "name_en": "M416 - Default", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
]

subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["Season 1", "Season 2", "Season 3", "Season 4"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII"]
}

banned_ips = ['123.45.67.89', '111.222.333.444']

def notify_telegram(ip, user_agent):
    bot_token = "your_bot_token_here"
    chat_id = "your_chat_id_here"
    message = f"🌐 *New Visitor Alert!*\\n\\n*IP:* `{ip}`\\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

@app.before_request
def block_banned_ips():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    if ip in banned_ips:
        abort(403)
    notify_telegram(ip, user_agent)

@app.route('/')
def home():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, current_subcategory=None, subcategories=[])

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [p for p in products if category_name in p.get('categories', [])]
    subs = subcategories_map.get(category_name, [])
    cart = session.get('cart', [])
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=category_name, current_subcategory=None, subcategories=subs)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'kh')
    product = next((p for p in products if p['id'] == product_id), None)
    cart = session.get('cart', [])
    return render_template('product.html', product=product, language=language, cart=cart)

@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart.append({"product": product, "quantity": quantity})
        session['cart'] = cart
    return jsonify({"success": True, "cart_count": len(session.get('cart', []))})

@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart, language=language)

@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']
        ip = request.remote_addr

        delivery_text = ""
        delivery_fee = 0
        if delivery_method == "door":
            delivery_text = "ទំនិញដល់ដៃទូទាត់ប្រាក់"
            delivery_fee = 7000
        elif delivery_method == "vet":
            delivery_text = "វីរៈប៊ុនថាំ (VET)"
            delivery_fee = 5000
        elif delivery_method == "jnt":
            delivery_text = "J&T"
            delivery_fee = 7000

        message = f"🛒 *New Order Received!*\\n\\n*Name:* {name}\\n*Phone:* {phone}\\n*Address:* {address}\\n*IP:* {ip}\\n*Delivery:* {delivery_text} ({delivery_fee}៛)\\n\\n*Order Details:*\\n"
        total = 0
        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
            message += f"- {p['name_en']} x {item['quantity']} = {subtotal}៛\\n"
        total += delivery_fee
        message += f"\\n*Total with Delivery:* {total}៛"

        bot_token = "your_bot_token_here"
        chat_id = "your_chat_id_here"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        session['cart'] = []
        return redirect(url_for('thank_you'))
    return render_template('checkout.html', language=language, cart=cart)

@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""

fixed_code[:4000]  # Truncate to 4000 characters to display here
