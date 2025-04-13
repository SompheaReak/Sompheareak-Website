from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy products data
products = [
    {
        "id": 1,
        "name_en": "M416 - Gold Plate",
        "name_kh": "M416 - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/m416-gold.jpg",
        "categories": ["Hot Sale", "Toy", "Keychain"]
    },
    {
        "id": 2,
        "name_en": "M416 - Default",
        "name_kh": "M416 - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/m416-default.jpg",
        "categories": ["Toy", "Keychain"]
    },
    {
        "id": 3,
        "name_en": "AKM - Gold Plate",
        "name_kh": "AKM - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/akm-gold.jpg",
        "categories": ["Hot Sale", "Toy", "Keychain"]
    },
    {
        "id": 4,
        "name_en": "AKM - Default",
        "name_kh": "AKM - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/akm-default.jpg",
        "categories": ["Toy", "Keychain"]
    }
]

# Simple in-memory orders (not real database yet)
orders = []

@app.route('/')
def home():
    language = request.args.get('lang', 'en')
    return render_template('home.html', products=products, language=language)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'en')
    product = next((item for item in products if item["id"] == product_id), None)
    return render_template('product.html', product=product, language=language)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        orders.append({"name": name, "phone": phone, "address": address})
        return redirect(url_for('home'))
    return render_template('checkout.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)