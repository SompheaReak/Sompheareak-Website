import os
import time
import json
import re
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_secure_123')

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(200)) 
    stock = db.Column(db.Integer, default=999)

# --- UI COMPONENTS (No Blocks, Just Strings) ---

HEADER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LEGO Shop</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900 flex flex-col min-h-screen">
    <nav class="bg-white border-b p-4 shadow-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div class="flex items-center gap-2">
                <div class="bg-red-600 text-white font-bold p-1 text-lg">LEGO</div>
                <h1 class="text-xl font-bold text-gray-800">Market</h1>
            </div>
            <div class="space-x-4">
                <a href="/" class="text-gray-600 hover:text-red-600 font-medium">Home</a>
                <a href="/lego" class="text-gray-600 hover:text-red-600 font-medium">Collections</a>
                <a href="/admin/login" class="text-gray-600 hover:text-red-600 font-medium">Admin</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto p-4 w-full flex-grow">
"""

FOOTER_HTML = """
    </main>
    <footer class="bg-gray-800 text-white p-6 mt-8 text-center">
        <p>&copy; 2024 Lego Market. All rights reserved.</p>
    </footer>
</body>
</html>
"""

# --- PAGE TEMPLATES ---

HOME_PAGE = HEADER_HTML + """
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">All Products</h2>
        <span class="text-gray-500 text-sm">{{ products|length }} items found</span>
    </div>
    
    {% if products %}
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {% for p in products %}
        <div class="bg-white p-4 rounded-xl border hover:shadow-lg transition-shadow">
            <div class="h-40 w-full mb-3 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center relative">
                 <img src="{{ p.image }}" class="w-full h-full object-contain p-2" 
                      onerror="this.onerror=null; this.parentElement.innerHTML='<span class=\'text-gray-400\'>No Image</span>'">
                 {% if p.stock < 5 %}
                 <span class="absolute top-1 right-1 bg-orange-500 text-white text-[10px] px-2 py-0.5 rounded-full">Low Stock</span>
                 {% endif %}
            </div>
            <h3 class="font-bold text-gray-800 truncate" title="{{ p.name }}">{{ p.name }}</h3>
            <div class="flex justify-between items-end mt-2">
                <div>
                    <span class="text-xs text-gray-500 block">{{ p.category }}</span>
                    <p class="text-red-600 font-bold">៛{{ "{:,}".format(p.price) }}</p>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="text-center py-20 text-gray-500">
        <p class="text-xl">No products available yet.</p>
        <p class="text-sm mt-2">Sync the catalog to see items here.</p>
    </div>
    {% endif %}
