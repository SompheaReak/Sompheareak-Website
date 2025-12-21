import React, { useState, useEffect, useMemo } from 'react';
import { 
  ShoppingBag, 
  Package, 
  Trash2, 
  Menu, 
  X, 
  ShieldCheck, 
  Search, 
  Gift, 
  Lock,
  CheckCircle,
  Truck,
  ArrowLeft
} from 'lucide-react';

// --- CONFIGURATION ---
const ADMIN_USERNAME = 'AdminSompheaReakVitou';
const ADMIN_PASSWORD = 'Thesong_Admin@2022?!$';

// Mapped from your Python 'products' list
const INITIAL_PRODUCTS = [
  { 
    id: 101, 
    name_kh: "NINJAGO Season 1 - DX Suit", 
    price: 30000, 
    image: "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dx.jpg", 
    categories: ["LEGO Ninjago", "Toy"], 
    subcategory: ["Lego Ninjago", "Season 1"], 
    stock: 1 
  },
  { 
    id: 102, 
    name_kh: "NINJAGO Season 1 - KAI (DX)", 
    price: 5000, 
    image: "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxkai.jpg", 
    categories: ["LEGO Ninjago", "Toy"], 
    subcategory: ["Lego Ninjago", "Season 1"], 
    stock: 1 
  },
  { 
    id: 103, 
    name_kh: "NINJAGO Season 1 - ZANE (DX)", 
    price: 5000, 
    image: "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxzane.jpg", 
    categories: ["LEGO Ninjago", "Toy"], 
    subcategory: ["Lego Ninjago", "Season 1"], 
    stock: 1 
  }
];

const CATEGORY_MAP = {
  "Hot Sale": [],
  "LEGO Ninjago": ["Dragon Rising", "Building Set", "Season 1", "Season 2", "Season 3", "Season 4", "Season 5"],
  "LEGO Anime": ["One Piece", "Demon Slayer"],
  "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet", "Bracelet"],
  "Toy": ["Lego Ninjago", "One Piece", "Lego WWII", "Lego ទាហាន"],
  "Keychain": ["Gun Keychains"],
  "Italy Bracelet": ["All", "Football", "Gem", "Flag", "Chain"],
  "LEGO": ["Formula 1"],
  "Lucky Draw": ["/lucky-draw"]
};

// NEW: Images for categories
const CATEGORY_IMAGES = {
  "Hot Sale": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=200",
  "LEGO Ninjago": "https://images.unsplash.com/photo-1560000593-06674681330c?w=200",
  "LEGO Anime": "https://images.unsplash.com/photo-1566576912902-1dcd1b6d0e3d?w=200",
  "Accessories": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=200",
  "Toy": "https://images.unsplash.com/photo-1558877385-48572c023785?w=200",
  "Keychain": "https://images.unsplash.com/photo-1622619000171-8935c421735d?w=200",
  "Italy Bracelet": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=200",
  "LEGO": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=200",
  "Lucky Draw": "https://images.unsplash.com/photo-1513201099705-a9746e1e201f?w=200"
};

