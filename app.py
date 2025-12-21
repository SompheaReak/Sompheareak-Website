import React, { useState, useEffect } from 'react';
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
  Truck
} from 'lucide-react';

/**
 * SIMULATED DATA FROM YOUR FLASK CODE
 */
const ADMIN_USERNAME = 'AdminSompheaReakVitou';
const ADMIN_PASSWORD = 'Thesong_Admin@2022?!$';

const SUBCATEGORIES_MAP = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["Dragon Rising","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5"],
    "LEGO Anime": ["One Piece","Demon Slayer"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece","Lego WWII", "Lego ទាហាន"],
    "Italy Bracelet": ["All","Football","Gem","Flag","Chain"],
    "Lucky Draw": ["/lucky-draw"], 
};

const MOCK_PRODUCTS = [
  { id: 1, name_kh: "LEGO One Piece Luffy", price: 6500, image: "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400", categories: ["LEGO Anime", "Toy"], subcategory: ["One Piece"] },
  { id: 2, name_kh: "Dragon Bracelet Luxury", price: 12000, image: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400", categories: ["Accessories"], subcategory: ["Dragon Bracelet"] },
  { id: 3, name_kh: "Gym Bracelet Pro", price: 5000, image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400", categories: ["Accessories"], subcategory: ["Gym Bracelet"] },
  { id: 4, name_kh: "LEGO Ninjago Dragon", price: 8500, image: "https://images.unsplash.com/photo-1560000593-06674681330c?w=400", categories: ["LEGO Ninjago"], subcategory: ["Dragon Rising"] }
];

export default function App() {
  const [view, setView] = useState('home');
  const [activeCategory, setActiveCategory] = useState('Hot Sale');
  const [activeSub, setActiveSub] = useState(null);
  const [cart, setCart] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminInput, setAdminInput] = useState({ user: '', pass: '' });
  const [checkoutStatus, setCheckoutStatus] = useState(null);

  // Filter products based on Flask logic
  const filteredProducts = MOCK_PRODUCTS.filter(p => {
    if (activeCategory === 'Hot Sale') return true;
    if (activeSub) return p.subcategory.includes(activeSub);
    return p.categories.includes(activeCategory);
  });

  const addToCart = (product) => {
    setCart([...cart, { ...product, cartId: Date.now() }]);
  };

  const handleCheckout = (e) => {
    e.preventDefault();
    setCheckoutStatus('loading');
    
    // Simulate your notify_telegram logic
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
      alert("Invalid Admin Credentials");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 font-sans pb-20">
      {/* Header */}
      <nav className="bg-white border-b sticky top-0 z-50 px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => setIsMenuOpen(true)} className="p-2 hover:bg-gray-100 rounded-lg">
            <Menu size={24} />
          </button>
          <h1 onClick={() => setView('home')} className="text-xl font-bold text-red-600 tracking-tighter cursor-pointer">
            THESONG STORE
          </h1>
        </div>

        <div className="flex items-center gap-4">
          <button onClick={() => setView('cart')} className="relative p-2 bg-slate-900 text-white rounded-full">
            <ShoppingBag size={20} />
            {cart.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-[10px] w-5 h-5 flex items-center justify-center rounded-full border-2 border-white font-bold">
                {cart.length}
              </span>
            )}
          </button>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-4">
        {view === 'home' && (
          <div className="space-y-6">
            {/* Category Navigation (Flask: subcategories_map) */}
            <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
              {Object.keys(SUBCATEGORIES_MAP).map(cat => (
                <button
                  key={cat}
                  onClick={() => {
                    if (cat === 'Lucky Draw') {
                      setView('lucky-draw');
                    } else {
                      setActiveCategory(cat);
                      setActiveSub(null);
                    }
                  }}
                  className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap transition-colors ${activeCategory === cat ? 'bg-red-600 text-white' : 'bg-white border text-gray-600'}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Sub-Category Navigation */}
            {SUBCATEGORIES_MAP[activeCategory] && SUBCATEGORIES_MAP[activeCategory].length > 0 && (
              <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                {SUBCATEGORIES_MAP[activeCategory].map(sub => (
                  <button
                    key={sub}
                    onClick={() => setActiveSub(sub)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${activeSub === sub ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-500'}`}
                  >
                    {sub}
                  </button>
                ))}
              </div>
            )}

            {/* Product Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {filteredProducts.map(p => (
                <div key={p.id} className="bg-white rounded-2xl overflow-hidden border shadow-sm group">
                  <div className="aspect-square bg-gray-100 relative">
                    <img src={p.image} className="w-full h-full object-cover" alt={p.name_kh} />
                  </div>
                  <div className="p-3">
                    <h3 className="font-bold text-sm mb-1">{p.name_kh}</h3>
                    <p className="text-red-600 font-bold mb-3">{p.price.toLocaleString()}៛</p>
                    <button 
                      onClick={() => addToCart(p)}
                      className="w-full bg-slate-100 group-hover:bg-red-600 group-hover:text-white py-2 rounded-xl text-[10px] font-black uppercase transition-all"
                    >
                      បន្ថែមទៅកន្ត្រក
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'cart' && (
          <div className="animate-in slide-in-from-bottom-4">
            <h2 className="text-2xl font-bold mb-6">កន្ត្រកទំនិញ ({cart.length})</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                {cart.map((item, idx) => (
                  <div key={idx} className="bg-white p-4 rounded-2xl border flex gap-4">
                    <img src={item.image} className="w-16 h-16 rounded-xl object-cover" />
                    <div className="flex-1">
                      <h4 className="font-bold text-sm">{item.name_kh}</h4>
                      <p className="text-red-600 font-bold">{item.price.toLocaleString()}៛</p>
                    </div>
                    <button onClick={() => setCart(cart.filter((_, i) => i !== idx))} className="text-gray-300">
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
                {cart.length === 0 && <p className="text-gray-400 py-10 text-center">Your cart is empty.</p>}
              </div>

              <div className="bg-white p-6 rounded-3xl border shadow-sm h-fit">
                <h3 className="font-bold text-lg mb-4">ការទូទាត់ប្រាក់</h3>
                <form onSubmit={handleCheckout} className="space-y-4">
                  <input placeholder="ឈ្មោះរបស់អ្នក" required className="w-full bg-gray-50 border p-3 rounded-xl text-sm" />
                  <input placeholder="លេខទូរស័ព្ទ" required className="w-full bg-gray-50 border p-3 rounded-xl text-sm" />
                  <select className="w-full bg-gray-50 border p-3 rounded-xl text-sm">
                    <option value="door">ដឹកដល់ផ្ទះ (7,000៛)</option>
                    <option value="vet">វីរៈប៊ុនថាំ (5,000៛)</option>
                  </select>
                  <div className="border-t pt-4 flex justify-between font-bold text-lg">
                    <span>សរុប:</span>
                    <span className="text-red-600">
                      {cart.reduce((sum, item) => sum + item.price, 0).toLocaleString()}៛
                    </span>
                  </div>
                  <button 
                    disabled={cart.length === 0 || checkoutStatus === 'loading'}
                    className="w-full bg-red-600 text-white py-4 rounded-2xl font-bold shadow-lg shadow-red-100 disabled:opacity-50"
                  >
                    {checkoutStatus === 'loading' ? 'កំពុងផ្ញើទៅ Telegram...' : 'បញ្ជាទិញឥឡូវនេះ'}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {view === 'lucky-draw' && (
          <div className="bg-white p-10 rounded-[40px] border shadow-sm text-center">
            <Gift className="mx-auto text-red-500 mb-6" size={60} />
            <h2 className="text-3xl font-bold mb-4">Minifigure Lucky Draw</h2>
            <p className="text-gray-500 mb-8">Win rare LEGO minifigures for only 5,000៛!</p>
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-3xl p-12 text-gray-300 font-bold text-4xl mb-8">
              ? ? ?
            </div>
            <button className="bg-red-600 text-white px-10 py-4 rounded-2xl font-bold text-xl shadow-xl shadow-red-200">
              Spin to Win
            </button>
            <button onClick={() => setView('home')} className="block mx-auto mt-6 text-gray-400 font-bold underline">
              Back to Store
            </button>
          </div>
        )}

        {view === 'admin-login' && !isAdmin && (
          <div className="max-w-sm mx-auto pt-20">
            <div className="bg-white p-8 rounded-3xl border shadow-xl text-center">
              <Lock className="mx-auto text-gray-200 mb-4" size={40} />
              <h2 className="text-xl font-bold mb-6">Admin Panel</h2>
              <form onSubmit={handleAdminLogin} className="space-y-4">
                <input 
                  placeholder="Username" 
                  className="w-full bg-gray-50 border p-3 rounded-xl text-sm"
                  value={adminInput.user}
                  onChange={e => setAdminInput({...adminInput, user: e.target.value})}
                />
                <input 
                  type="password" 
                  placeholder="Password" 
                  className="w-full bg-gray-50 border p-3 rounded-xl text-sm"
                  value={adminInput.pass}
                  onChange={e => setAdminInput({...adminInput, pass: e.target.value})}
                />
                <button className="w-full bg-slate-900 text-white py-3 rounded-xl font-bold">Login</button>
              </form>
            </div>
          </div>
        )}

        {isAdmin && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Dashboard</h2>
              <button onClick={() => setIsAdmin(false)} className="text-red-500 font-bold">Logout</button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white p-6 rounded-2xl border text-center">
                <p className="text-xs text-gray-400 font-bold uppercase">Products</p>
                <p className="text-2xl font-bold">{MOCK_PRODUCTS.length}</p>
              </div>
              <div className="bg-white p-6 rounded-2xl border text-center">
                <p className="text-xs text-gray-400 font-bold uppercase">Bot Status</p>
                <p className="text-2xl font-bold text-green-500">Active</p>
              </div>
              <div className="bg-white p-6 rounded-2xl border text-center">
                <p className="text-xs text-gray-400 font-bold uppercase">IP Bans</p>
                <p className="text-2xl font-bold">2</p>
              </div>
            </div>
            <div className="bg-white border rounded-2xl overflow-hidden">
               <div className="p-4 border-b font-bold bg-gray-50">Manage Products</div>
               <div className="divide-y">
                 {MOCK_PRODUCTS.map(p => (
                   <div key={p.id} className="p-4 flex items-center justify-between">
                     <div className="flex items-center gap-3">
                       <img src={p.image} className="w-10 h-10 rounded-lg object-cover" />
                       <span className="text-sm font-bold">{p.name_kh}</span>
                     </div>
                     <button className="text-red-500"><Trash2 size={16} /></button>
                   </div>
                 ))}
               </div>
            </div>
          </div>
        )}

        {checkoutStatus === 'success' && (
          <div className="fixed inset-0 bg-white z-[100] flex flex-col items-center justify-center p-6 text-center animate-in fade-in zoom-in">
            <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6">
              <CheckCircle size={40} />
            </div>
            <h2 className="text-3xl font-bold mb-4">ការបញ្ជាទិញជោគជ័យ!</h2>
            <p className="text-gray-500 mb-10 max-w-xs">ក្រុមការងារយើងនឹងទាក់ទងទៅអ្នកក្នុងពេលឆាប់ៗតាមរយៈ Telegram ។</p>
            <button onClick={() => {setCheckoutStatus(null); setView('home');}} className="w-full max-w-xs bg-slate-900 text-white py-4 rounded-2xl font-bold">រួចរាល់</button>
          </div>
        )}
      </main>

      {/* Footer Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-md border-t px-6 py-3 flex justify-around items-center z-40">
        <button onClick={() => setView('home')} className={`flex flex-col items-center ${view === 'home' ? 'text-red-600' : 'text-gray-400'}`}>
          <Package size={20} />
          <span className="text-[10px] font-bold mt-1">Store</span>
        </button>
        <button onClick={() => setView('lucky-draw')} className={`flex flex-col items-center ${view === 'lucky-draw' ? 'text-red-600' : 'text-gray-400'}`}>
          <Gift size={20} />
          <span className="text-[10px] font-bold mt-1">Lucky Draw</span>
        </button>
        <button onClick={() => setView('admin-login')} className={`flex flex-col items-center ${view === 'admin-login' || isAdmin ? 'text-red-600' : 'text-gray-400'}`}>
          <ShieldCheck size={20} />
          <span className="text-[10px] font-bold mt-1">Admin</span>
        </button>
      </div>

      {/* Side Menu */}
      <div className={`fixed inset-0 bg-black/40 z-[60] transition-opacity ${isMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
        <div className={`w-72 bg-white h-full transition-transform duration-300 ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-6 border-b flex justify-between items-center">
            <h2 className="font-bold text-xl">Categories</h2>
            <button onClick={() => setIsMenuOpen(false)} className="p-2"><X size={20} /></button>
          </div>
          <div className="p-4 space-y-1">
            {Object.keys(SUBCATEGORIES_MAP).map(cat => (
              <button 
                key={cat}
                onClick={() => {setActiveCategory(cat); setIsMenuOpen(false); setView('home');}}
                className="w-full text-left p-3 rounded-xl hover:bg-gray-50 font-bold text-gray-600 flex items-center justify-between"
              >
                {cat}
                <span className="text-gray-300"><Search size={14} /></span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

