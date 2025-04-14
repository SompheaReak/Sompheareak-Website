from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests  # important for sending message to Telegram

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy products data
products = [
    {
        "id": 1,
        "name_en": "M416 - Gold Plate",
        "name_kh": "M416 - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/m416-gold.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 2,
        "name_en": "M416 - Default",
        "name_kh": "M416 - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/m416-default.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 3,
        "name_en": "AKM - Gold Plate",
        "name_kh": "AKM - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/akm-gold.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 4,
        "name_en": "AKM - Default",
        "name_kh": "AKM - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/akm-default.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 5,
        "name_en": "Scar L - Default",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/scarl-default.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 6,
        "name_en": "Scar L - Gold",
        "name_kh": "Scar L - ពណ៌ដើម ",
        "price": 6000,
        "image": "/static/images/scarl-gold.jpg",
        "categories": ["Keychain"]
    }
]

# In-memory cart
cart = []

@app.route('/')
def home():
    language = request.args.get('lang', 'en')
    return render_template('home.html', products=products, language=language, cart=cart)

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'en')
    filtered_products = [product for product in products if category_name in product['categories']]
    return render_template('home.html', products=filtered_products, language=language, cart=cart)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'en')
    product = next((item for item in products if item["id"] == product_id), None)
    return render_template('product.html', product=product, language=language)

@app.route('/cart', methods=["GET"])
def cart_page():
    return render_template('cart.html', cart=cart)

@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((item for item in products if item["id"] == product_id), None)
    if product:
        cart.append({
            "product": product,
            "quantity": quantity
        })
    return jsonify({"success": True, "cart_count": len(cart)})

@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    if 0 <= index < len(cart):
        cart.pop(index)
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']

        # Prepare Telegram message
        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n"
        message += f"*Phone:* {phone}\n"
        message += f"*Address:* {address}\n\n"
        message += "*Order Details:*\n"

        total = 0
        for item in cart:
            product_name = item['product']['name_en']
            quantity = item['quantity']
            price = item['product']['price']
            subtotal = price * quantity
            total += subtotal
            message += f"- {product_name} x {quantity} = {subtotal}៛\n"

        message += f"\n*Total:* {total}៛"

        # Send message to Telegram
        bot_token = '7981426501:AAE7CInWMNE2_sz5DaCMuAcKmH8yji1YBqk'
        chat_id = 1098161879
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("Failed to send Telegram message:", response.text)

        cart.clear()  # Clear cart after sending

        # Redirect to Thank You Page
        return redirect(url_for('thank_you'))

    return render_template('checkout.html')

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)