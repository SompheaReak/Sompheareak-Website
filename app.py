<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Somphea Reak Shop - Preview</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        @media (min-width: 768px) { .product-grid { grid-template-columns: repeat(4, 1fr); gap: 24px; } }
        .cart-drawer { transition: transform 0.3s ease-in-out; }
        .cart-closed { transform: translateX(100%); }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">

    <!-- NAVIGATION -->
    <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100 px-4 py-3">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="bg-orange-600 text-white p-2 rounded-xl shadow-lg shadow-orange-200">
                    <i class="fa-solid fa-shop"></i>
                </div>
                <h1 class="font-extrabold text-lg tracking-tight">
                    SOMPHEA <span class="text-orange-600">REAK</span>
                </h1>
            </div>
            
            <div class="flex items-center gap-3">
                <button class="p-2 text-gray-500 hover:bg-gray-100 rounded-full"><i class="fa-solid fa-magnifying-glass"></i></button>
                <button onclick="toggleCart()" class="relative p-2.5 bg-gray-900 text-white rounded-xl shadow-xl shadow-gray-200 active:scale-95 transition-transform">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <span id="cart-count" class="absolute -top-1 -right-1 bg-orange-500 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-white">0</span>
                </button>
            </div>
        </div>
    </nav>

    <!-- MAIN CONTENT -->
    <main class="max-w-7xl mx-auto px-4 pb-20">
        
        <!-- CATEGORY SCROLLER -->
        <div class="flex gap-2 overflow-x-auto py-6 scrollbar-hide">
            <button class="px-5 py-2.5 bg-gray-900 text-white rounded-2xl text-sm font-bold shadow-xl shadow-gray-200 whitespace-nowrap">All</button>
            <button class="px-5 py-2.5 bg-white text-gray-500 border border-gray-100 rounded-2xl text-sm font-bold whitespace-nowrap hover:border-gray-300">LEGO Ninjago</button>
            <button class="px-5 py-2.5 bg-white text-gray-500 border border-gray-100 rounded-2xl text-sm font-bold whitespace-nowrap hover:border-gray-300">LEGO Anime</button>
            <button class="px-5 py-2.5 bg-white text-gray-500 border border-gray-100 rounded-2xl text-sm font-bold whitespace-nowrap hover:border-gray-300">Accessories</button>
            <button class="px-5 py-2.5 bg-white text-gray-500 border border-gray-100 rounded-2xl text-sm font-bold whitespace-nowrap hover:border-gray-300">Keychain</button>
        </div>

        <!-- HERO SECTION -->
        <div class="relative rounded-3xl overflow-hidden mb-8 h-44 bg-gradient-to-br from-orange-500 to-red-600">
            <div class="absolute inset-0 opacity-20">
                <svg width="100%" height="100%"><pattern id="pattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="1" fill="white"/></pattern><rect width="100%" height="100%" fill="url(#pattern)"/></svg>
            </div>
            <div class="relative h-full flex flex-col justify-center px-8">
                <span class="text-orange-100 text-[10px] font-bold tracking-[0.2em] mb-1">NEW SEASON 2024</span>
                <h2 class="text-white text-2xl font-black leading-tight mb-3">NINJAGO <br>COLLECTION</h2>
                <button class="bg-white text-orange-600 text-xs font-bold py-2 px-5 rounded-full shadow-lg w-fit active:scale-95 transition-transform">Explore Now</button>
            </div>
            <div class="absolute right-[-20px] bottom-[-20px] opacity-10 transform rotate-12">
                <i class="fa-solid fa-dragon text-[160px] text-white"></i>
            </div>
        </div>

        <!-- PRODUCT GRID -->
        <div class="flex items-center justify-between mb-6 px-1">
            <h3 class="text-lg font-black tracking-tight">Top Sellers</h3>
            <span class="text-xs font-bold text-gray-400">102 Items</span>
        </div>

        <div class="product-grid" id="product-list">
            <!-- Products will be injected by JS -->
        </div>

    </main>

    <!-- BOTTOM TAB BAR (MOBILE ONLY) -->
    <div class="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-100 px-8 py-3 flex justify-between md:hidden z-40">
        <button class="text-orange-600 flex flex-col items-center gap-1"><i class="fa-solid fa-house text-lg"></i><span class="text-[10px] font-bold">Home</span></button>
        <button class="text-gray-400 flex flex-col items-center gap-1"><i class="fa-solid fa-gamepad text-lg"></i><span class="text-[10px] font-bold">Game</span></button>
        <button class="text-gray-400 flex flex-col items-center gap-1"><i class="fa-solid fa-heart text-lg"></i><span class="text-[10px] font-bold">Saved</span></button>
        <button class="text-gray-400 flex flex-col items-center gap-1"><i class="fa-solid fa-user text-lg"></i><span class="text-[10px] font-bold">Profile</span></button>
    </div>

    <!-- CART DRAWER -->
    <div id="cart-drawer" class="fixed inset-0 z-[60] cart-drawer cart-closed pointer-events-none">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm pointer-events-auto" onclick="toggleCart()"></div>
        <div class="absolute top-0 right-0 bottom-0 w-full max-w-sm bg-white pointer-events-auto flex flex-col shadow-2xl">
            <div class="p-6 border-b flex items-center justify-between bg-gray-50">
                <h2 class="text-xl font-black">Your Cart</h2>
                <button onclick="toggleCart()" class="p-2 hover:bg-gray-200 rounded-full"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="cart-items" class="flex-grow overflow-y-auto p-6 space-y-4">
                <div class="h-full flex flex-col items-center justify-center text-gray-400">
                    <i class="fa-solid fa-cart-shopping text-5xl mb-4"></i>
                    <p class="font-bold">Your cart is empty</p>
                </div>
            </div>
            <div class="p-6 border-t space-y-4">
                <div class="flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span id="cart-total" class="text-orange-600">0៛</span>
                </div>
                <button class="w-full bg-gray-900 text-white py-4 rounded-2xl font-black shadow-xl shadow-gray-200 active:scale-95 transition-transform">CHECKOUT NOW</button>
            </div>
        </div>
    </div>

    <script>
        const products = [
            { id: 1, name: "#OP01 One Piece - Sakazuki", price: 7500, image: "https://images.unsplash.com/photo-1593085512500-5d55148d6f0d?auto=format&fit=crop&q=80&w=400", sub: "One Piece" },
            { id: 2, name: "#OP02 One Piece - Portgas D Ace", price: 6500, image: "https://images.unsplash.com/photo-1613292252537-be6ada176e0e?auto=format&fit=crop&q=80&w=400", sub: "One Piece" },
            { id: 101, name: "NINJAGO Season 1 - DX Suit", price: 30000, image: "https://images.unsplash.com/photo-1560000593-0182ec647a06?auto=format&fit=crop&q=80&w=400", sub: "Lego Ninjago" },
            { id: 3101, name: "Gym Bracelet - Matte Black", price: 5000, image: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&q=80&w=400", sub: "Gym Bracelet" },
            { id: 2001, name: "WWII - Big Gun", price: 3500, image: "https://images.unsplash.com/photo-1590483734724-383b853b317d?auto=format&fit=crop&q=80&w=400", sub: "Lego WWII" },
            { id: 6, name: "#OP06 One Piece - Shanks", price: 7000, image: "https://images.unsplash.com/photo-1613292252537-be6ada176e0e?auto=format&fit=crop&q=80&w=400", sub: "One Piece" }
        ];

        let cart = [];

        function renderProducts() {
            const list = document.getElementById('product-list');
            list.innerHTML = products.map(p => `
                <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm flex flex-col group">
                    <div class="relative aspect-square overflow-hidden bg-gray-50">
                        <img src="${p.image}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                    </div>
                    <div class="p-3 flex flex-col flex-grow">
                        <span class="text-[9px] font-extrabold text-orange-600 uppercase tracking-widest mb-1">${p.sub}</span>
                        <h4 class="text-xs font-bold text-gray-800 line-clamp-2 mb-2 leading-tight">${p.name}</h4>
                        <div class="mt-auto pt-2 flex items-center justify-between">
                            <span class="font-black text-sm text-gray-900">${p.price.toLocaleString()}៛</span>
                            <button onclick="addToCart(${p.id})" class="bg-gray-900 text-white w-8 h-8 rounded-lg flex items-center justify-center shadow-lg shadow-gray-200 active:scale-90 transition-transform">
                                <i class="fa-solid fa-plus text-xs"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function addToCart(id) {
            const product = products.find(p => p.id === id);
            cart.push(product);
            document.getElementById('cart-count').innerText = cart.length;
            updateCartUI();
            
            // Show a simple toast simulation
            const btn = event.currentTarget;
            btn.innerHTML = '<i class="fa-solid fa-check text-xs"></i>';
            btn.classList.replace('bg-gray-900', 'bg-green-600');
            setTimeout(() => {
                btn.innerHTML = '<i class="fa-solid fa-plus text-xs"></i>';
                btn.classList.replace('bg-green-600', 'bg-gray-900');
            }, 1000);
        }

        function updateCartUI() {
            const itemsDiv = document.getElementById('cart-items');
            const totalSpan = document.getElementById('cart-total');
            
            if (cart.length === 0) {
                itemsDiv.innerHTML = '<div class="h-full flex flex-col items-center justify-center text-gray-400"><i class="fa-solid fa-cart-shopping text-5xl mb-4"></i><p class="font-bold">Your cart is empty</p></div>';
                totalSpan.innerText = '0៛';
                return;
            }

            let total = 0;
            itemsDiv.innerHTML = cart.map((item, index) => {
                total += item.price;
                return `
                    <div class="flex gap-4 border-b border-gray-50 pb-4">
                        <img src="${item.image}" class="w-16 h-16 rounded-xl object-cover">
                        <div class="flex-grow">
                            <h5 class="text-xs font-bold leading-tight mb-1">${item.name}</h5>
                            <div class="text-orange-600 font-black text-sm">${item.price.toLocaleString()}៛</div>
                        </div>
                        <button onclick="removeFromCart(${index})" class="text-gray-300 hover:text-red-500"><i class="fa-solid fa-trash-can"></i></button>
                    </div>
                `;
            }).join('');
            totalSpan.innerText = total.toLocaleString() + '៛';
        }

        function removeFromCart(index) {
            cart.splice(index, 1);
            document.getElementById('cart-count').innerText = cart.length;
            updateCartUI();
        }

        function toggleCart() {
            const drawer = document.getElementById('cart-drawer');
            drawer.classList.toggle('cart-closed');
        }

        renderProducts();
    </script>
</body>
</html>

