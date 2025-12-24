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
    # --- Charm
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Italy Bracelet", "Charm"], "subcategory": "Charms"},
   
    # --- F1 LOGOS (1100 - 1195) ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},

    # --- Pink F1 (1200 - 1295) ---
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1291, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1292, "name_kh": "Pink F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1293, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1294, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1295, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},

    {"id": 1201, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-f1-202.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1202, "name_kh": "Pink F1 - Ferrari", "price": 3000, "image": "/static/images/charm-f1-203.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1203, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-204.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1204, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-205.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink F1"},

    # --- CAR LOGOS (1001 - 1015) ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1006, "name_kh": "Car Charm 06", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1007, "name_kh": "Car Charm 07", "price": 3000, "image": "/static/images/cc07.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"}, 
    {"id": 1008, "name_kh": "Car Charm 08", "price": 3000, "image": "/static/images/cc08.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1009, "name_kh": "Car Charm 09", "price": 3000, "image": "/static/images/cc09.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1010, "name_kh": "Car Charm 10", "price": 3000, "image": "/static/images/cc10.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1011, "name_kh": "Car Charm 11", "price": 3000, "image": "/static/images/cc11.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1012, "name_kh": "Car Charm 12", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1013, "name_kh": "Car Charm 13", "price": 3000, "image": "/static/images/cc13.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1014, "name_kh": "Car Charm 14", "price": 3000, "image": "/static/images/cc14.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1015, "name_kh": "Car Charm 15", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},

    # --- FLAGS (2001 - 2019) ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2003, "name_kh": "Flag Charm 03", "price": 3000, "image": "/static/images/cf03.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2004, "name_kh": "Flag Charm 04", "price": 3000, "image": "/static/images/cf04.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2005, "name_kh": "Flag Charm 05", "price": 3000, "image": "/static/images/cf05.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2006, "name_kh": "Flag Charm 06", "price": 3000, "image": "/static/images/cf06.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2007, "name_kh": "Flag Charm 07", "price": 3000, "image": "/static/images/cf07.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2008, "name_kh": "Flag Charm 08", "price": 3000, "image": "/static/images/cf08.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2009, "name_kh": "Flag Charm 09", "price": 3000, "image": "/static/images/cf09.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2010, "name_kh": "Flag Charm 10", "price": 3000, "image": "/static/images/cf10.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2011, "name_kh": "Flag Charm 11", "price": 3000, "image": "/static/images/cf11.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2012, "name_kh": "Flag Charm 12", "price": 3000, "image": "/static/images/cf12.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2013, "name_kh": "Flag Charm 13", "price": 3000, "image": "/static/images/cf13.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2014, "name_kh": "Flag Charm 14", "price": 3000, "image": "/static/images/cf14.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2015, "name_kh": "Flag Charm 15", "price": 3000, "image": "/static/images/cf15.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2016, "name_kh": "Flag Charm 16", "price": 3000, "image": "/static/images/cf16.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2017, "name_kh": "Flag Charm 17", "price": 3000, "image": "/static/images/cf17.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["Flag","Football"]},
    {"id": 2018, "name_kh": "Flag Charm 18", "price": 3000, "image": "/static/images/cf18.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},
    {"id": 2019, "name_kh": "Flag Charm 19", "price": 3000, "image": "/static/images/cf19.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": ["All","Football"]},

    # --- GEMSTONES (3001 - 3024) ---
    {"id": 3001, "name_kh": "Gemstone Charm 01", "price": 3500, "image": "/static/images/cg01.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3002, "name_kh": "Gemstone Charm 02", "price": 3500, "image": "/static/images/cg02.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3003, "name_kh": "Gemstone Charm 03", "price": 3500, "image": "/static/images/cg03.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3004, "name_kh": "Gemstone Charm 04", "price": 3500, "image": "/static/images/cg04.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3005, "name_kh": "Gemstone Charm 05", "price": 3500, "image": "/static/images/cg05.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3006, "name_kh": "Gemstone Charm 06", "price": 3500, "image": "/static/images/cg06.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3007, "name_kh": "Gemstone Charm 07", "price": 3500, "image": "/static/images/cg07.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3008, "name_kh": "Gemstone Charm 08", "price": 3500, "image": "/static/images/cg08.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3009, "name_kh": "Gemstone Charm 09", "price": 3500, "image": "/static/images/cg09.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3010, "name_kh": "Gemstone Charm 10", "price": 3500, "image": "/static/images/cg10.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3011, "name_kh": "Gemstone Charm 11", "price": 3500, "image": "/static/images/cg11.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3012, "name_kh": "Gemstone Charm 12", "price": 3500, "image": "/static/images/cg12.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3013, "name_kh": "Gemstone Charm 13", "price": 3500, "image": "/static/images/cg13.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3014, "name_kh": "Gemstone Charm 14", "price": 3500, "image": "/static/images/cg14.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3015, "name_kh": "Gemstone Charm 15", "price": 3500, "image": "/static/images/cg15.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3016, "name_kh": "Gemstone Charm 16", "price": 3500, "image": "/static/images/cg16.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3017, "name_kh": "Gemstone Charm 17", "price": 3500, "image": "/static/images/cg17.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3018, "name_kh": "Gemstone Charm 18", "price": 3500, "image": "/static/images/cg18.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3019, "name_kh": "Gemstone Charm 19", "price": 3500, "image": "/static/images/cg19.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3020, "name_kh": "Gemstone Charm 20", "price": 3500, "image": "/static/images/cg20.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3021, "name_kh": "Gemstone Charm 21", "price": 5000, "image": "/static/images/cg21.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["Car Logo"]},
    {"id": 3022, "name_kh": "Gemstone Charm 22", "price": 5000, "image": "/static/images/cg22.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3023, "name_kh": "Gemstone Charm 23", "price": 5000, "image": "/static/images/cg23.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},
    {"id": 3024, "name_kh": "Gemstone Charm 24", "price": 5000, "image": "/static/images/cg24.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": ["All","Football"]},

    # --- Chain (4001 - 4016) ---
    {"id": 4001, "name_kh": "Chain Charm 01", "price": 3000, "image": "/static/images/charm-chain-01.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4002, "name_kh": "Chain Charm 02", "price": 3000, "image": "/static/images/charm-chain-02.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4003, "name_kh": "Chain Charm 03", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4004, "name_kh": "Chain Charm 04", "price": 3000, "image": "/static/images/charm-chain-04.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4005, "name_kh": "Chain Charm 05", "price": 3000, "image": "/static/images/charm-chain-05.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4006, "name_kh": "Chain Charm 06", "price": 3000, "image": "/static/images/charm-chain-06.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4007, "name_kh": "Chain Charm 07", "price": 3000, "image": "/static/images/charm-chain-07.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4008, "name_kh": "Chain Charm 08", "price": 3000, "image": "/static/images/charm-chain-08.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4009, "name_kh": "Chain Charm 09", "price": 3000, "image": "/static/images/charm-chain-09.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4010, "name_kh": "Chain Charm 10", "price": 3000, "image": "/static/images/charm-chain-10.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4011, "name_kh": "Chain Charm 11", "price": 3000, "image": "/static/images/charm-chain-11.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4012, "name_kh": "Chain Charm 12", "price": 3000, "image": "/static/images/charm-chain-12.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4013, "name_kh": "Chain Charm 13", "price": 3000, "image": "/static/images/charm-chain-13.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4014, "name_kh": "Chain Charm 14", "price": 3000, "image": "/static/images/charm-chain-14.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},
    {"id": 4015, "name_kh": "Chain Charm 15", "price": 3000, "image": "/static/images/charm-chain-15.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["All","Football"]},
    {"id": 4016, "name_kh": "Chain Charm 16", "price": 3000, "image": "/static/images/charm-chain-16.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": ["Flag","Football"]},

    # --- Football Club (5001 - 5015) ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5002, "name_kh": "Real Madrid", "price": 3000, "image": "/static/images/charm-footballclub-02.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5003, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-03.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5004, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-04.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5005, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-05.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5006, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-06.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5007, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-07.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5008, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-08.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5009, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-09.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5010, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-10.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5011, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-11.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5012, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-12.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5013, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-13.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5014, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-14.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},
    {"id": 5015, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-15.jpg", "categories": ["Italy Bracelet", "Football Club Logo"]},

    # --- Black Lover (6001 - 6007) ---
    {"id": 6001, "name_kh": "Black Charm 01", "price": 3000, "image": "/static/images/cb01.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["All","Football"]},
    {"id": 6002, "name_kh": "Black Charm 02", "price": 3000, "image": "/static/images/cb02.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["Flag","Football"]},
    {"id": 6003, "name_kh": "Black Charm 03", "price": 3000, "image": "/static/images/cb03.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["All","Football"]},
    {"id": 6004, "name_kh": "Black Charm 04", "price": 3000, "image": "/static/images/cb04.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["Flag","Football"]},
    {"id": 6005, "name_kh": "Black Charm 05", "price": 3000, "image": "/static/images/cb05.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["Flag","Football"]},
    {"id": 6006, "name_kh": "Black Charm 06", "price": 3000, "image": "/static/images/cb06.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["Flag","Football"]},
    {"id": 6007, "name_kh": "Black Charm 07", "price": 3000, "image": "/static/images/cb07.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": ["Flag","Football"]},

    # --- Dog&Cat Lover (7001 - 7007) ---
    {"id": 7001, "name_kh": "Cat&Dog Charm 01", "price": 3000, "image": "/static/images/charm-animal-01.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["All","Football"]},
    {"id": 7002, "name_kh": "Cat&Dog Charm 02", "price": 3000, "image": "/static/images/charm-animal-02.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["Flag","Football"]},
    {"id": 7003, "name_kh": "Cat&Dog Charm 03", "price": 3000, "image": "/static/images/charm-animal-03.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["All","Football"]},
    {"id": 7004, "name_kh": "Cat&Dog Charm 04", "price": 3000, "image": "/static/images/charm-animal-04.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["Flag","Football"]},
    {"id": 7005, "name_kh": "Cat&Dog Charm 05", "price": 3000, "image": "/static/images/charm-animal-05.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["Flag","Football"]},
    {"id": 7006, "name_kh": "Cat&Dog Charm 06", "price": 3000, "image": "/static/images/charm-animal-06.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["Flag","Football"]},
    {"id": 7007, "name_kh": "Cat&Dog Charm 07", "price": 3000, "image": "/static/images/charm-animal-07.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": ["Flag","Football"]},

    # --- Blue Sea Lover (7011-7025) ---
    {"id": 7011, "name_kh": "Blue Sea Lover 01", "price": 3000, "image": "/static/images/charm-bluesealover-01.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["All","Football"]},
    {"id": 7012, "name_kh": "Blue Sea Lover 02", "price": 3000, "image": "/static/images/charm-bluesealover-02.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7013, "name_kh": "Blue Sea Lover 03", "price": 3000, "image": "/static/images/charm-bluesealover-03.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["All","Football"]},
    {"id": 7014, "name_kh": "Blue Sea Lover 04", "price": 3000, "image": "/static/images/charm-bluesealover-04.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7015, "name_kh": "Blue Sea Lover 05", "price": 3000, "image": "/static/images/charm-bluesealover-05.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7016, "name_kh": "Blue Sea Lover 06", "price": 3000, "image": "/static/images/charm-bluesealover-06.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7017, "name_kh": "Blue Sea Lover 07", "price": 3000, "image": "/static/images/charm-bluesealover-07.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7018, "name_kh": "Blue Sea Lover 08", "price": 3000, "image": "/static/images/charm-bluesealover-08.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["All","Football"]},
    {"id": 7019, "name_kh": "Blue Sea Lover 09", "price": 3000, "image": "/static/images/charm-bluesealover-09.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7020, "name_kh": "Blue Sea Lover 10", "price": 3000, "image": "/static/images/charm-bluesealover-10.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["All","Football"]},
    {"id": 7021, "name_kh": "Blue Sea Lover 11", "price": 3000, "image": "/static/images/charm-bluesealover-11.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7022, "name_kh": "Blue Sea Lover 12", "price": 3000, "image": "/static/images/charm-bluesealover-12.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7023, "name_kh": "Blue Sea Lover 13", "price": 3000, "image": "/static/images/charm-bluesealover-13.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7024, "name_kh": "Blue Sea Lover 14", "price": 3000, "image": "/static/images/charm-bluesealover-14.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},
    {"id": 7025, "name_kh": "Blue Sea Lover 15", "price": 3000, "image": "/static/images/charm-bluesealover-15.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": ["Flag","Football"]},

    # --- Pink Lover (8001 - 8009) ---
    {"id": 8001, "name_kh": "Pink Charm 01", "price": 3000, "image": "/static/images/cp01.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["All","Football"]},
    {"id": 8002, "name_kh": "Pink Charm 02", "price": 3000, "image": "/static/images/cp02.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8003, "name_kh": "Pink Charm 03", "price": 3000, "image": "/static/images/cp03.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["All","Football"]},
    {"id": 8004, "name_kh": "Pink Charm 04", "price": 3000, "image": "/static/images/cp04.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8005, "name_kh": "Pink Charm 05", "price": 3000, "image": "/static/images/cp05.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8006, "name_kh": "Pink Charm 06", "price": 3000, "image": "/static/images/cp06.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8007, "name_kh": "Pink Charm 07", "price": 3000, "image": "/static/images/cp07.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8008, "name_kh": "Pink Charm 08", "price": 3000, "image": "/static/images/cp08.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
    {"id": 8009, "name_kh": "Pink Charm 09", "price": 3000, "image": "/static/images/cp09.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": ["Flag","Football"]},
 
    # --- PINK LETTERS (9001 - 9026) ---
    {"id": 9001, "name_kh": "Pink Letter Charm A", "price": 1200, "image": "/static/images/ap.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9002, "name_kh": "Pink Letter Charm B", "price": 1200, "image": "/static/images/bp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9003, "name_kh": "Pink Letter Charm C", "price": 1200, "image": "/static/images/cp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9004, "name_kh": "Pink Letter Charm D", "price": 1200, "image": "/static/images/dp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9005, "name_kh": "Pink Letter Charm E", "price": 1200, "image": "/static/images/ep.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9006, "name_kh": "Pink Letter Charm F", "price": 1200, "image": "/static/images/fp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9007, "name_kh": "Pink Letter Charm G", "price": 1200, "image": "/static/images/gp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9008, "name_kh": "Pink Letter Charm H", "price": 1200, "image": "/static/images/hp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9009, "name_kh": "Pink Letter Charm I", "price": 1200, "image": "/static/images/ip.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9010, "name_kh": "Pink Letter Charm J", "price": 1200, "image": "/static/images/jp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9011, "name_kh": "Pink Letter Charm K", "price": 1200, "image": "/static/images/kp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9012, "name_kh": "Pink Letter Charm L", "price": 1200, "image": "/static/images/lp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9013, "name_kh": "Pink Letter Charm M", "price": 1200, "image": "/static/images/mp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9014, "name_kh": "Pink Letter Charm N", "price": 1200, "image": "/static/images/np.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9015, "name_kh": "Pink Letter Charm O", "price": 1200, "image": "/static/images/op.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9016, "name_kh": "Pink Letter Charm P", "price": 1200, "image": "/static/images/pp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9017, "name_kh": "Pink Letter Charm Q", "price": 1200, "image": "/static/images/qp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9018, "name_kh": "Pink Letter Charm R", "price": 1200, "image": "/static/images/rp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9019, "name_kh": "Pink Letter Charm S", "price": 1200, "image": "/static/images/sp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9020, "name_kh": "Pink Letter Charm T", "price": 1200, "image": "/static/images/tp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9021, "name_kh": "Pink Letter Charm U", "price": 1200, "image": "/static/images/up.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9022, "name_kh": "Pink Letter Charm V", "price": 1200, "image": "/static/images/vp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9023, "name_kh": "Pink Letter Charm W", "price": 1200, "image": "/static/images/wp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9024, "name_kh": "Pink Letter Charm X", "price": 1200, "image": "/static/images/xp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["Flag","Football"]},
    {"id": 9025, "name_kh": "Pink Letter Charm Y", "price": 1200, "image": "/static/images/yp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},
    {"id": 9026, "name_kh": "Pink Letter Charm Z", "price": 1200, "image": "/static/images/zp.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": ["All","Football"]},

    # --- SILVER/GOLD LETTERS (2201 - 2226) (Renumbered from 1101 to prevent conflict with F1) ---
    {"id": 2201, "name_kh": "Letter Charm A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2202, "name_kh": "Letter Charm B", "price": 1200, "image": "/static/images/b.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2203, "name_kh": "Letter Charm C", "price": 1200, "image": "/static/images/c.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2204, "name_kh": "Letter Charm D", "price": 1200, "image": "/static/images/d.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2205, "name_kh": "Letter Charm E", "price": 1200, "image": "/static/images/e.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2206, "name_kh": "Letter Charm F", "price": 1200, "image": "/static/images/f.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2207, "name_kh": "Letter Charm G", "price": 1200, "image": "/static/images/g.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2208, "name_kh": "Letter Charm H", "price": 1200, "image": "/static/images/h.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2209, "name_kh": "Letter Charm I", "price": 1200, "image": "/static/images/i.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2210, "name_kh": "Letter Charm J", "price": 1200, "image": "/static/images/j.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2211, "name_kh": "Letter Charm K", "price": 1200, "image": "/static/images/k.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2212, "name_kh": "Letter Charm L", "price": 1200, "image": "/static/images/l.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2213, "name_kh": "Letter Charm M", "price": 1200, "image": "/static/images/m.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2214, "name_kh": "Letter Charm N", "price": 1200, "image": "/static/images/n.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2215, "name_kh": "Letter Charm O", "price": 1200, "image": "/static/images/o.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2216, "name_kh": "Letter Charm P", "price": 1200, "image": "/static/images/p.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2217, "name_kh": "Letter Charm Q", "price": 1200, "image": "/static/images/q.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2218, "name_kh": "Letter Charm R", "price": 1200, "image": "/static/images/r.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2219, "name_kh": "Letter Charm S", "price": 1200, "image": "/static/images/s.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2220, "name_kh": "Letter Charm T", "price": 1200, "image": "/static/images/t.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2221, "name_kh": "Letter Charm U", "price": 1200, "image": "/static/images/u.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2222, "name_kh": "Letter Charm V", "price": 1200, "image": "/static/images/v.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2223, "name_kh": "Letter Charm W", "price": 1200, "image": "/static/images/w.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2224, "name_kh": "Letter Charm X", "price": 1200, "image": "/static/images/x.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["Flag","Football"]},
    {"id": 2225, "name_kh": "Letter Charm Y", "price": 1200, "image": "/static/images/y.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},
    {"id": 2226, "name_kh": "Letter Charm Z", "price": 1200, "image": "/static/images/z.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": ["All","Football"]},

    # --- STEAV (2301 - 2313) (Renumbered from 1201 to prevent conflict with Pink F1) ---
    {"id": 2301, "name_kh": "Steav Charm 01", "price": 3000, "image": "/static/images/cm01.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["Car Logo"]},
    {"id": 2302, "name_kh": "Steav Charm 02", "price": 3000, "image": "/static/images/cm02.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2303, "name_kh": "Steav Charm 03", "price": 3000, "image": "/static/images/cm03.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2304, "name_kh": "Steav Charm 04", "price": 3000, "image": "/static/images/cm04.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2305, "name_kh": "Steav Charm 05", "price": 3000, "image": "/static/images/cm05.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2306, "name_kh": "Steav Charm 06", "price": 3000, "image": "/static/images/cm06.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["Car Logo"]},
    {"id": 2307, "name_kh": "Steav Charm 07", "price": 3000, "image": "/static/images/cm07.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["Car Logo"]},
    {"id": 2308, "name_kh": "Steav Charm 08", "price": 3000, "image": "/static/images/cm08.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2309, "name_kh": "Steav Charm 09", "price": 3000, "image": "/static/images/cm09.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2310, "name_kh": "Steav Charm 10", "price": 3000, "image": "/static/images/cm10.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2311, "name_kh": "Steav Charm 11", "price": 3000, "image": "/static/images/cm11.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2312, "name_kh": "Steav Charm 12", "price": 3000, "image": "/static/images/cm12.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    {"id": 2313, "name_kh": "Steav Charm 13", "price": 4000, "image": "/static/images/cm13.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": ["All","Football"]},
    
    # --- Cartoon (1301) ---
    {"id": 1301, "name_kh": "Cartoon Charm", "price": 3000, "image": "/static/images/ct01.jpg", "categories": ["Italy Bracelet", "Cartoon"]},

    # --- CUTIE (1401 - 1416) ---
    {"id": 1401, "name_kh": "Cutie Charm 01", "price": 3000, "image": "/static/images/cw01.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["Car Logo"]},
    {"id": 1402, "name_kh": "Cutie Charm 02", "price": 3000, "image": "/static/images/cw02.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1403, "name_kh": "Cutie Charm 03", "price": 3000, "image": "/static/images/cw03.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1404, "name_kh": "Cutie Charm 04", "price": 3000, "image": "/static/images/cw04.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1405, "name_kh": "Cutie Charm 05", "price": 3000, "image": "/static/images/cw05.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1406, "name_kh": "Cutie Charm 06", "price": 4000, "image": "/static/images/cw06.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["Car Logo"]},
    {"id": 1407, "name_kh": "Cutie Charm 07", "price": 4000, "image": "/static/images/cw07.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["Car Logo"]},
    {"id": 1408, "name_kh": "Cutie Charm 08", "price": 4000, "image": "/static/images/cw08.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1409, "name_kh": "Cutie Charm 09", "price": 4000, "image": "/static/images/cw09.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1410, "name_kh": "Cutie Charm 10", "price": 4000, "image": "/static/images/cw10.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]}, 
    {"id": 1411, "name_kh": "Cutie Charm 11", "price": 4000, "image": "/static/images/cw11.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1412, "name_kh": "Cutie Charm 12", "price": 4000, "image": "/static/images/cw12.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1413, "name_kh": "Cutie Charm 13", "price": 4000, "image": "/static/images/cw13.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1414, "name_kh": "Cutie Charm 14", "price": 4000, "image": "/static/images/cw14.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1415, "name_kh": "Cutie Charm 15", "price": 4000, "image": "/static/images/cw15.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},
    {"id": 1416, "name_kh": "Cutie Charm 16", "price": 4000, "image": "/static/images/cw16.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": ["All","Football"]},

    # --- Bubble (1501 - 1512) ---
    {"id": 1501, "name_kh": " Charm 01", "price": 3000, "image": "/static/images/charm-bubble-01.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["Car Logo"]},
    {"id": 1502, "name_kh": " Charm 02", "price": 3000, "image": "/static/images/charm-bubble-02.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1503, "name_kh": " Charm 03", "price": 3000, "image": "/static/images/charm-bubble-03.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1504, "name_kh": " Charm 04", "price": 3000, "image": "/static/images/charm-bubble-04.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1505, "name_kh": " Charm 05", "price": 3000, "image": "/static/images/charm-bubble-05.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1506, "name_kh": " Charm 06", "price": 3000, "image": "/static/images/charm-bubble-06.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["Car Logo"]},
    {"id": 1507, "name_kh": " Charm 07", "price": 3000, "image": "/static/images/charm-bubble-07.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["Car Logo"]},
    {"id": 1508, "name_kh": " Charm 08", "price": 3000, "image": "/static/images/charm-bubble-08.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1509, "name_kh": " Charm 09", "price": 3000, "image": "/static/images/charm-bubble-09.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1510, "name_kh": " Charm 10", "price": 3000, "image": "/static/images/charm-bubble-10.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1511, "name_kh": " Charm 11", "price": 3000, "image": "/static/images/charm-bubble-11.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},
    {"id": 1512, "name_kh": " Charm 12", "price": 3000, "image": "/static/images/charm-bubble-12.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": ["All","Football"]},

    # --- Cute Cat (1601 - 1612) ---
    {"id": 1601, "name_kh": " Charm 01", "price": 3000, "image": "/static/images/charm-cutecat-01.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["Car Logo"]},
    {"id": 1602, "name_kh": " Charm 02", "price": 3000, "image": "/static/images/charm-cutecat-02.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1603, "name_kh": " Charm 03", "price": 3000, "image": "/static/images/charm-cutecat-03.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1604, "name_kh": " Charm 04", "price": 3000, "image": "/static/images/charm-cutecat-04.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1605, "name_kh": " Charm 05", "price": 3000, "image": "/static/images/charm-cutecat-05.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1606, "name_kh": " Charm 06", "price": 3000, "image": "/static/images/charm-cutecat-06.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["Car Logo"]},
    {"id": 1607, "name_kh": " Charm 07", "price": 3000, "image": "/static/images/charm-cutecat-07.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["Car Logo"]},
    {"id": 1608, "name_kh": " Charm 08", "price": 3000, "image": "/static/images/charm-cutecat-08.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1609, "name_kh": " Charm 09", "price": 3000, "image": "/static/images/charm-cutecat-09.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1610, "name_kh": " Charm 10", "price": 3000, "image": "/static/images/charm-cutecat-10.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1611, "name_kh": " Charm 11", "price": 3000, "image": "/static/images/charm-cutecat-11.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},
    {"id": 1612, "name_kh": " Charm 12", "price": 3000, "image": "/static/images/charm-cutecat-12.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": ["All","Football"]},

    # --- Rok Jit (1701 - 1708) ---
    {"id": 1701, "name_kh": "Rok Jit 01", "price": 3000, "image": "/static/images/charm-rokjit-01.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1702, "name_kh": "Rok Jit 02", "price": 3000, "image": "/static/images/charm-rokjit-02.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1703, "name_kh": "Rok Jit 03", "price": 3000, "image": "/static/images/charm-rokjit-03.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1704, "name_kh": "Rok Jit 04", "price": 3000, "image": "/static/images/charm-rokjit-04.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1705, "name_kh": "Rok Jit 05", "price": 3000, "image": "/static/images/charm-rokjit-05.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1706, "name_kh": "Rok Jit 06", "price": 3000, "image": "/static/images/charm-rokjit-06.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},
    {"id": 1707, "name_kh": "Rok Jit 07", "price": 3000, "image": "/static/images/charm-rokjit-07.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]}, 
    {"id": 1708, "name_kh": "Rok Jit 08", "price": 3000, "image": "/static/images/charm-rokjit-08.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"]},

    # --- 8 Ball (1801 - 1803) ---
    {"id": 1801, "name_kh": "8 Ball 🎱 01", "price": 3000, "image": "/static/images/charm-8ball-01.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},
    {"id": 1802, "name_kh": "8 Ball 🎱 02", "price": 3000, "image": "/static/images/charm-8ball-02.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},
    {"id": 1803, "name_kh": "8 Ball 🎱 03", "price": 3000, "image": "/static/images/charm-8ball-03.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},

    # --- Cherry (1901) ---
    {"id": 1901, "name_kh": "Cherry 🍒 01", "price": 3000, "image": "/static/images/charm-cherry-01.jpg", "categories": ["Italy Bracelet", "Cherry 🍒"]},

    # --- Christmas (2501 - 2529) (Renumbered from 2001 to prevent conflict with Flags) ---
    {"id": 2501, "name_kh": "Christmas 🎄 01", "price": 3000, "image": "/static/images/charm-christmas-01.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2502, "name_kh": "Christmas 🎄 02", "price": 3000, "image": "/static/images/charm-christmas-02.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2503, "name_kh": "Christmas 🎄 03", "price": 3000, "image": "/static/images/charm-christmas-03.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2504, "name_kh": "Christmas 🎄 04", "price": 3000, "image": "/static/images/charm-christmas-04.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2505, "name_kh": "Christmas 🎄 05", "price": 3000, "image": "/static/images/charm-christmas-05.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2506, "name_kh": "Christmas 🎄 06", "price": 3000, "image": "/static/images/charm-christmas-06.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2507, "name_kh": "Christmas 🎄 07", "price": 3000, "image": "/static/images/charm-christmas-07.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]}, 
    {"id": 2508, "name_kh": "Christmas 🎄 08", "price": 3000, "image": "/static/images/charm-christmas-08.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2509, "name_kh": "Christmas 🎄 09", "price": 3000, "image": "/static/images/charm-christmas-09.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},

    {"id": 2511, "name_kh": "Christmas 🎄 11", "price": 3000, "image": "/static/images/charm-christmas-11.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2512, "name_kh": "Christmas 🎄 12", "price": 3000, "image": "/static/images/charm-christmas-12.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2513, "name_kh": "Christmas 🎄 13", "price": 3000, "image": "/static/images/charm-christmas-13.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2514, "name_kh": "Christmas 🎄 14", "price": 3000, "image": "/static/images/charm-christmas-14.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2515, "name_kh": "Christmas 🎄 15", "price": 3000, "image": "/static/images/charm-christmas-15.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2516, "name_kh": "Christmas 🎄 16", "price": 3000, "image": "/static/images/charm-christmas-16.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2517, "name_kh": "Christmas 🎄 17", "price": 3000, "image": "/static/images/charm-christmas-17.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]}, 
    {"id": 2518, "name_kh": "Christmas 🎄 18", "price": 3000, "image": "/static/images/charm-christmas-18.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2519, "name_kh": "Christmas 🎄 19", "price": 3000, "image": "/static/images/charm-christmas-19.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},

    {"id": 2521, "name_kh": "Christmas 🎄 21", "price": 3000, "image": "/static/images/charm-christmas-21.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2522, "name_kh": "Christmas 🎄 22", "price": 3000, "image": "/static/images/charm-christmas-22.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2523, "name_kh": "Christmas 🎄 23", "price": 3000, "image": "/static/images/charm-christmas-23.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2524, "name_kh": "Christmas 🎄 24", "price": 3000, "image": "/static/images/charm-christmas-04.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2525, "name_kh": "Christmas 🎄 25", "price": 3000, "image": "/static/images/charm-christmas-05.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2526, "name_kh": "Christmas 🎄 26", "price": 3000, "image": "/static/images/charm-christmas-06.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2527, "name_kh": "Christmas 🎄 27", "price": 3000, "image": "/static/images/charm-christmas-07.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]}, 
    {"id": 2528, "name_kh": "Christmas 🎄 28", "price": 3000, "image": "/static/images/charm-christmas-08.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},
    {"id": 2529, "name_kh": "Christmas 🎄 29", "price": 3000, "image": "/static/images/charm-christmas-09.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"]},

    # --- FLOWER (2101 - 2109) ---
    {"id": 2101, "name_kh": "Flower 🌹 01", "price": 3000, "image": "/static/images/charm-flower-01.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2102, "name_kh": "Flower 🌹 02", "price": 3000, "image": "/static/images/charm-flower-02.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2103, "name_kh": "Flower 🌹 03", "price": 3000, "image": "/static/images/charm-flower-03.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2104, "name_kh": "Flower 🌹 04", "price": 3000, "image": "/static/images/charm-flower-04.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2105, "name_kh": "Flower 🌹 05", "price": 3000, "image": "/static/images/charm-flower-05.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2106, "name_kh": "Flower 🌹 06", "price": 3000, "image": "/static/images/charm-flower-06.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2107, "name_kh": "Flower 🌹 07", "price": 3000, "image": "/static/images/charm-flower-07.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]}, 
    {"id": 2108, "name_kh": "Flower 🌹 08", "price": 3000, "image": "/static/images/charm-flower-08.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},
    {"id": 2109, "name_kh": "Flower 🌹 09", "price": 3000, "image": "/static/images/charm-flower-09.jpg", "categories": ["Italy Bracelet", "Flower 🌹"]},

    # --- LEGO (Examples) ---
    {"id": 9001, "name_kh": "Kai - Ninjago", "price": 5000, "image": "https://m.media-amazon.com/images/I/51+u+A-uG+L._AC_UF894,1000_QL80_.jpg", "categories": ["LEGO", "LEGO Ninjago"], "subcategory": "Season 1"},
    
    # --- KEYCHAINS (Examples) ---
    {"id": 8001, "name_kh": "Gun Keychain A", "price": 2500, "image": "https://down-ph.img.susercontent.com/file/sg-11134201-22100-bf65465465iv8c", "categories": ["Keychain"], "subcategory": "Gun Keychains"},

    # --- HOT SALE (Examples) ---
    {"id": 9999, "name_kh": "Special Set", "price": 10000, "image": "/static/images/special.jpg", "categories": ["Hot Sale", "LEGO"], "subcategory": "Sets"},
]

# --- SUBCATEGORIES MAP ---
SUBCATEGORIES_MAP = {
    "Hot Sale": [],
    "LEGO": ["LEGO Ninjago", "LEGO Anime", "Formula 1", "Lego WWII"],
    "LEGO Ninjago": ["Dragon Rising", "Season 1", "Season 2", "Season 13"],
    "LEGO Anime": ["One Piece", "Demon Slayer"],
    "Keychain": ["Gun Keychains", "Anime Keychains"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet"],
    "Toy": ["General Toys"],
}

# --- NAVIGATION MENU ---
NAV_MENU = [
    "Hot Sale",
    "LEGO", 
    "Keychain",
    "Accessories",
    "Toy",
    "Italy Bracelet", 
    "Lucky Draw"      
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
            
            # Handle subcategory (string or list)
            sub_val = item.get('subcategory', 'General')
            if isinstance(sub_val, list):
                sub_str = ", ".join(sub_val)
            else:
                sub_str = str(sub_val)
            
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

    # 3. Get Subcategories
    subs = SUBCATEGORIES_MAP.get(category_name, [])

    return render_template('home.html', 
                           products=filtered_products, 
                           current_category=category_name, 
                           menu=NAV_MENU,
                           subcategories=subs,
                           cart=session.get('cart', []))

@app.route('/subcategory/<sub_name>')
def subcategory_view(sub_name):
    # Route for clicking subcategory pills (e.g., /subcategory/LEGO%20Ninjago)
    all_products = Product.query.all()
    # Filter by checking if sub_name is in categories_str OR subcategory_str
    # This ensures items tagged with "LEGO Ninjago" in categories OR subcategory show up
    filtered = [p for p in all_products if sub_name in p.categories_str or sub_name in p.subcategory_str]
    
    return render_template('home.html', 
                           products=filtered, 
                           current_category=sub_name, 
                           menu=NAV_MENU,
                           subcategories=[], # Clear subs when inside a sub
                           cart=session.get('cart', []))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    all_products = Product.query.all()
    filtered = [p for p in all_products if query in p.name_kh.lower()]
    return render_template('home.html', 
                           products=filtered, 
                           current_category=f"Search: {query}", 
                           menu=NAV_MENU,
                           subcategories=[],
                           cart=session.get('cart', []))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    p_id = request.form.get('product_id')
    if p_id:
        cart = session.get('cart', [])
        cart.append(p_id)
        session['cart'] = cart
        return jsonify({"success": True, "cart_count": len(cart)})
    return jsonify({"success": False})

@app.route('/cart')
def view_cart():
    # Basic Cart View logic - for now redirect to home or render simple template
    cart_ids = session.get('cart', [])
    cart_items = []
    total = 0
    for pid in cart_ids:
        p = Product.query.get(pid)
        if p: 
            cart_items.append(p)
            total += p.price
    # If you have a cart.html, render it. If not, just show a basic list or redirect.
    # For this fix, I'll return a simple JSON dump or redirect back to shop if no template exists.
    return render_template('home.html', products=cart_items, current_category="My Cart", menu=NAV_MENU, subcategories=[], cart=cart_ids)

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