""" + FOOTER_HTML

LEGO_PAGE = HEADER_HTML + """
    <h2 class="text-3xl font-extrabold mb-8 text-center text-gray-900 uppercase tracking-widest">Featured Themes</h2>

    {# Ninjago Section #}
    {% if data.ninjago_sorted %}
    <div class="mb-12 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-6 border-b pb-4">
            <div class="w-2 h-8 bg-red-600 rounded-full"></div>
            <h3 class="text-2xl font-bold text-gray-900">NINJAGO Universe</h3>
        </div>
        
        {% for season, items in data.ninjago_sorted %}
            <div class="mb-8 last:mb-0">
                <h4 class="text-lg font-bold mb-3 text-gray-700 bg-gray-50 inline-block px-3 py-1 rounded-lg">{{ season }}</h4>
                <div class="flex overflow-x-auto gap-4 pb-4 scrollbar-hide" style="scrollbar-width: thin;">
                    {% for p in items %}
                    <div class="min-w-[200px] w-[200px] bg-white p-3 rounded-xl border border-gray-200 hover:border-red-400 transition-colors flex-shrink-0">
                        <div class="h-32 bg-gray-50 rounded-lg mb-2 flex items-center justify-center">
                            <img src="{{ p.image }}" class="w-full h-full object-contain p-2" onerror="this.src='https://placehold.co/200?text=Lego'">
                        </div>
                        <h5 class="text-sm font-bold text-gray-900 truncate">{{ p.name }}</h5>
                        <p class="text-red-600 font-bold text-sm mt-1">៛{{ "{:,}".format(p.price) }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    </div>
    {% endif %}

    {# Other Sections Loop #}
    {% for key, items in [('One Piece', data.one_piece), ('Formula 1', data.f1), ('Military', data.military), ('Building Sets', data.sets)] %}
        {% if items %}
        <div class="mb-8">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-2 h-6 bg-blue-600 rounded-full"></div>
                <h3 class="text-xl font-bold">{{ key }}</h3>
            </div>
            <div class="flex overflow-x-auto gap-4 pb-4" style="scrollbar-width: thin;">
                {% for p in items %}
                <div class="min-w-[180px] w-[180px] bg-white p-3 rounded-xl border border-gray-200 flex-shrink-0">
                     <div class="h-28 bg-gray-50 rounded-lg mb-2 flex items-center justify-center">
                        <img src="{{ p.image }}" class="w-full h-full object-contain p-2" onerror="this.src='https://placehold.co/200?text={{ key }}'">
                     </div>
                     <h5 class="text-sm font-bold truncate">{{ p.name }}</h5>
                     <p class="text-blue-600 font-bold text-sm">៛{{ "{:,}".format(p.price) }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    {% endfor %}

""" + FOOTER_HTML

# --- LOGIC HELPERS ---

def get_data_fast():
    # Fetch all data immediately from DB
    return Product.query.all()

def natural_sort_key(s):
    # Sorts "Season 2" before "Season 10" correctly
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def organize_lego(products):
    data = {
        "ninjago": {},
        "one_piece": [],
        "f1": [],
        "sets": [],
        "military": [],
        "other": []
    }
    
    for p in products:
        cat_str = (p.category or "").lower()
        sub_str = (p.subcategory or "").lower()
        
        # Logic to bucket products
        if "ninjago" in cat_str or "ninjago" in sub_str:
            season = "General"
            if p.subcategory:
                parts = p.subcategory.split(',') if ',' in p.subcategory else [p.subcategory]
                for part in parts:
                    clean = part.strip()
                    # Detect season markers
                    if any(x in clean for x in ["Season", "Dragon Rising", "Pilot", "Movie"]):
                        season = clean
                        break
            if season not in data["ninjago"]: data["ninjago"][season] = []
            data["ninjago"][season].append(p)
        
        elif "one piece" in sub_str or "anime" in cat_str: data["one_piece"].append(p)
        elif "formula 1" in sub_str or "f1" in sub_str: data["f1"].append(p)
        elif "wwii" in sub_str or "military" in sub_str: data["military"].append(p)
        elif "set" in sub_str or "building" in sub_str: data["sets"].append(p)
        else: data["other"].append(p)

    # Sort Ninjago seasons
    sorted_seasons = sorted(data["ninjago"].keys(), key=natural_sort_key)
    data["ninjago_sorted"] = [(s, data["ninjago"][s]) for s in sorted_seasons]
    
    return data

# --- ROUTES ---

@app.route('/')
def home():
    try:
        products = get_data_fast()
        return render_template_string(HOME_PAGE, products=products)
    except Exception as e:
        app.logger.error(f"Home Error: {e}")
        return f"<h3>System Error</h3><p>{e}</p>", 500

@app.route('/lego')
def lego_world():
    try:
        products = get_data_fast()
        lego_data = organize_lego(products)
        return render_template_string(LEGO_PAGE, data=lego_data)
    except Exception as e:
        app.logger.error(f"Lego Page Error: {e}")
        return f"<h3>System Error</h3><p>{e}</p>", 500

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    try:
        data = request.json
        items = data.get('items', [])
        
        # Get existing IDs to decide update vs create
        existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
        
        count = 0
        for item in items:
            try:
                # Validation
                if 'id' not in item or 'price' not in item: continue
                
                # Cleaning inputs
                pid = int(item['id'])
                sub = item.get('subcategory')
                if isinstance(sub, list): sub = ",".join(sub)
                if sub is None: sub = ""
                
                name = item.get('name_kh') or item.get('name') or "Unknown"
                
                # Safe Category Extraction
                cats = item.get('categories')
                category = "General"
                if isinstance(cats, list) and cats:
                    category = cats[0]

                if pid not in existing_ids:
                    db.session.add(Product(
                        id=pid, name=name, price=int(item['price']),
                        image=item.get('image', ''), category=category, subcategory=sub
                    ))
                    count += 1
                else:
                    # Update existing (Using safe getter)
                    p = db.session.get(Product, pid)
                    if p:
                        p.name = name
                        p.price = int(item['price'])
                        p.subcategory = sub
            except Exception as row_err:
                print(f"Row Error: {row_err}")
                continue

        db.session.commit()
        return jsonify(success=True, added=count)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@app.route('/admin/login')
def admin_login():
    return "<h3>Admin Login</h3><p>Not implemented in this demo.</p>"

# --- STARTUP ---
if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully.")
            
            # Create a sample product if DB is empty so page isn't blank
            if not Product.query.first():
                print("Adding sample data...")
                db.session.add(Product(id=1, name="Demo Ninjago Set", price=25000, category="Toy", subcategory="Lego Ninjago,Season 1"))
                db.session.commit()
        except Exception as e:
            print(f"Database Error: {e}")

    app.run(host="0.0.0.0", port=5000, debug=True)


