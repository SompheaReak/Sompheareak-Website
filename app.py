import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  onSnapshot, 
  addDoc, 
  deleteDoc, 
  doc, 
  serverTimestamp,
  setDoc
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
  Truck,
  Phone,
  User,
  MapPin,
  History,
  Info
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'the-song-store';

// --- Constants ---
const BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8";
const CHAT_ID = "-1002654437316";

const CATEGORIES_MAP = {
  "Hot Sale": [],
  "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet", "Bracelet"],
  "LEGO Ninjago": ["Dragon Rising", "Building Set", "Season 1", "Season 2", "Season 3", "Season 4", "Season 5"],
  "LEGO Anime": ["One Piece", "Demon Slayer"],
  "Keychain": ["Gun Keychains"],
  "LEGO": ["Formula 1"],
  "Toy": ["Lego Ninjago", "One Piece", "Lego WWII", "Lego ទាហាន"],
  "Italy Bracelet": ["All", "Football", "Gem", "Flag", "Chain"],
  "Lucky Draw": ["/lucky-draw"]
};

const LANGUAGES = {
  kh: {
    storeName: "TheSong Store",
    addToCart: "ដាក់ក្នុងកន្ត្រក",
    checkout: "ទូទាត់ប្រាក់",
    cart: "កន្ត្រកទំនិញ",
    total: "សរុប",
    name: "ឈ្មោះ",
    phone: "លេខទូរស័ព្ទ",
    address: "អាសយដ្ឋាន",
    delivery: "សេវាដឹកជញ្ជូន",
    orderNow: "បញ្ជាទិញឥឡូវនេះ",
    admin: "គ្រប់គ្រង",
    history: "ប្រវត្តិកម្ម៉ង់",
    currency: "៛",
    emptyCart: "មិនទាន់មានទំនិញក្នុងកន្ត្រក"
  },
  en: {
    storeName: "TheSong Store",
    addToCart: "Add to Cart",
    checkout: "Checkout",
    cart: "Shopping Cart",
    total: "Total",
    name: "Full Name",
    phone: "Phone Number",
    address: "Address",
    delivery: "Delivery Method",
    orderNow: "Order Now",
    admin: "Admin",
    history: "Order History",
    currency: "KHR",
    emptyCart: "Your cart is empty"
  }
};

// --- Helper Functions ---
const sendTelegram = async (message) => {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: CHAT_ID,
        text: message,
        parse_mode: 'Markdown'
      })
    });
  } catch (err) {
    console.error("Telegram error:", err);
  }
};

