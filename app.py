import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  onSnapshot, 
  addDoc, 
  doc, 
  serverTimestamp 
} from 'firebase/firestore';
import { 
  ShoppingBag, 
  Package, 
  Plus, 
  Trash2, 
  ChevronRight, 
  Menu, 
  X, 
  ShieldCheck, 
  ArrowLeft,
  Phone,
  User,
  MapPin,
  Search,
  CheckCircle2
} from 'lucide-react';

// --- CRITICAL: Safe Global Variable Handling ---
// This prevents the "Deploy Failed" error caused by missing/invalid environment variables
const getSafeConfig = () => {
  try {
    if (typeof __firebase_config !== 'undefined' && __firebase_config) {
      return JSON.parse(__firebase_config);
    }
  } catch (e) {
    console.error("Firebase config parse error:", e);
  }
  return null;
};

const appId = typeof __app_id !== 'undefined' ? __app_id : 'the-song-store-default';
const firebaseConfig = getSafeConfig();

// Initialize Firebase only if config exists
let app, auth, db;
if (firebaseConfig) {
  app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
  auth = getAuth(app);
  db = getFirestore(app);
}

// --- Constants ---
const BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8";
const CHAT_ID = "-1002654437316";

const INITIAL_PRODUCTS = [
  { 
    "id": 1, 
    "name_kh": "#OP01 One Piece - Sakazuki",
    "price": 7500, 
    "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/op01.jpg", 
    "categories": ["LEGO Anime", "Toy"], 
    "subcategory": ["One Piece"],
    "stock": 1,
    "discount": 0 
  },
  { 
    "id": 2, 
    "name_kh": "#OP02 One Piece - Portgas D Ace",
    "price": 6500, 
    "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/op02.jpg", 
    "categories": ["LEGO Anime", "Toy"], 
    "subcategory": ["One Piece"],
    "stock": 1,
    "discount": 0 
  }
];

const CATEGORY_DATA = {
  "Hot Sale": { img: "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400", sub: [] },
  "Accessories": { img: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400", sub: ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet", "Bracelet"] },
  "LEGO Ninjago": { img: "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400", sub: ["Dragon Rising", "Building Set"] },
  "LEGO Anime": { img: "https://images.unsplash.com/photo-1614583225154-5feaba071595?w=400", sub: ["One Piece", "Demon Slayer"] },
  "Keychain": { img: "https://images.unsplash.com/photo-1582142407894-ec85a1260a46?w=400", sub: ["Gun Keychains"] },
  "Toy": { img: "https://images.unsplash.com/photo-1531651008558-ed1740375b39?w=400", sub: ["Lego Ninjago", "One Piece"] },
  "Italy Bracelet": { img: "https://images.unsplash.com/photo-1535633302703-b0703af2939a?w=400", sub: ["All", "Football", "Flag"] },
  "Lucky Draw": { img: "https://images.unsplash.com/photo-1596838132731-163467475510?w=400", sub: ["Play"] }
};

const LANGUAGES = {
  kh: {
    storeName: "TheSong Store",
    addToCart: "បន្ថែមទៅក្នុងកន្ត្រក",
    checkout: "បន្តទៅការទូទាត់",
    cart: "កន្ត្រកទំនិញ",
    total: "សរុប",
    name: "ឈ្មោះពេញ",
    phone: "លេខទូរស័ព្ទ",
    address: "អាសយដ្ឋានដឹកជញ្ជូន",
    orderNow: "បញ្ជាទិញឥឡូវនេះ",
    currency: "៛",
    explore: "ស្វែងរកតាមប្រភេទ",
    trending: "ទំនិញពេញនិយម"
  },
  en: {
    storeName: "TheSong Store",
    addToCart: "Add to Cart",
    checkout: "Checkout Now",
    cart: "Your Cart",
    total: "Subtotal",
    name: "Full Name",
    phone: "Phone Number",
    address: "Shipping Address",
    orderNow: "Complete Order",
    currency: "KHR",
    explore: "Shop by Category",
    trending: "Trending Now"
  }
};

