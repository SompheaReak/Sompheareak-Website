from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Products data
products = [
    {"id": 1, "name_en": "M416 - Gold Plate", "name_kh": "M416 - ប្រាក់មាស", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 2, "name_en": "M416 - Default", "name_kh": "M416 - ពណ៌ដើម", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 3, "name_en": "AKM - Gold Plate", "name_kh": "AKM - ប្រាក់មាស", "price": 6000, "image": "/static/images/akm-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4, "name_en": "AKM - Default", "name_kh": "AKM - ពណ៌ដើម", "price": 6000, "image": "/static/images/akm-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 5, "name_en": "Scar L - Default", "name_kh": "Scar L - ពណ៌ដើម", "price": 6000, "image": "/static/images/scarl-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 6, "name_en": "Scar L - Gold", "name_kh": "Scar L - ពណ៌មាស", "price": 6000, "image": "/static/images/scarl-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 7, "name_en": "White Chalcedony", "name_kh": "ក្រវិលស", "price": 6000, "image": "/static/images/bc-01.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 8, "name_en": "Pink Opal", "name_kh": "ក្រវិលពណ៌ផ្កាឈូក", "price": 6000, "image": "/static/images/bc-02.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 9, "name_en": "Pink Crystal", "name_kh": "គ្រីស្ទាល់ពណ៌ផ្កាឈូក", "price": 5500, "image": "/static/images/bc-03.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 10, "name_en": "Strawberry Crystal", "name_kh": "គ្រីស្ទាល់ស្ករត្រសក់", "price": 9000, "image": "/static/images/bc-04.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"}
]

# Subcategories map
subcategories_map = {
    "Accessories": ["Gem Stone Bracelets", "Gym Bracelet"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": []
}

# In-memory cart
cart = []

# Home page
@app.route('/')
def home():
    language = request.args.get('lang', 'en')
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, subcategories=[])

# Category page
@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'en')
    filtered_products = [p for p in products if category_name in p['categories']]
    subs = subcategories_map.get(category_name, [])
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=category_name, subcategories=subs)

# Subcategory page
@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'en')
    filtered_products = [p for p in products if p.get('subcategory') == subcategory_name]
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=subcategory_name, subcategories=[])

# Product Detail page
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'en')
    product = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product, language=language)

# Cart page
@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'en')
    return render_template('cart.html', cart=cart, language=language)

# Add to cart
@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        cart.append({"product": product, "quantity": quantity})
    return jsonify({"success": True, "cart_count": len(cart)})

# Remove from cart
@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    if 0 <= index < len(cart):
        cart.pop(index)
    return redirect(url_for('cart_page'))

# Checkout page
@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'en')
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']

        # Send order to Telegram
        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n\n*Order Details:*\n"
        total = 0
        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
            message += f"- {p['name_en']} x {item['quantity']} = {subtotal}៛\n"
        message += f"\n*Total:* {total}៛"

        bot_token = '7981426501:AAE7CInWMNE2_sz5DaCMuAcKmH8yji1YBqk'
        chat_id = 1098161879
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("Telegram error:", response.text)

        cart.clear()
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language)

# Thank you page
@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'en')
    return render_template('thankyou.html', language=language)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
Help me replace all 