export default function App() {
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState('kh');
  const [view, setView] = useState('shop');
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [activeCategory, setActiveCategory] = useState("Hot Sale");
  const [activeSub, setActiveSub] = useState("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAdminMode, setIsAdminMode] = useState(false);

  const t = LANGUAGES[lang];

  // Auth Initialization
  useEffect(() => {
    const init = async () => {
      try {
        await signInAnonymously(auth);
      } catch (e) { console.error(e); }
    };
    init();
    const unsub = onAuthStateChanged(auth, setUser);
    return () => unsub();
  }, []);

  // Data Listeners
  useEffect(() => {
    if (!user) return;

    const prodRef = collection(db, 'artifacts', appId, 'public', 'data', 'products');
    const unsubProd = onSnapshot(prodRef, (snap) => {
      const data = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      setProducts(data);
    });

    const orderRef = collection(db, 'artifacts', appId, 'users', user.uid, 'orders');
    const unsubOrder = onSnapshot(orderRef, (snap) => {
      const data = snap.docs.map(d => ({ id: d.id, ...d.data() }));
      setOrders(data);
    });

    // Notify Visitor (only once per mount)
    sendTelegram(`👀 *New Visitor*\nIP: Checked\nUser ID: \`${user.uid}\``);

    return () => { unsubProd(); unsubOrder(); };
  }, [user]);

  // Handlers
  const handleAddToCart = (p) => {
    setCart(prev => {
      const exists = prev.find(i => i.id === p.id);
      if (exists) return prev.map(i => i.id === p.id ? {...i, qty: i.qty + 1} : i);
      return [...prev, {...p, qty: 1}];
    });
  };

  const handleCheckout = async (customerData) => {
    if (!user || cart.length === 0) return;
    
    const subtotal = cart.reduce((acc, i) => acc + (i.price * i.qty), 0);
    const fee = customerData.delivery === "VET" ? 5000 : 7000;
    const finalTotal = subtotal + fee;

    const orderObj = {
      ...customerData,
      items: cart,
      subtotal,
      fee,
      total: finalTotal,
      timestamp: serverTimestamp(),
      status: 'pending'
    };

    try {
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'orders'), orderObj);
      
      let msg = `🛒 *NEW ORDER RECEIVED*\n`;
      msg += `👤 *Name:* ${customerData.name}\n📞 *Phone:* ${customerData.phone}\n📍 *Addr:* ${customerData.address}\n`;
      msg += `🚚 *Delivery:* ${customerData.delivery}\n\n*Items:*\n`;
      cart.forEach(i => msg += `- ${i.name_kh} x ${i.qty}\n`);
      msg += `\n💰 *Total:* ${finalTotal.toLocaleString()}៛`;
      
      sendTelegram(msg);
      setCart([]);
      setView('history');
    } catch (e) { console.error(e); }
  };

  const displayProducts = useMemo(() => {
    let list = products;
    if (activeCategory !== "Hot Sale") {
      list = products.filter(p => p.categories?.includes(activeCategory));
    }
    if (activeSub) {
      list = list.filter(p => p.subcategory?.includes(activeSub));
    }
    return list;
  }, [products, activeCategory, activeSub]);

  // Render Logic
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col text-slate-800">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-40 px-4 py-3 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-3">
          <button onClick={() => setIsMenuOpen(true)} className="p-1"><Menu size={24} /></button>
          <h1 className="font-extrabold text-xl text-red-600 tracking-tight">{t.storeName}</h1>
        </div>
        <div className="flex gap-4 items-center">
          <button onClick={() => setLang(lang === 'kh' ? 'en' : 'kh')} className="text-xs font-bold border rounded px-2 py-1 flex items-center gap-1">
            <Languages size={14} /> {lang.toUpperCase()}
          </button>
          <button onClick={() => setView('cart')} className="relative">
            <ShoppingBag size={24} />
            {cart.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <div className={`fixed inset-0 z-50 bg-black/40 transition-opacity ${isMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
        <div className={`w-72 bg-white h-full transition-transform duration-300 ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-4 border-b flex justify-between items-center">
            <span className="font-bold">Categories</span>
            <button onClick={() => setIsMenuOpen(false)}><X /></button>
          </div>
          <div className="p-2 overflow-y-auto h-[calc(100%-100px)]">
            {Object.keys(CATEGORIES_MAP).map(cat => (
              <button 
                key={cat}
                onClick={() => { setActiveCategory(cat); setActiveSub(""); setView('shop'); setIsMenuOpen(false); }}
                className={`w-full text-left p-3 rounded-lg flex justify-between items-center ${activeCategory === cat ? 'bg-red-50 text-red-600 font-bold' : 'hover:bg-gray-50'}`}
              >
                {cat} <ChevronRight size={14} />
              </button>
            ))}
            <div className="mt-4 pt-4 border-t px-2">
              <button onClick={() => { setView('admin'); setIsMenuOpen(false); }} className="flex items-center gap-3 text-gray-500 p-2"><ShieldCheck size={18} /> Admin Panel</button>
              <button onClick={() => { setView('history'); setIsMenuOpen(false); }} className="flex items-center gap-3 text-gray-500 p-2"><History size={18} /> My Orders</button>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 max-w-4xl mx-auto w-full p-4">
        {view === 'shop' && (
          <>
            <div className="mb-6 overflow-x-auto flex gap-2 no-scrollbar pb-2">
              {CATEGORIES_MAP[activeCategory]?.map(sub => (
                <button 
                  key={sub}
                  onClick={() => setActiveSub(sub === activeSub ? "" : sub)}
                  className={`px-4 py-1.5 rounded-full whitespace-nowrap text-sm border transition-all ${activeSub === sub ? 'bg-black text-white' : 'bg-white border-gray-200'}`}
                >
                  {sub}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {displayProducts.length > 0 ? displayProducts.map(p => (
                <div key={p.id} className="bg-white rounded-2xl border shadow-sm overflow-hidden flex flex-col">
                  <div className="aspect-square bg-gray-100">
                    <img src={p.image} alt="" className="w-full h-full object-cover" />
                  </div>
                  <div className="p-3 flex-1 flex flex-col">
                    <h3 className="font-bold text-sm leading-tight mb-1 line-clamp-2">
                      {lang === 'kh' ? p.name_kh : (p.name_en || p.name_kh)}
                    </h3>
                    <div className="mt-auto">
                      <p className="text-red-600 font-extrabold text-lg">{p.price?.toLocaleString()} {t.currency}</p>
                      <button 
                        onClick={() => handleAddToCart(p)}
                        className="w-full mt-2 bg-slate-900 text-white py-2 rounded-xl text-xs font-bold active:scale-95 transition-transform"
                      >
                        {t.addToCart}
                      </button>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-20 text-gray-400">
                  <Package size={48} className="mx-auto mb-2 opacity-20" />
                  <p>No items found in this section.</p>
                </div>
              )}
            </div>
          </>
        )}

        {view === 'cart' && (
          <div className="max-w-xl mx-auto">
            <button onClick={() => setView('shop')} className="flex items-center gap-2 mb-6 text-gray-500"><ArrowLeft size={18}/> Back</button>
            <h2 className="text-2xl font-bold mb-6">{t.cart}</h2>
            {cart.length > 0 ? (
              <div className="space-y-4">
                {cart.map(item => (
                  <div key={item.id} className="bg-white p-3 rounded-2xl border flex gap-4">
                    <img src={item.image} className="w-20 h-20 rounded-xl object-cover" />
                    <div className="flex-1 flex flex-col justify-between py-1">
                      <div className="flex justify-between items-start">
                        <span className="font-bold text-sm">{item.name_kh}</span>
                        <button onClick={() => setCart(cart.filter(i => i.id !== item.id))} className="text-red-500"><Trash2 size={16} /></button>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-red-600 font-bold">{item.price?.toLocaleString()}៛</span>
                        <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-1">
                          <button onClick={() => setCart(cart.map(i => i.id === item.id ? {...i, qty: Math.max(1, i.qty-1)} : i))} className="w-6 h-6 border rounded flex items-center justify-center">-</button>
                          <span className="text-sm font-bold">{item.qty}</span>
                          <button onClick={() => setCart(cart.map(i => i.id === item.id ? {...i, qty: i.qty+1} : i))} className="w-6 h-6 border rounded flex items-center justify-center">+</button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                <div className="mt-8 bg-white p-6 rounded-2xl border">
                  <div className="flex justify-between mb-6">
                    <span className="text-gray-500 text-lg">{t.total}</span>
                    <span className="text-2xl font-extrabold text-red-600">
                      {cart.reduce((s, i) => s + (i.price * i.qty), 0).toLocaleString()} {t.currency}
                    </span>
                  </div>
                  <button 
                    onClick={() => setView('checkout')}
                    className="w-full bg-red-600 text-white py-4 rounded-2xl font-bold shadow-lg shadow-red-100 active:scale-[0.98]"
                  >
                    {t.checkout}
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-gray-400">
                <ShoppingBag size={48} className="mx-auto mb-2 opacity-20" />
                <p>{t.emptyCart}</p>
              </div>
            )}
          </div>
        )}

        {view === 'checkout' && (
          <div className="max-w-xl mx-auto">
             <button onClick={() => setView('cart')} className="flex items-center gap-2 mb-6 text-gray-500"><ArrowLeft size={18}/> Back</button>
             <h2 className="text-2xl font-bold mb-6">Delivery Details</h2>
             <form className="space-y-4" onSubmit={(e) => {
               e.preventDefault();
               const fd = new FormData(e.target);
               handleCheckout(Object.fromEntries(fd));
             }}>
                <div className="bg-white p-6 rounded-2xl border space-y-4 shadow-sm">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-400 uppercase">{t.name}</label>
                    <div className="flex items-center border rounded-xl px-3 bg-gray-50">
                      <User size={18} className="text-gray-400" />
                      <input name="name" required className="bg-transparent w-full p-3 outline-none" placeholder="Enter full name" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-400 uppercase">{t.phone}</label>
                    <div className="flex items-center border rounded-xl px-3 bg-gray-50">
                      <Phone size={18} className="text-gray-400" />
                      <input name="phone" type="tel" required className="bg-transparent w-full p-3 outline-none" placeholder="012 345 678" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-400 uppercase">{t.address}</label>
                    <div className="flex items-start border rounded-xl px-3 bg-gray-50">
                      <MapPin size={18} className="text-gray-400 mt-4" />
                      <textarea name="address" required className="bg-transparent w-full p-3 outline-none h-24 resize-none" placeholder="House No, Street, District..." />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-gray-400 uppercase">{t.delivery}</label>
                    <select name="delivery" className="w-full p-4 border rounded-xl bg-gray-50 outline-none">
                      <option value="Standard">Standard Delivery (7000៛)</option>
                      <option value="VET">Vireak Buntham (5000៛)</option>
                      <option value="Express">J&T Express (7000៛)</option>
                    </select>
                  </div>
                </div>
                <button type="submit" className="w-full bg-black text-white py-4 rounded-2xl font-bold mt-4 shadow-xl">
                  {t.orderNow}
                </button>
             </form>
          </div>
        )}

        {view === 'history' && (
          <div className="max-w-xl mx-auto">
            <button onClick={() => setView('shop')} className="flex items-center gap-2 mb-6 text-gray-500"><ArrowLeft size={18}/> Home</button>
            <h2 className="text-2xl font-bold mb-6">Recent Orders</h2>
            <div className="space-y-4">
              {orders.length > 0 ? orders.sort((a,b) => b.timestamp - a.timestamp).map(o => (
                <div key={o.id} className="bg-white p-4 rounded-2xl border shadow-sm">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-xs font-bold text-gray-400">ID: ...{o.id.slice(-6)}</span>
                    <span className="text-[10px] px-2 py-1 bg-orange-100 text-orange-600 rounded-full font-bold uppercase">{o.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <div className="text-sm font-bold">
                      {o.items?.length} items • {o.delivery}
                    </div>
                    <div className="text-red-600 font-extrabold">{o.total?.toLocaleString()}៛</div>
                  </div>
                </div>
              )) : <p className="text-center py-10 text-gray-400">No orders found.</p>}
            </div>
          </div>
        )}

        {view === 'admin' && (
          <AdminPanel products={products} db={db} appId={appId} onBack={() => setView('shop')} />
        )}
      </main>

      {/* Footer Navigation (Mobile Style) */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t p-2 flex justify-around items-center z-40">
        <button onClick={() => setView('shop')} className={`flex flex-col items-center p-2 ${view === 'shop' ? 'text-red-600' : 'text-gray-400'}`}>
          <Package size={20} /> <span className="text-[10px] mt-1">Shop</span>
        </button>
        <button onClick={() => setView('cart')} className={`flex flex-col items-center p-2 ${view === 'cart' ? 'text-red-600' : 'text-gray-400'}`}>
          <ShoppingBag size={20} /> <span className="text-[10px] mt-1">Cart</span>
        </button>
        <button onClick={() => setView('history')} className={`flex flex-col items-center p-2 ${view === 'history' ? 'text-red-600' : 'text-gray-400'}`}>
          <History size={20} /> <span className="text-[10px] mt-1">Orders</span>
        </button>
      </footer>
    </div>
  );
}

function AdminPanel({ products, db, appId, onBack }) {
  const [showAdd, setShowAdd] = useState(false);
  
  const handleAdd = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd);
    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'products'), {
        ...data,
        price: Number(data.price),
        categories: [data.category],
        subcategory: [data.subcategory]
      });
      setShowAdd(false);
    } catch (e) { alert("Error adding product"); }
  };

  const handleDelete = async (id) => {
    if (confirm("Delete product?")) {
      await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'products', id));
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4">
      <div className="flex justify-between items-center mb-6">
        <button onClick={onBack} className="flex items-center gap-2 text-gray-500"><ArrowLeft size={18}/> Back</button>
        <button onClick={() => setShowAdd(true)} className="bg-red-600 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
          <Plus size={18} /> Add Item
        </button>
      </div>

      <div className="space-y-3 pb-20">
        {products.map(p => (
          <div key={p.id} className="bg-white p-3 rounded-2xl border flex items-center gap-4">
            <img src={p.image} className="w-12 h-12 rounded-lg object-cover" />
            <div className="flex-1">
              <p className="text-sm font-bold truncate">{p.name_kh}</p>
              <p className="text-xs text-gray-400">{p.price?.toLocaleString()}៛ • {p.category}</p>
            </div>
            <button onClick={() => handleDelete(p.id)} className="text-red-500 p-2"><Trash2 size={18}/></button>
          </div>
        ))}
      </div>

      {showAdd && (
        <div className="fixed inset-0 z-[100] bg-black/60 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl">
            <div className="flex justify-between mb-4">
              <h3 className="font-bold text-lg">New Product</h3>
              <button onClick={() => setShowAdd(false)}><X /></button>
            </div>
            <form onSubmit={handleAdd} className="space-y-4">
              <input name="name_kh" required placeholder="Name (Khmer)" className="w-full p-3 border rounded-xl" />
              <input name="name_en" placeholder="Name (English)" className="w-full p-3 border rounded-xl" />
              <input name="price" type="number" required placeholder="Price (៛)" className="w-full p-3 border rounded-xl" />
              <input name="image" required placeholder="Image URL" className="w-full p-3 border rounded-xl" />
              <div className="grid grid-cols-2 gap-2">
                <select name="category" className="p-3 border rounded-xl bg-white">
                  {Object.keys(CATEGORIES_MAP).map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <input name="subcategory" placeholder="Sub-category" className="p-3 border rounded-xl" />
              </div>
              <button className="w-full bg-black text-white py-4 rounded-xl font-bold">Add Product</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

