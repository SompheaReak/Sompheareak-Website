import React, { useState, useEffect, useMemo } from 'react';
import { 
  ShoppingBag, 
  Search, 
  Menu, 
  X, 
  Plus, 
  Minus, 
  Trash2, 
  ChevronRight, 
  Home, 
  User, 
  Settings,
  Star,
  Zap,
  Tag
} from 'lucide-react';

// --- MOCK DATA BASED ON USER INVENTORY ---
const INITIAL_PRODUCTS = [
  { id: 1, name: "#OP01 One Piece - Sakazuki", price: 7500, category: "LEGO Anime", subcategory: "One Piece", image: "https://images.unsplash.com/photo-1593085512500-5d55148d6f0d?auto=format&fit=crop&q=80&w=400", stock: 12 },
  { id: 2, name: "#OP02 One Piece - Portgas D Ace", price: 6500, category: "LEGO Anime", subcategory: "One Piece", image: "https://images.unsplash.com/photo-1613292252537-be6ada176e0e?auto=format&fit=crop&q=80&w=400", stock: 8 },
  { id: 101, name: "NINJAGO S1 - DX Suit", price: 30000, category: "LEGO Ninjago", subcategory: "Season 1", image: "https://images.unsplash.com/photo-1560000593-0182ec647a06?auto=format&fit=crop&q=80&w=400", stock: 5 },
  { id: 3101, name: "Gym Bracelet - Matte Black", price: 5000, category: "Accessories", subcategory: "Gym Bracelet", image: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&q=80&w=400", stock: 25 },
  { id: 3401, name: "Italian Football Charm", price: 5000, category: "Italy Bracelet", subcategory: "Football", image: "https://images.unsplash.com/photo-1611085583191-a3b1a308964b?auto=format&fit=crop&q=80&w=400", stock: 100 },
  { id: 4001, name: "M416 Keychain - Gold", price: 6000, category: "Keychain", subcategory: "Gun Keychains", image: "https://images.unsplash.com/photo-1590483734724-383b853b317d?auto=format&fit=crop&q=80&w=400", stock: 15 },
  { id: 20001, name: "71049 F1 - Red Bull", price: 24000, category: "LEGO", subcategory: "Formula 1", image: "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&q=80&w=400", stock: 4 },
];

const CATEGORIES = ["All", "LEGO Ninjago", "LEGO Anime", "Accessories", "Italy Bracelet", "Keychain", "LEGO"];

const App = () => {
  const [products, setProducts] = useState(INITIAL_PRODUCTS);
  const [cart, setCart] = useState([]);
  const [activeTab, setActiveTab] = useState('shop'); // shop, admin
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // --- LOGIC ---
  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;
      const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [products, selectedCategory, searchQuery]);

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    // Optional: Auto-open cart or show toast
  };

  const updateQuantity = (id, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQty = Math.max(1, item.quantity + delta);
        return { ...item, quantity: newQty };
      }
      return item;
    }));
  };

  const removeFromCart = (id) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const totalCartValue = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // --- COMPONENTS ---
  const ProductCard = ({ product }) => (
    <div className="group bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden flex flex-col">
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        <img 
          src={product.image} 
          alt={product.name} 
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        {product.stock < 5 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white text-[10px] font-bold px-2 py-1 rounded-full">
            LOW STOCK
          </div>
        )}
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <span className="text-xs text-orange-600 font-semibold mb-1 uppercase tracking-wider">{product.subcategory}</span>
        <h3 className="text-sm font-bold text-gray-800 line-clamp-2 mb-2 leading-tight">
          {product.name}
        </h3>
        <div className="mt-auto pt-3 flex items-center justify-between">
          <div className="text-lg font-black text-gray-900">
            {product.price.toLocaleString()}៛
          </div>
          <button 
            onClick={() => addToCart(product)}
            className="p-2.5 bg-gray-900 text-white rounded-xl hover:bg-orange-600 transition-colors shadow-lg active:scale-95"
          >
            <Plus size={18} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F8F9FA] text-gray-900 font-sans selection:bg-orange-200">
      
      {/* HEADER */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-full"
            >
              <Menu size={24} />
            </button>
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab('shop')}>
              <div className="w-10 h-10 bg-orange-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-orange-200">
                <ShoppingBag size={20} weight="bold" />
              </div>
              <h1 className="text-xl font-black tracking-tight hidden sm:block">
                SOMPHEA <span className="text-orange-600">REAK</span>
              </h1>
            </div>
          </div>

          <div className="flex-grow max-w-md mx-8 hidden md:block">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input 
                type="text" 
                placeholder="Search products..."
                className="w-full bg-gray-100 border-none rounded-2xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 transition-all outline-none text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => setActiveTab(activeTab === 'shop' ? 'admin' : 'shop')}
              className="p-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-all"
              title="Admin Dashboard"
            >
              {activeTab === 'shop' ? <Settings size={22} /> : <Home size={22} />}
            </button>
            <button 
              onClick={() => setIsCartOpen(true)}
              className="relative p-2.5 bg-gray-900 text-white rounded-xl shadow-xl shadow-gray-200 hover:bg-gray-800 transition-all active:scale-95"
            >
              <ShoppingBag size={22} />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-white">
                  {cart.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* MOBILE MENU */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm lg:hidden">
          <div className="absolute left-0 top-0 bottom-0 w-4/5 max-w-xs bg-white p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold">Categories</h2>
              <button onClick={() => setIsMobileMenuOpen(false)} className="p-2 hover:bg-gray-100 rounded-full"><X /></button>
            </div>
            <div className="flex flex-col gap-2">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => {
                    setSelectedCategory(cat);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`text-left px-4 py-3 rounded-xl font-medium transition-all ${selectedCategory === cat ? 'bg-orange-50 text-orange-600' : 'hover:bg-gray-50'}`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SHOP VIEW */}
      {activeTab === 'shop' && (
        <main className="max-w-7xl mx-auto px-4 py-8">
          
          {/* HERO BANNER */}
          <div className="relative h-48 sm:h-64 rounded-3xl overflow-hidden mb-8 group">
            <img 
              src="https://images.unsplash.com/photo-1545558014-8692077e9b5c?auto=format&fit=crop&q=80&w=1200" 
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
              alt="Promo"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black/70 to-transparent flex flex-col justify-center p-8 sm:p-12">
              <h2 className="text-white text-3xl sm:text-4xl font-black mb-2">NEW ARRIVALS</h2>
              <p className="text-gray-200 text-sm sm:text-base max-w-sm mb-6">Discover the latest collection of LEGO Ninjago and Custom Italian Bracelets.</p>
              <button className="bg-orange-600 text-white font-bold py-2.5 px-6 rounded-xl w-fit hover:bg-orange-700 transition-colors shadow-lg shadow-orange-900/20">
                Shop Now
              </button>
            </div>
          </div>

          {/* CATEGORY TABS (Desktop) */}
          <div className="flex items-center gap-2 overflow-x-auto pb-6 scrollbar-hide mb-4">
            {CATEGORIES.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-5 py-2.5 rounded-2xl whitespace-nowrap text-sm font-bold transition-all border ${
                  selectedCategory === cat 
                  ? 'bg-gray-900 text-white border-gray-900 shadow-xl shadow-gray-200' 
                  : 'bg-white text-gray-500 border-gray-100 hover:border-gray-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-black">{selectedCategory} Collections</h2>
            <p className="text-sm text-gray-500 font-medium">{filteredProducts.length} Items</p>
          </div>

          {/* PRODUCT GRID - Modern 4 Column Setup */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {filteredProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          
          {filteredProducts.length === 0 && (
            <div className="py-20 text-center flex flex-col items-center">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 mb-4">
                <Search size={40} />
              </div>
              <h3 className="text-xl font-bold mb-1">No products found</h3>
              <p className="text-gray-500">Try adjusting your search or category filter.</p>
            </div>
          )}
        </main>
      )}

      {/* ADMIN VIEW (Simplified) */}
      {activeTab === 'admin' && (
        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-black">Inventory Manager</h2>
            <button 
              className="bg-green-600 text-white px-4 py-2 rounded-xl font-bold flex items-center gap-2 hover:bg-green-700"
              onClick={() => alert('New product flow triggered')}
            >
              <Plus size={20} /> Add Product
            </button>
          </div>
          <div className="bg-white rounded-3xl border border-gray-200 overflow-hidden shadow-sm">
            <table className="w-full text-left">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Product</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Stock</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {products.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 flex items-center gap-3">
                      <img src={p.image} className="w-10 h-10 rounded-lg object-cover" />
                      <div>
                        <div className="text-sm font-bold text-gray-900">{p.name}</div>
                        <div className="text-xs text-gray-400">{p.category}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-sm font-bold ${p.stock < 10 ? 'text-red-600' : 'text-green-600'}`}>{p.stock}</span>
                    </td>
                    <td className="px-6 py-4 text-sm font-bold">{p.price.toLocaleString()}៛</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <button className="text-blue-600 hover:text-blue-800"><ChevronRight size={20} /></button>
                        <button className="text-red-600 hover:text-red-800"><Trash2 size={20} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      )}

      {/* CART DRAWER */}
      {isCartOpen && (
        <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
            <div className="p-6 border-b flex items-center justify-between">
              <h2 className="text-2xl font-black">Your Cart</h2>
              <button onClick={() => setIsCartOpen(false)} className="p-2 hover:bg-gray-100 rounded-full"><X /></button>
            </div>

            <div className="flex-grow overflow-y-auto p-6 space-y-6">
              {cart.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-50">
                  <ShoppingBag size={80} className="mb-4" />
                  <p className="text-xl font-bold">Your cart is empty</p>
                  <button 
                    onClick={() => setIsCartOpen(false)}
                    className="mt-4 text-orange-600 font-bold"
                  >
                    Start shopping →
                  </button>
                </div>
              ) : (
                cart.map(item => (
                  <div key={item.id} className="flex gap-4">
                    <img src={item.image} className="w-20 h-20 rounded-xl object-cover bg-gray-100" />
                    <div className="flex-grow">
                      <h4 className="font-bold text-sm leading-tight mb-1">{item.name}</h4>
                      <div className="text-orange-600 font-black mb-3">{item.price.toLocaleString()}៛</div>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center border rounded-lg bg-gray-50">
                          <button onClick={() => updateQuantity(item.id, -1)} className="p-1.5 hover:bg-gray-200 rounded-l-lg"><Minus size={14} /></button>
                          <span className="w-8 text-center text-sm font-bold">{item.quantity}</span>
                          <button onClick={() => updateQuantity(item.id, 1)} className="p-1.5 hover:bg-gray-200 rounded-r-lg"><Plus size={14} /></button>
                        </div>
                        <button onClick={() => removeFromCart(item.id)} className="text-red-500 hover:bg-red-50 p-2 rounded-lg transition-colors"><Trash2 size={16} /></button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {cart.length > 0 && (
              <div className="p-6 bg-gray-50 border-t space-y-4">
                <div className="flex items-center justify-between text-gray-500">
                  <span>Subtotal</span>
                  <span className="font-bold">{totalCartValue.toLocaleString()}៛</span>
                </div>
                <div className="flex items-center justify-between text-gray-500">
                  <span>Delivery</span>
                  <span className="text-green-600 font-bold">FREE</span>
                </div>
                <div className="flex items-center justify-between text-xl font-black border-t pt-4">
                  <span>Total</span>
                  <span>{totalCartValue.toLocaleString()}៛</span>
                </div>
                <button 
                  onClick={() => alert('Order details sent to Telegram!')}
                  className="w-full bg-orange-600 text-white font-black py-4 rounded-2xl shadow-xl shadow-orange-200 hover:bg-orange-700 transition-all active:scale-95"
                >
                  Checkout Now
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="bg-white border-t border-gray-200 py-12 mt-12">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center text-white">
                <ShoppingBag size={16} />
              </div>
              <h1 className="text-lg font-black tracking-tight">SOMPHEA <span className="text-orange-600">REAK</span></h1>
            </div>
            <p className="text-gray-500 max-w-sm mb-6">Your premium destination for unique toys, anime collections, and customized jewelry in Cambodia.</p>
            <div className="flex gap-4">
              <div className="w-10 h-10 bg-gray-100 rounded-full hover:bg-orange-100 transition-colors cursor-pointer" />
              <div className="w-10 h-10 bg-gray-100 rounded-full hover:bg-orange-100 transition-colors cursor-pointer" />
              <div className="w-10 h-10 bg-gray-100 rounded-full hover:bg-orange-100 transition-colors cursor-pointer" />
            </div>
          </div>
          <div>
            <h4 className="font-black mb-4 uppercase text-xs tracking-widest text-gray-400">Quick Links</h4>
            <ul className="space-y-2 text-sm font-medium text-gray-600">
              <li className="hover:text-orange-600 cursor-pointer">Best Sellers</li>
              <li className="hover:text-orange-600 cursor-pointer">New Arrivals</li>
              <li className="hover:text-orange-600 cursor-pointer">Order Tracking</li>
              <li className="hover:text-orange-600 cursor-pointer">Privacy Policy</li>
            </ul>
          </div>
          <div>
            <h4 className="font-black mb-4 uppercase text-xs tracking-widest text-gray-400">Support</h4>
            <ul className="space-y-2 text-sm font-medium text-gray-600">
              <li className="hover:text-orange-600 cursor-pointer">Help Center</li>
              <li className="hover:text-orange-600 cursor-pointer">Contact Us</li>
              <li className="hover:text-orange-600 cursor-pointer">Telegram Bot</li>
              <li className="hover:text-orange-600 cursor-pointer">Shipping Rates</li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 mt-12 pt-8 border-t text-center text-xs font-bold text-gray-400 uppercase tracking-widest">
          © 2024 Somphea Reak Shop. All rights reserved.
        </div>
      </footer>

    </div>
  );
};

export default App;