export default function App() {
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState('kh');
  const [view, setView] = useState('home'); 
  const [activeCategory, setActiveCategory] = useState(null);
  const [activeSub, setActiveSub] = useState(null);
  const [products] = useState(INITIAL_PRODUCTS);
  const [cart, setCart] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const t = LANGUAGES[lang];

  // Auth Initialization (Mandatory Rule 3)
  useEffect(() => {
    if (!auth) return;

    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (e) {
        console.error("Auth failed:", e);
      }
    };
    initAuth();
    const unsub = onAuthStateChanged(auth, setUser);
    return () => unsub();
  }, []);

  const filteredProducts = useMemo(() => {
    let list = products;
    if (activeCategory && activeCategory !== "Hot Sale") {
      list = list.filter(p => p.categories?.includes(activeCategory));
    }
    if (activeSub) {
      list = list.filter(p => p.subcategory?.includes(activeSub));
    }
    if (searchQuery) {
      list = list.filter(p => p.name_kh.toLowerCase().includes(searchQuery.toLowerCase()));
    }
    return list;
  }, [products, activeCategory, activeSub, searchQuery]);

  const sendOrderToTelegram = async (data) => {
    const subtotal = cart.reduce((acc, i) => acc + (i.price * i.qty), 0);
    const msg = `🚀 *NEW ORDER*\n👤 ${data.name}\n📞 ${data.phone}\n📍 ${data.address}\n\n*Items:* \n${cart.map(i => `- ${i.name_kh} x${i.qty}`).join('\n')}\n\n*Total:* ${subtotal.toLocaleString()}៛`;
    
    try {
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: CHAT_ID, text: msg, parse_mode: 'Markdown' })
      });
      setCart([]);
      setView('success');
    } catch (err) {
      console.error("Telegram error:", err);
    }
  };

  // Guard: If no config, show setup instructions instead of crashing
  if (!firebaseConfig) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6 text-center">
        <ShieldCheck className="text-red-500 mb-4" size={64} />
        <h1 className="text-2xl font-black mb-2">Setup Required</h1>
        <p className="text-gray-500 max-w-sm">Please add your Firebase configuration to the project settings to enable store features.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FB] text-slate-900 font-sans pb-24">
      {/* Navbar */}
      <nav className="bg-white/80 backdrop-blur-xl sticky top-0 z-40 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsMenuOpen(true)} className="p-2 hover:bg-gray-50 rounded-xl transition-colors">
              <Menu size={22} strokeWidth={2.5} />
            </button>
            <h1 onClick={() => { setView('home'); setActiveCategory(null); }} className="text-xl font-black tracking-tight cursor-pointer text-red-600">
              THESONG
            </h1>
          </div>

          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="ស្វែងរកទំនិញ..." 
                className="w-full bg-gray-100 border-none rounded-2xl py-2 pl-10 pr-4 text-sm focus:ring-2 ring-red-500/20 transition-all outline-none font-medium"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={() => setLang(lang === 'kh' ? 'en' : 'kh')} className="text-[10px] font-black border-2 border-gray-100 px-3 py-1.5 rounded-xl hover:bg-gray-50 uppercase">
              {lang}
            </button>
            <button onClick={() => setView('cart')} className="relative p-2.5 bg-gray-900 text-white rounded-2xl shadow-lg active:scale-95 transition-transform">
              <ShoppingBag size={20} />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-white">
                  {cart.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 pt-6">
        {view === 'home' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="mb-8">
              <h2 className="text-3xl font-black tracking-tight mb-2">{t.explore}</h2>
              <div className="h-1.5 w-12 bg-red-600 rounded-full"></div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
              {Object.entries(CATEGORY_DATA).map(([name, meta]) => (
                <div 
                  key={name}
                  onClick={() => {
                    setActiveCategory(name);
                    setActiveSub(null);
                    setView('shop');
                  }}
                  className="group relative h-40 md:h-56 rounded-[32px] overflow-hidden cursor-pointer shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-500"
                >
                  <img src={meta.img} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" alt={name} />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent flex items-end p-5 md:p-6">
                    <div>
                      <h3 className="text-white font-black text-lg md:text-xl leading-tight">{name}</h3>
                      <p className="text-white/60 text-[10px] font-bold uppercase tracking-widest mt-1">Collection</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'shop' && (
          <div className="animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <button onClick={() => setView('home')} className="flex items-center gap-2 text-gray-400 font-bold text-sm hover:text-black transition-colors w-fit">
                <ArrowLeft size={16}/> Back
              </button>
              <h2 className="text-4xl font-black tracking-tighter">{activeCategory}</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
              {filteredProducts.map(p => <ProductCard key={p.id} product={p} t={t} setCart={setCart} />)}
            </div>
          </div>
        )}

        {view === 'cart' && (
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 animate-in slide-in-from-bottom-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-black mb-6">{t.cart}</h2>
              {cart.map((item, idx) => (
                <div key={idx} className="bg-white p-4 rounded-[32px] border border-gray-100 flex gap-4">
                  <img src={item.image} className="w-20 h-20 rounded-2xl object-cover" alt={item.name_kh} />
                  <div className="flex-1 flex flex-col justify-between">
                    <h4 className="font-bold text-sm">{item.name_kh}</h4>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600 font-black">{item.price.toLocaleString()}៛</span>
                      <button onClick={() => setCart(cart.filter((_, i) => i !== idx))} className="text-gray-300 hover:text-red-500"><Trash2 size={18}/></button>
                    </div>
                  </div>
                </div>
              ))}
              {cart.length === 0 && <p className="text-center py-10 text-gray-400 font-bold">Your cart is empty</p>}
            </div>

            <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-50 h-fit">
              <h3 className="text-xl font-black mb-6">Checkout</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                sendOrderToTelegram(Object.fromEntries(new FormData(e.target)));
              }} className="space-y-4">
                <input name="name" required className="w-full bg-gray-50 p-4 rounded-2xl outline-none font-bold text-sm" placeholder={t.name} />
                <input name="phone" required className="w-full bg-gray-50 p-4 rounded-2xl outline-none font-bold text-sm" placeholder={t.phone} />
                <textarea name="address" required className="w-full bg-gray-50 p-4 rounded-2xl outline-none font-bold text-sm h-24" placeholder={t.address} />
                <div className="pt-6 border-t flex justify-between items-center">
                  <span className="font-bold text-gray-400">{t.total}</span>
                  <span className="text-2xl font-black text-red-600">{cart.reduce((s, i) => s + (i.price * i.qty), 0).toLocaleString()}៛</span>
                </div>
                <button type="submit" disabled={cart.length === 0} className="w-full bg-red-600 text-white py-5 rounded-3xl font-black disabled:opacity-50">
                  {t.orderNow}
                </button>
              </form>
            </div>
          </div>
        )}

        {view === 'success' && (
          <div className="max-w-md mx-auto py-20 text-center animate-in zoom-in-95">
            <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} />
            </div>
            <h2 className="text-3xl font-black mb-2">Order Success!</h2>
            <p className="text-gray-500 mb-8">We will contact you shortly.</p>
            <button onClick={() => setView('home')} className="w-full bg-gray-900 text-white py-4 rounded-2xl font-black">Back to Home</button>
          </div>
        )}
      </main>

      {/* Dock */}
      <div className="fixed bottom-6 left-0 right-0 px-4 flex justify-center z-50">
        <nav className="bg-white/90 backdrop-blur-xl border border-gray-100 shadow-2xl p-2 rounded-[32px] flex gap-1">
          <button onClick={() => setView('home')} className={`p-4 rounded-[26px] ${view === 'home' ? 'bg-red-600 text-white shadow-lg shadow-red-200' : 'text-gray-400'}`}>
            <Package size={20} />
          </button>
          <button onClick={() => setView('cart')} className={`p-4 rounded-[26px] ${view === 'cart' ? 'bg-red-600 text-white shadow-lg shadow-red-200' : 'text-gray-400'}`}>
            <ShoppingBag size={20} />
          </button>
        </nav>
      </div>
    </div>
  );
}

function ProductCard({ product, t, setCart }) {
  return (
    <div className="bg-white rounded-[32px] border border-gray-100 overflow-hidden group shadow-sm hover:shadow-xl transition-all flex flex-col">
      <div className="aspect-square relative overflow-hidden bg-gray-50">
        <img src={product.image} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" alt={product.name_kh} />
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <h4 className="font-black text-xs mb-2 line-clamp-2">{product.name_kh}</h4>
        <p className="text-red-600 font-black text-base mt-auto mb-3">{product.price.toLocaleString()}៛</p>
        <button 
          onClick={() => setCart(prev => {
            const exists = prev.find(i => i.id === product.id);
            if (exists) return prev.map(i => i.id === product.id ? {...i, qty: i.qty + 1} : i);
            return [...prev, { ...product, qty: 1 }];
          })}
          className="w-full bg-gray-900 text-white py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest active:scale-95 transition-all"
        >
          {t.addToCart}
        </button>
      </div>
    </div>
  );
}