export default function App() {
  const [view, setView] = useState('home');
  const [activeCategory, setActiveCategory] = useState("LEGO Ninjago"); 
  const [activeSub, setActiveSub] = useState(null);
  const [products, setProducts] = useState(INITIAL_PRODUCTS);
  const [cart, setCart] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminInput, setAdminInput] = useState({ user: '', pass: '' });
  const [checkoutStatus, setCheckoutStatus] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Filtering Logic
  const filteredProducts = useMemo(() => {
    let list = products;
    
    // Category Filter
    if (activeCategory && activeCategory !== "Hot Sale") {
      list = list.filter(p => p.categories?.includes(activeCategory));
    }
    
    // Subcategory Filter
    if (activeSub) {
      list = list.filter(p => p.subcategory?.includes(activeSub));
    }

    // Search Filter
    if (searchQuery) {
      list = list.filter(p => p.name_kh.toLowerCase().includes(searchQuery.toLowerCase()));
    }
    
    return list;
  }, [products, activeCategory, activeSub, searchQuery]);

  // Handlers
  const addToCart = (product) => {
    setCart(prev => [...prev, { ...product, qty: 1 }]);
  };

  const handleCheckout = (e) => {
    e.preventDefault();
    setCheckoutStatus('sending');
    setTimeout(() => {
      setCheckoutStatus('success');
      setCart([]);
    }, 1500);
  };

  const handleAdminLogin = (e) => {
    e.preventDefault();
    if (adminInput.user === ADMIN_USERNAME && adminInput.pass === ADMIN_PASSWORD) {
      setIsAdmin(true);
    } else {
      alert("Incorrect Credentials");
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] text-slate-900 font-sans pb-24">
      
      {/* Navbar */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-40 border-b border-gray-100 px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => setIsMenuOpen(true)} className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
            <Menu size={22} strokeWidth={2.5} />
          </button>
          <h1 onClick={() => setView('home')} className="text-xl font-black text-red-600 tracking-tighter cursor-pointer">
            THESONG
          </h1>
        </div>
        
        <div className="flex items-center gap-2">
           <button onClick={() => setView('cart')} className="relative p-2.5 bg-gray-900 text-white rounded-xl shadow-lg shadow-gray-200">
            <ShoppingBag size={20} />
            {cart.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-600 text-[10px] w-5 h-5 flex items-center justify-center rounded-full border-2 border-white font-bold">
                {cart.length}
              </span>
            )}
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-2 pt-4">
        
        {view === 'home' && (
          <div className="animate-in fade-in duration-500">
            
            {/* Category Images (Grid 4 per row) */}
            <div className="grid grid-cols-4 gap-4 pb-6 px-2">
              {Object.keys(CATEGORY_MAP).map(cat => (
                <button 
                  key={cat}
                  onClick={() => {
                    if (cat === 'Lucky Draw') setView('lucky-draw');
                    else { setActiveCategory(cat); setActiveSub(null); }
                  }}
                  className="flex flex-col items-center gap-2 group"
                >
                  <div className={`w-16 h-16 rounded-full p-0.5 border-2 transition-all duration-300 ${activeCategory === cat ? 'border-red-600 scale-110 shadow-md' : 'border-transparent bg-white shadow-sm'}`}>
                    <div className="w-full h-full rounded-full overflow-hidden bg-gray-100">
                         <img 
                           src={CATEGORY_IMAGES[cat] || "https://via.placeholder.com/100"} 
                           alt={cat} 
                           className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                         />
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold text-center leading-tight ${activeCategory === cat ? 'text-red-600' : 'text-gray-600'}`}>
                    {cat === 'Lucky Draw' ? '🎁 Lucky' : cat}
                  </span>
                </button>
              ))}
            </div>

            {/* Subcategories */}
            {CATEGORY_MAP[activeCategory] && CATEGORY_MAP[activeCategory].length > 0 && (
              <div className="flex gap-2 overflow-x-auto no-scrollbar pb-4 px-2">
                 <button 
                    onClick={() => setActiveSub(null)}
                    className={`px-4 py-1.5 rounded-xl whitespace-nowrap text-[10px] font-bold uppercase transition-all ${!activeSub ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-500'}`}
                 >
                   All
                 </button>
                 {CATEGORY_MAP[activeCategory].map(sub => (
                   <button 
                      key={sub}
                      onClick={() => setActiveSub(sub)}
                      className={`px-4 py-1.5 rounded-xl whitespace-nowrap text-[10px] font-bold uppercase transition-all ${activeSub === sub ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-500'}`}
                   >
                     {sub}
                   </button>
                 ))}
              </div>
            )}

            {/* STRICT 4-COLUMN GRID */}
            <div className="grid grid-cols-4 gap-2 px-2">
               {filteredProducts.map(p => (
                 <div key={p.id} className="bg-white rounded-[16px] overflow-hidden border border-gray-100 flex flex-col group active:scale-95 transition-transform">
                    <div className="aspect-square relative bg-gray-50">
                       <img 
                          src={p.image} 
                          onError={(e) => e.target.src = "https://via.placeholder.com/150?text=No+Img"}
                          className="w-full h-full object-cover" 
                          alt={p.name_kh} 
                       />
                    </div>
                    <div className="p-2 flex-1 flex flex-col text-center">
                       <h3 className="text-[10px] font-bold leading-tight line-clamp-2 min-h-[2.4em] mb-1">{p.name_kh}</h3>
                       <p className="text-[10px] font-black text-red-600 mb-2">{p.price.toLocaleString()}៛</p>
                       <button 
                          onClick={() => addToCart(p)}
                          className="w-full bg-gray-100 hover:bg-red-600 hover:text-white py-2 rounded-lg text-[9px] font-black uppercase tracking-widest mt-auto transition-colors"
                       >
                         Add
                       </button>
                    </div>
                 </div>
               ))}
            </div>
            
            {filteredProducts.length === 0 && (
               <div className="text-center py-20 opacity-50">
                  <Package size={48} className="mx-auto mb-2"/>
                  <p className="font-bold text-sm">No items found</p>
               </div>
            )}
          </div>
        )}

        {/* LUCKY DRAW VIEW */}
        {view === 'lucky-draw' && (
          <div className="p-4 flex flex-col items-center justify-center min-h-[60vh] text-center animate-in zoom-in-95">
             <div className="w-full max-w-sm bg-white rounded-[40px] border-2 border-dashed border-gray-200 p-8 shadow-xl">
                <Gift className="w-16 h-16 text-red-600 mx-auto mb-6" />
                <h2 className="text-3xl font-black mb-2">Lucky Draw</h2>
                <p className="text-gray-400 text-sm font-bold mb-8">Spin to win exclusive Minifigures!</p>
                <div className="bg-yellow-400 w-48 h-48 rounded-full border-4 border-white shadow-xl mx-auto mb-8 flex items-center justify-center relative overflow-hidden group cursor-pointer active:rotate-[1080deg] transition-transform duration-[3000ms]">
                   <span className="text-4xl font-black text-yellow-700">?</span>
                </div>
                <button className="w-full bg-red-600 text-white py-4 rounded-2xl font-black shadow-lg shadow-red-200 active:scale-95 transition-all">
                  SPIN (5000៛)
                </button>
             </div>
             <button onClick={() => setView('home')} className="mt-8 text-gray-400 font-bold flex items-center gap-2">
               <ArrowLeft size={16}/> Back to Store
             </button>
          </div>
        )}

        {/* CART VIEW */}
        {view === 'cart' && (
          <div className="p-4 animate-in slide-in-from-bottom-4">
             <h2 className="text-2xl font-black mb-6">Your Cart ({cart.length})</h2>
             <div className="space-y-3 mb-8">
               {cart.map((item, idx) => (
                 <div key={idx} className="bg-white p-3 rounded-2xl border border-gray-100 flex gap-3">
                   <img src={item.image} className="w-16 h-16 rounded-xl object-cover bg-gray-50" />
                   <div className="flex-1 flex flex-col justify-center">
                     <h4 className="font-bold text-xs">{item.name_kh}</h4>
                     <p className="text-red-600 font-black text-xs">{item.price.toLocaleString()}៛</p>
                   </div>
                   <button onClick={() => setCart(cart.filter((_, i) => i !== idx))} className="text-gray-300 hover:text-red-500">
                     <Trash2 size={18} />
                   </button>
                 </div>
               ))}
             </div>
             
             {cart.length > 0 ? (
               <div className="bg-white p-6 rounded-[32px] shadow-xl border border-gray-100">
                 <h3 className="font-black text-lg mb-4">Checkout</h3>
                 <form onSubmit={handleCheckout} className="space-y-3">
                   <input required placeholder="Your Name" className="w-full bg-gray-50 p-3 rounded-xl text-xs font-bold outline-none focus:ring-2 ring-red-500/20" />
                   <input required placeholder="Phone Number" className="w-full bg-gray-50 p-3 rounded-xl text-xs font-bold outline-none focus:ring-2 ring-red-500/20" />
                   <div className="flex justify-between items-center py-4 border-t border-gray-100 mt-4">
                     <span className="font-bold text-gray-400">Total</span>
                     <span className="text-2xl font-black text-red-600">{cart.reduce((s, i) => s + i.price, 0).toLocaleString()}៛</span>
                   </div>
                   <button className="w-full bg-gray-900 text-white py-4 rounded-xl font-black text-sm shadow-xl active:scale-95 transition-all">
                     ORDER NOW
                   </button>
                 </form>
               </div>
             ) : (
               <div className="text-center py-20 text-gray-400 font-bold">Cart is empty</div>
             )}
          </div>
        )}

        {/* SUCCESS VIEW */}
        {checkoutStatus === 'success' && (
           <div className="fixed inset-0 z-50 bg-white flex flex-col items-center justify-center p-8 text-center animate-in zoom-in-95">
              <div className="w-24 h-24 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6">
                <CheckCircle size={48} />
              </div>
              <h2 className="text-3xl font-black mb-2">Order Sent!</h2>
              <p className="text-gray-500 font-bold text-sm mb-8">We have sent your order to Telegram. <br/>Our staff will contact you shortly.</p>
              <button onClick={() => { setCheckoutStatus(null); setView('home'); }} className="bg-gray-900 text-white px-8 py-3 rounded-xl font-black">
                Back to Shop
              </button>
           </div>
        )}

        {/* ADMIN LOGIN */}
        {view === 'admin' && !isAdmin && (
           <div className="p-4 flex flex-col items-center justify-center min-h-[60vh] animate-in slide-in-from-bottom-4">
              <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-100 w-full max-w-sm text-center">
                 <Lock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                 <h2 className="text-xl font-black mb-6">Admin Access</h2>
                 <form onSubmit={handleAdminLogin} className="space-y-4">
                    <input 
                      placeholder="Username" 
                      className="w-full bg-gray-50 p-4 rounded-2xl font-bold text-xs outline-none"
                      value={adminInput.user}
                      onChange={e => setAdminInput({...adminInput, user: e.target.value})}
                    />
                    <input 
                      type="password"
                      placeholder="Password" 
                      className="w-full bg-gray-50 p-4 rounded-2xl font-bold text-xs outline-none"
                      value={adminInput.pass}
                      onChange={e => setAdminInput({...adminInput, pass: e.target.value})}
                    />
                    <button className="w-full bg-gray-900 text-white py-4 rounded-2xl font-black">LOGIN</button>
                 </form>
              </div>
           </div>
        )}
        
        {/* ADMIN DASHBOARD */}
        {view === 'admin' && isAdmin && (
           <div className="p-4 space-y-6">
              <div className="flex justify-between items-center">
                 <h2 className="text-2xl font-black">Dashboard</h2>
                 <button onClick={() => setIsAdmin(false)} className="text-red-600 font-bold text-xs">LOGOUT</button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                 <div className="bg-white p-6 rounded-[24px] border border-gray-100">
                    <p className="text-[10px] font-black uppercase text-gray-400 mb-1">Products</p>
                    <p className="text-3xl font-black">{products.length}</p>
                 </div>
                 <div className="bg-white p-6 rounded-[24px] border border-gray-100">
                    <p className="text-[10px] font-black uppercase text-gray-400 mb-1">Bot Status</p>
                    <p className="text-3xl font-black text-green-500">ON</p>
                 </div>
              </div>
              
              <div className="bg-white rounded-[24px] border border-gray-100 overflow-hidden">
                 <div className="p-4 border-b border-gray-50 font-black text-sm bg-gray-50/50">Inventory Management</div>
                 <div className="divide-y divide-gray-50">
                    {products.map(p => (
                       <div key={p.id} className="p-3 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                             <img src={p.image} className="w-10 h-10 rounded-lg bg-gray-100 object-cover" />
                             <div>
                                <p className="font-bold text-xs line-clamp-1">{p.name_kh}</p>
                                <p className="text-[10px] text-gray-400">ID: {p.id}</p>
                             </div>
                          </div>
                          <button onClick={() => setProducts(products.filter(pr => pr.id !== p.id))} className="text-red-400 p-2">
                             <Trash2 size={16} />
                          </button>
                       </div>
                    ))}
                 </div>
              </div>
           </div>
        )}

      </main>

      {/* Dock */}
      <div className="fixed bottom-6 left-0 right-0 px-4 flex justify-center z-50 pointer-events-none">
        <nav className="bg-white/90 backdrop-blur-xl border border-gray-100 shadow-[0_10px_40px_rgba(0,0,0,0.1)] p-2 rounded-[32px] flex gap-2 pointer-events-auto">
          <button onClick={() => setView('home')} className={`p-4 rounded-[24px] transition-all ${view === 'home' ? 'bg-red-600 text-white shadow-lg shadow-red-200' : 'text-gray-400 hover:bg-gray-50'}`}>
            <Package size={20} />
          </button>
          <button onClick={() => setView('lucky-draw')} className={`p-4 rounded-[24px] transition-all ${view === 'lucky-draw' ? 'bg-red-600 text-white shadow-lg shadow-red-200' : 'text-gray-400 hover:bg-gray-50'}`}>
            <Gift size={20} />
          </button>
          <button onClick={() => setView('admin')} className={`p-4 rounded-[24px] transition-all ${view === 'admin' ? 'bg-red-600 text-white shadow-lg shadow-red-200' : 'text-gray-400 hover:bg-gray-50'}`}>
            <ShieldCheck size={20} />
          </button>
        </nav>
      </div>

    </div>
  );
}