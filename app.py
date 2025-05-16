import os 
import requests
# Admin login credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
app = Flask(__name__)
import datetime
def notify_telegram(ip, user_agent):
    bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
    chat_id = "-1002660809745"    
    message = f"🌐 *New Visitor Alert!*\n\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    print("==> Visitor Bot Message Sent")
    print("BOT TOKEN:", bot_token)
    print("CHAT ID:", chat_id)
    print("MESSAGE:", message)
    print("RESPONSE:", response.text)
# List of IPs you want to ban
banned_ips = ['123.45.67.89']  # Replace with real IPs
@app.before_request
def block_banned_ips():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')

    # Block banned IPs
    if ip in banned_ips:
        abort(403)

    # Notify only once per session
    if not session.get('visited'):
        notify_telegram(ip, user_agent)
        session['visited'] = True

# Products data
products = [

]
# --- Subcategories Map ---
subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["New","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, current_subcategory=None, subcategories=[])

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    subs = subcategories_map.get(category_name, [])
    
    # If subcategories exist, redirect to first one
    if subs:
        return redirect(url_for('subcategory', subcategory_name=subs[0]))

    # If no subcategories, show all products in that category
    filtered_products = [
        p for p in products
        if category_name in p.get('categories', [])
    ]
    cart = session.get('cart', [])
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=category_name,
        current_subcategory=None,
        subcategories=[]
    )
@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [
        p for p in products
        if subcategory_name in p.get('subcategory', [])
    ]
    cart = session.get('cart', [])

    # Find main category
    main_category = None
    for category, subs in subcategories_map.items():
        if subcategory_name in subs:
            main_category = category
            break

    subs = subcategories_map.get(main_category, []) if main_category else []

    # Correct indentation here!
    if request.args.get('ajax') == 'true':
        return render_template('product_cards.html', products=filtered_products, language=language)

    # Full page render
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=main_category,
        current_subcategory=subcategory_name,
        subcategories=subs
    )
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'kh')
    product = next((p for p in products if p['id'] == product_id), None)
    cart = session.get('cart', [])
    return render_template('product.html', product=product, language=language, cart=cart)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Try again.'

    return render_template('admin_login.html', error=error)
@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart, language=language)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))

    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False})

    cart = session.get('cart', [])
    cart.append({"product": product, "quantity": quantity})
    session['cart'] = cart

    return jsonify({"success": True, "cart_count": len(cart)})
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
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        # Replace with your actual bot token and chat ID
        bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
        chat_id = "-1002660809745"

        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']

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

        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n"
        message += f"*Delivery:* {delivery_text} ({delivery_fee}៛)\n"
        message += f"*IP:* {ip}\n\n*Order Details:*\n"

        total = 0
        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
        name = p.get('name_en', p.get('name_kh', 'Unknown Product'))
        message += f"{name} x {item['quantity']} = {subtotal}\n"
        total += delivery_fee
        message += f"\n*Total with Delivery:* {total}៛"

        # Send to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        print("Telegram response:", response.text)

        session['cart'] = []
        return redirect(url_for('thank_you'))

    # If not POST, render checkout page
    return render_template('checkout.html', language=language, cart=cart)
@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403
@app.route('/admin/products')
def admin_products():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=products)


@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_id = max([p['id'] for p in products]) + 1 if products else 1
        new_product = {
            'id': new_id,
            'name_kh': request.form['name_kh'],
            'name_en': request.form['name_en'],
            'price': int(request.form['price']),
            'image': request.form['image'],
            'categories': [request.form['category']],
            'subcategory': request.form['subcategory']
        }
        products.append(new_product)
        return redirect(url_for('admin_products'))

    return render_template('add_product.html')


@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        product['name_kh'] = request.form['name_kh']
        product['name_en'] = request.form['name_en']
        product['price'] = int(request.form['price'])
        product['image'] = request.form['image']
        return redirect(url_for('admin_products'))

    return render_template('edit_product.html', product=product)


@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('admin_products'))


@app.route('/admin/ban-ip', methods=['GET', 'POST'])
def ban_ip():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    message = ""
    if request.method == 'POST':
        ip = request.form.get('ip')
    if ip and ip not in banned_ips:
        banned_ips.append(ip)
        message = f"IP {ip} has been banned."
    return render_template('ban_ip.html', banned_ips=banned_ips, message=message)


@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)