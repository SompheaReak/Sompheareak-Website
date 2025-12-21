import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
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
  Languages,
  ArrowLeft,
  Phone,
  User,
  MapPin,
  History,
  Search,
  CheckCircle2
} from 'lucide-react';

// --- Firebase Initialization (CRITICAL FOR DEPLOY) ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'the-song-store-v2';

// --- Constants ---
const BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8";
const CHAT_ID = "-1002654437316";

// Keeping your specific product storage way
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
  "Accessories": { 
    img: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400", 
    sub: ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet", "Bracelet"] 
  },
  "LEGO Ninjago": { 
    img: "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400", 
    sub: ["Dragon Rising", "Building Set", "Season 1", "Season 2", "Season 3"] 
  },
  "LEGO Anime": { 
    img: "https://images.unsplash.com/photo-1614583225154-5feaba071595?w=400", 
    sub: ["One Piece", "Demon Slayer"] 
  },
  "Keychain": { 
    img: "https://images.unsplash.com/photo-1582142407894-ec85a1260a46?w=400", 
    sub: ["Gun Keychains"] 
  },
  "Toy": { 
    img: "https://images.unsplash.com/photo-1531651008558-ed1740375b39?w=400", 
    sub: ["Lego Ninjago", "One Piece", "Lego WWII", "Lego ទាហាន"] 
  },
  "Italy Bracelet": { 
    img: "https://images.unsplash.com/photo-1535633302703-b0703af2939a?w=400", 
    sub: ["All", "Football", "Gem", "Flag", "Chain"] 
  },
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
    delivery: "សេវាដឹកជញ្ជូន",
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
    delivery: "Delivery Method",
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

  // RULE 3: Auth Before Queries
  useEffect(() => {
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
    const msg = `🚀 *NEW ORDER*\n👤 ${data.name}\n📞 ${data.phone}\n📍 ${data.address}\n🚚 ${data.delivery}\n\n*Items:* \n${cart.map(i => `- ${i.name_kh} x${i.qty}`).join('\n')}\n\n*Total:* ${subtotal.toLocaleString()}៛`;
    
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

  return (
    <div className="min-h-screen bg-[#F8F9FB] text-slate-900 font-sans pb-24">
      {/* Header */}
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
        {/* VIEW: HOME */}
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
                      <p className="text-white/60 text-[10px] font-bold uppercase tracking-widest mt-1">Explore Collection</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-12 mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-black">{t.trending}</h2>
              <button onClick={() => { setView('shop'); setActiveCategory(null); }} className="text-red-600 font-bold text-sm flex items-center gap-1">View All <ChevronRight size={16}/></button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
               {products.slice(0, 5).map(p => <ProductCard key={p.id} product={p} lang={lang} t={t} setCart={setCart} />)}
            </div>
          </div>
        )}

        {/* VIEW: SHOP */}
        {view === 'shop' && (
          <div className="animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div>
                <button onClick={() => setView('home')} className="flex items-center gap-2 text-gray-400 font-bold text-sm mb-2 hover:text-black transition-colors">
                  <ArrowLeft size={16}/> Back to Categories
                </button>
                <h2 className="text-4xl font-black tracking-tighter">{activeCategory || "All Products"}</h2>
              </div>
              
              {activeCategory && CATEGORY_DATA[activeCategory]?.sub.length > 0 && (
                <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2">
                  <button 
                    onClick={() => setActiveSub(null)}
                    className={`px-6 py-2.5 rounded-2xl whitespace-nowrap text-xs font-black transition-all ${!activeSub ? 'bg-red-600 text-white shadow-lg' : 'bg-white border border-gray-100'}`}
                  >
                    All
                  </button>
                  {CATEGORY_DATA[activeCategory].sub.map(s => (
                    <button 
                      key={s}
                      onClick={() => setActiveSub(s)}
                      className={`px-6 py-2.5 rounded-2xl whitespace-nowrap text-xs font-black transition-all ${activeSub === s ? 'bg-gray-900 text-white shadow-lg' : 'bg-white border border-gray-100'}`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {filteredProducts.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
                {filteredProducts.map(p => <ProductCard key={p.id} product={p} lang={lang} t={t} setCart={setCart} />)}
              </div>
            ) : (
              <div className="text-center py-20 bg-white rounded-[40px] border-2 border-dashed border-gray-100">
                <Search size={32} className="text-gray-300 mx-auto mb-4" />
                <h3 className="font-black text-xl">No products found</h3>
              </div>
            )}
          </div>
        )}

        {/* VIEW: CART */}
        {view === 'cart' && (
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 animate-in slide-in-from-bottom-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-black mb-6">{t.cart}</h2>
              {cart.length > 0 ? cart.map((item, idx) => (
                <div key={idx} className="bg-white p-4 rounded-[32px] border border-gray-100 flex gap-4 shadow-sm">
                  <img src={item.image} className="w-20 h-20 rounded-2xl object-cover bg-gray-50" alt={item.name_kh} />
                  <div className="flex-1 py-1 flex flex-col justify-between">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-sm leading-tight">{item.name_kh}</h4>
                      <button onClick={() => setCart(cart.filter((_, i) => i !== idx))} className="text-gray-300 hover:text-red-500 transition-colors"><Trash2 size={18}/></button>
                    </div>
                    <div className="flex justify-between items-center">
                       <span className="text-red-600 font-black">{item.price.toLocaleString()}៛</span>
                       <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-1 px-3">
                          <button onClick={() => setCart(cart.map((c, i) => i === idx ? {...c, qty: Math.max(1, c.qty-1)} : c))} className="font-black text-gray-400">-</button>
                          <span className="text-xs font-black w-4 text-center">{item.qty}</span>
                          <button onClick={() => setCart(cart.map((c, i) => i === idx ? {...c, qty: c.qty+1} : c))} className="font-black text-gray-400">+</button>
                       </div>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="bg-white p-12 rounded-[40px] text-center border-2 border-dashed border-gray-100">
                  <ShoppingBag size={48} className="mx-auto text-gray-200 mb-4" />
                  <p className="font-bold text-gray-400">Empty cart</p>
                </div>
              )}
            </div>

            <div className="bg-white p-8 rounded-[40px] shadow-xl shadow-gray-200/50 h-fit sticky top-24 border border-gray-50">
              <h3 className="text-xl font-black mb-6">Order Summary</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                const fd = new FormData(e.target);
                sendOrderToTelegram(Object.fromEntries(fd));
              }} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-gray-400 tracking-widest pl-2">{t.name}</label>
                  <div className="flex items-center bg-gray-50 rounded-2xl px-4 border border-transparent focus-within:border-red-500/20 transition-all">
                    <User size={16} className="text-gray-400" />
                    <input name="name" required className="w-full bg-transparent p-3.5 outline-none font-bold text-sm" placeholder="Your name" />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-gray-400 tracking-widest pl-2">{t.phone}</label>
                  <div className="flex items-center bg-gray-50 rounded-2xl px-4 border border-transparent focus-within:border-red-500/20 transition-all">
                    <Phone size={16} className="text-gray-400" />
                    <input name="phone" required className="w-full bg-transparent p-3.5 outline-none font-bold text-sm" placeholder="Phone number" />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-gray-400 tracking-widest pl-2">{t.address}</label>
                  <div className="flex items-start bg-gray-50 rounded-2xl px-4 border border-transparent focus-within:border-red-500/20 transition-all">
                    <MapPin size={16} className="text-gray-400 mt-4" />
                    <textarea name="address" required className="w-full bg-transparent p-3.5 outline-none font-bold text-sm h-20 resize-none" placeholder="Delivery address" />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-gray-400 tracking-widest pl-2">{t.delivery}</label>
                  <select name="delivery" className="w-full bg-gray-50 p-4 rounded-2xl outline-none font-bold text-sm border border-transparent focus:border-red-500/20 transition-all cursor-pointer">
                    <option>Standard Delivery (7,000៛)</option>
                    <option>VET Express (5,000៛)</option>
                    <option>J&T Express (7,000៛)</option>
                  </select>
                </div>

                <div className="pt-6 border-t border-gray-100 mt-6">
                  <div className="flex justify-between items-center mb-6">
                    <span className="text-gray-400 font-bold">{t.total}</span>
                    <span className="text-3xl font-black text-red-600">
                      {cart.reduce((s, i) => s + (i.price * i.qty), 0).toLocaleString()} {t.currency}
                    </span>
                  </div>
                  <button 
                    type="submit" 
                    disabled={cart.length === 0}
                    className="w-full bg-red-600 text-white py-5 rounded-[24px] font-black text-lg shadow-xl shadow-red-200 active:scale-95 disabled:opacity-50 transition-all"
                  >
                    {t.orderNow}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* VIEW: SUCCESS */}
        {view === 'success' && (
          <div className="max-w-md mx-auto py-20 text-center animate-in zoom-in-95 duration-500">
            <div className="w-24 h-24 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl shadow-green-100">
              <CheckCircle2 size={48} />
            </div>
            <h2 className="text-3xl font-black mb-3">Order Received!</h2>
            <p className="text-gray-500 font-medium mb-8">We have notified our staff. You will receive a call shortly to confirm your delivery.</p>
            <button onClick={() => setView('home')} className="w-full bg-gray-900 text-white py-5 rounded-[24px] font-black text-lg active:scale-95 transition-all">
              Back to Shopping
            </button>
          </div>
        )}
      </main>

      {/* Floating Bottom Nav */}
      <div className="fixed bottom-6 left-0 right-0 px-4 flex justify-center z-50 pointer-events-none">
        <nav className="bg-white/90 backdrop-blur-xl border border-white/20 shadow-[0_20px_60px_rgba(0,0,0,0.15)] p-2 rounded-[32px] flex gap-1 pointer-events-auto">
          <button onClick={() => { setView('home'); setActiveCategory(null); }} className={`p-4 rounded-[26px] flex items-center gap-2 transition-all ${view === 'home' || view === 'shop' ? 'bg-red-600 text-white shadow-xl shadow-red-200' : 'text-gray-400 hover:bg-gray-50'}`}>
            <Package size={20} strokeWidth={2.5} />
            {(view === 'home' || view === 'shop') && <span className="text-xs font-black">Shop</span>}
          </button>
          <button onClick={() => setView('cart')} className={`p-4 rounded-[26px] flex items-center gap-2 transition-all ${view === 'cart' || view === 'checkout' ? 'bg-red-600 text-white shadow-xl shadow-red-200' : 'text-gray-400 hover:bg-gray-50'}`}>
            <ShoppingBag size={20} strokeWidth={2.5} />
            {(view === 'cart' || view === 'checkout') && <span className="text-xs font-black">Cart</span>}
          </button>
          <button onClick={() => setView('admin')} className="p-4 rounded-[26px] text-gray-400 hover:bg-gray-50 transition-all">
            <ShieldCheck size={20} strokeWidth={2.5} />
          </button>
        </nav>
      </div>

      {/* Drawer Overlay */}
      <div className={`fixed inset-0 z-50 bg-black/40 backdrop-blur-sm transition-opacity duration-500 ${isMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
        <div className={`w-80 bg-white h-full shadow-2xl transition-transform duration-500 ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-8 border-b border-gray-50 flex justify-between items-center">
            <h2 className="font-black text-2xl tracking-tight">Menu</h2>
            <button onClick={() => setIsMenuOpen(false)} className="p-2 bg-gray-50 rounded-full"><X size={20}/></button>
          </div>
          <div className="p-6 space-y-2">
            <button onClick={() => { setView('home'); setIsMenuOpen(false); }} className="w-full text-left p-4 rounded-2xl font-black text-gray-700 hover:bg-gray-50 flex items-center gap-4 transition-all">
              <Package size={20}/> Categories
            </button>
            <button onClick={() => { setView('cart'); setIsMenuOpen(false); }} className="w-full text-left p-4 rounded-2xl font-black text-gray-700 hover:bg-gray-50 flex items-center gap-4 transition-all">
              <ShoppingBag size={20}/> My Cart
            </button>
            <div className="pt-8 mt-8 border-t border-gray-50 px-4">
              <p className="text-[10px] font-black text-gray-300 uppercase tracking-widest mb-4">Account</p>
              <button onClick={() => { setView('admin'); setIsMenuOpen(false); }} className="w-full text-left font-black text-gray-400 flex items-center gap-3">
                <ShieldCheck size={18}/> Staff Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProductCard({ product, t, setCart }) {
  const fallbackImg = "https://via.placeholder.com/400?text=TheSong+Store";

  return (
    <div className="bg-white rounded-[32px] border border-gray-100 overflow-hidden group shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-500 flex flex-col">
      <div className="aspect-square relative overflow-hidden bg-[#F2F4F7]">
        <img 
          src={product.image} 
          onError={(e) => { e.target.src = fallbackImg; }}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
          alt={product.name_kh} 
        />
        {product.discount > 0 && (
          <span className="absolute top-4 left-4 bg-red-600 text-white text-[10px] font-black px-2.5 py-1 rounded-xl shadow-lg">-{product.discount}%</span>
        )}
      </div>
      <div className="p-4 md:p-5 flex-1 flex flex-col">
        <h4 className="font-black text-xs md:text-sm line-clamp-2 mb-2 group-hover:text-red-600 transition-colors">{product.name_kh}</h4>
        <div className="mt-auto">
          <p className="text-red-600 font-black text-base md:text-lg mb-4">{product.price.toLocaleString()} {t.currency}</p>
          <button 
            onClick={() => setCart(prev => {
              const existing = prev.find(i => i.id === product.id);
              if (existing) return prev.map(i => i.id === product.id ? {...i, qty: i.qty + 1} : i);
              return [...prev, { ...product, qty: 1 }];
            })}
            className="w-full bg-gray-50 group-hover:bg-red-600 text-gray-900 group-hover:text-white py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 active:scale-95"
          >
            {t.addToCart}
          </button>
        </div>
      </div>
    </div>
  );
}

