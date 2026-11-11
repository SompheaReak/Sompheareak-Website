import os
import glob
import re
import json
from collections import defaultdict
from app import app, db
from models import Product, Category, MinifigurePool

def clean_title(name):
    # e.g. njoss10legacykai -> Ninjago S10 Legacy Kai
    # lego-wwii-army-101 -> LEGO WWII Army 101
    # charm-anime -> Anime Charms
    s = os.path.splitext(name)[0]
    s = s.replace('-', ' ').replace('_', ' ')
    
    # Season replacements
    s = re.sub(r'njoss(\d+)', r'Ninjago S\1 ', s, flags=re.I)
    s = re.sub(r'njodrgss(\d+)', r'Dragons Rising S\1 ', s, flags=re.I)
    s = re.sub(r'\blego\b', 'LEGO', s, flags=re.I)
    s = re.sub(r'\bwwii\b', 'WWII', s, flags=re.I)
    s = re.sub(r'\bcharm\b', 'Charm', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    return s.title()

def sync_images_to_database():
    with app.app_context():
        # SAFETY CHECK: Do not delete existing products!
        existing_count = Product.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} products. Aborting to ensure no overwriting.")
            return

        print("Syncing static images into products & categories...")

        # 1. Gather all static images
        images = sorted(glob.glob('static/images/*.*'))
        groups = defaultdict(list)

        for img in images:
            base = os.path.basename(img)
            name_no_ext = os.path.splitext(base)[0]

            if base.startswith('njos'):
                m = re.match(r'(njoss\d+[a-zA-Z]+)', name_no_ext)
                grp = m.group(1) if m else name_no_ext[:8]
                groups[('minifigure', 'Ninjago', grp)].append(base)
            elif base.startswith('njodrg'):
                m = re.match(r'(njodrgss\d+[a-zA-Z]+)', name_no_ext)
                grp = m.group(1) if m else name_no_ext[:10]
                groups[('minifigure', 'Ninjago', grp)].append(base)
            elif 'wwii' in base.lower():
                m = re.match(r'(lego-wwii-[a-zA-Z]+|wwii)', name_no_ext)
                grp = m.group(1) if m else 'wwii-army'
                groups[('minifigure,toy', 'Military', grp)].append(base)
            elif base.startswith('charm-'):
                parts = name_no_ext.split('-')
                grp = f'charm-{parts[1]}' if len(parts) > 1 else 'charm'
                groups[('custom_bracelet', 'Charm', grp)].append(base)
            elif base.startswith('bc-') or base.startswith('bc') or base.startswith('bcl'):
                groups[('bracelet', 'Bracelet', 'bracelets')].append(base)
            elif base.startswith('lego-') or base.startswith('dragon'):
                groups[('lego,toy', 'Building Sets', 'lego-sets')].append(base)
            elif base.startswith('lucky-'):
                groups[('toy,minifigure', 'Lucky Draw', 'lucky-box')].append(base)

        added_products = 0
        added_categories = set()

        for idx, ((store, category, grp_key), img_list) in enumerate(groups.items()):
            first_img_url = f"/static/images/{img_list[0]}"
            product_title = clean_title(grp_key)
            product_code = f"SKU{idx+1:04d}"

            variants = []
            total_stock = 0
            default_price = 1.50 if 'minifigure' in store else (2.00 if 'bracelet' in store else 15.00)

            for v_idx, img_name in enumerate(img_list):
                v_title = clean_title(img_name)
                v_img_url = f"/static/images/{img_name}"
                variants.append({
                    "id": v_idx,
                    "name": v_title,
                    "price": default_price,
                    "stock": 10,
                    "image": v_img_url,
                    "category": category,
                    "discount_percent": 0.0,
                    "code": f"{product_code}-{v_idx+1}"
                })
                total_stock += 10

            new_prod = Product(
                product_code=product_code,
                title=product_title,
                price=default_price,
                stock=total_stock,
                image=first_img_url,
                category=category,
                store=store,
                discount_percent=0.0,
                variants=json.dumps(variants),
                sort_order=idx,
                is_visible=True,
                use_custom_thumbnail=False,
                detail_images=json.dumps([f"/static/images/{img}" for img in img_list[:4]])
            )
            db.session.add(new_prod)
            added_products += 1

            # Ensure category is registered
            cat_tuple = (category, store.split(',')[0])
            if cat_tuple not in added_categories:
                added_categories.add(cat_tuple)
                if not Category.query.filter_by(name=category).first():
                    db.session.add(Category(name=category, store=store.split(',')[0], image=first_img_url, sort_order=len(added_categories)))

        # Also add lucky draw minifigure prizes if pool is empty
        if MinifigurePool.query.count() == 0:
            lucky_images = glob.glob('static/images/lucky-*.*')[:30]
            for l_idx, l_img in enumerate(lucky_images):
                rarity = "Legendary" if l_idx < 3 else ("Epic" if l_idx < 10 else ("Rare" if l_idx < 20 else "Common"))
                base_name = os.path.basename(l_img)
                db.session.add(MinifigurePool(
                    name=f"Minifigure Prize #{l_idx+1}",
                    image=f"/static/images/{base_name}",
                    rarity=rarity,
                    stock=5,
                    sort_order=l_idx
                ))

        db.session.commit()
        print(f"Successfully synced {added_products} catalog items into the database!")

if __name__ == '__main__':
    sync_images_to_database()
