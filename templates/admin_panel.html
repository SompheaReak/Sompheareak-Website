<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Somphea Reak - Admin Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f9fafb; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-slate-900">

    <!-- SIDEBAR NAV -->
    <aside class="w-72 bg-white border-r flex flex-col h-full z-50">
        <div class="p-8 border-b">
            <h1 class="text-xl font-black uppercase italic tracking-tighter">Somphea <span class="text-orange-600">Reak</span></h1>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Admin Dashboard</p>
        </div>

        <nav class="flex-grow overflow-y-auto py-6 no-scrollbar">
            <p class="px-8 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Quick Links</p>
            <a href="/admin/panel" class="flex items-center gap-3 px-8 py-3 text-sm font-bold text-orange-600 bg-orange-50 border-r-4 border-orange-600">
                <i class="fa-solid fa-layer-group"></i> Inventory Manager
            </a>
            <a href="/admin/add-product" class="flex items-center gap-3 px-8 py-3 text-sm font-bold text-slate-500 hover:bg-slate-50">
                <i class="fa-solid fa-plus-circle"></i> Add New Product
            </a>
            <div class="mt-8">
                <p class="px-8 text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Categories</p>
                {% for category in grouped.keys() %}
                <a href="#cat-{{ loop.index }}" class="flex items-center justify-between px-8 py-2 text-xs font-bold text-slate-500 hover:text-orange-600">
                    <span>{{ category }}</span>
                    <span class="bg-slate-100 px-2 py-0.5 rounded-full text-[9px]">{{ grouped[category]|length }}</span>
                </a>
                {% endfor %}
            </div>
        </nav>

        <div class="p-6 border-t bg-slate-50/50">
            <a href="/admin/logout" class="flex items-center gap-3 text-sm font-bold text-red-500 hover:text-red-600">
                <i class="fa-solid fa-power-off"></i> Sign Out
            </a>
        </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-grow flex flex-col h-full bg-slate-50/30 overflow-hidden">
        
        <header class="bg-white/80 backdrop-blur-md border-b px-10 py-6 flex justify-between items-center sticky top-0 z-40">
            <div>
                <h2 class="text-2xl font-black tracking-tight">Inventory Console</h2>
                <p class="text-xs font-semibold text-slate-400 mt-1">Update stock levels in real-time</p>
            </div>
            <div class="flex items-center gap-4">
                <div class="relative">
                    <i class="fa-solid fa-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
                    <input type="text" id="charmSearch" placeholder="Search product..." 
                           class="bg-slate-100 border-none rounded-2xl pl-12 pr-6 py-3 text-sm font-bold w-64 focus:ring-2 focus:ring-orange-500 transition-all outline-none">
                </div>
                <a href="/" class="text-xs font-black uppercase text-slate-400 hover:text-slate-600">View Shop</a>
            </div>
        </header>

        <div class="flex-grow overflow-y-auto px-10 py-8 no-scrollbar pb-32">
            
            <!-- STATS -->
            <section class="grid grid-cols-4 gap-6 mb-12">
                <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-5">
                    <div class="w-14 h-14 bg-orange-50 text-orange-600 rounded-2xl flex items-center justify-center text-xl"><i class="fa-solid fa-box"></i></div>
                    <div><p class="text-[10px] font-black text-slate-400 uppercase">Total SKU</p><p class="text-xl font-black">{{ stats.total_items }}</p></div>
                </div>
                <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-5">
                    <div class="w-14 h-14 bg-red-50 text-red-600 rounded-2xl flex items-center justify-center text-xl"><i class="fa-solid fa-circle-xmark"></i></div>
                    <div><p class="text-[10px] font-black text-slate-400 uppercase">Out of Stock</p><p class="text-xl font-black text-red-600">{{ stats.out_of_stock }}</p></div>
                </div>
                <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-5">
                    <div class="w-14 h-14 bg-yellow-50 text-yellow-600 rounded-2xl flex items-center justify-center text-xl"><i class="fa-solid fa-bolt"></i></div>
                    <div><p class="text-[10px] font-black text-slate-400 uppercase">Low Stock</p><p class="text-xl font-black text-yellow-600">{{ stats.low_stock }}</p></div>
                </div>
                <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-5">
                    <div class="w-14 h-14 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center text-xl"><i class="fa-solid fa-money-bill-wave"></i></div>
                    <div><p class="text-[10px] font-black text-slate-400 uppercase">Inv. Value</p><p class="text-xl font-black">{{ stats.total_value }}៛</p></div>
                </div>
            </section>

            {% for subcategory, items in grouped.items() %}
            <div id="cat-{{ loop.index }}" class="mb-16 scroll-mt-32">
                <div class="flex items-center gap-4 mb-8">
                    <h3 class="text-lg font-black uppercase italic tracking-tighter text-slate-800">{{ subcategory }}</h3>
                    <div class="h-[1px] bg-slate-200 flex-grow"></div>
                    <span class="text-[10px] font-black text-slate-400 bg-white border px-4 py-1.5 rounded-full uppercase">{{ items|length }} Items</span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
                    {% for p in items %}
                    <div class="charm-card bg-white rounded-[2rem] p-4 border border-slate-100 shadow-sm hover:shadow-xl transition-all group" data-name="{{ p.name_kh }}">
                        <div class="relative aspect-square mb-4 overflow-hidden rounded-2xl bg-slate-50">
                            <img src="{{ p.image }}" class="w-full h-full object-cover group-hover:scale-110 transition-transform">
                            {% if p.stock <= 0 %}
                            <div class="absolute inset-0 bg-red-600/60 backdrop-blur-sm flex items-center justify-center">
                                <span class="text-white font-black text-[10px] uppercase border border-white px-2 py-1">Sold Out</span>
                            </div>
                            {% endif %}
                        </div>
                        <p class="text-[10px] font-black text-slate-800 truncate uppercase mb-4">{{ p.name_kh }}</p>
                        <div class="flex items-center gap-2">
                            <input type="number" value="{{ p.stock }}" id="input-{{ p.id }}"
                                   class="w-full bg-slate-100 border-none rounded-xl py-2 px-3 text-xs font-black text-center outline-none focus:ring-1 focus:ring-orange-500">
                            <button onclick="saveStock({{ p.id }})" 
                                    class="bg-slate-900 text-white w-9 h-9 rounded-xl flex items-center justify-center active:scale-90 transition-all">
                                <i class="fa-solid fa-check text-[10px]"></i>
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <script>
        // Real-time Search
        document.getElementById('charmSearch').addEventListener('input', function(e) {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.charm-card').forEach(card => {
                const name = card.dataset.name.toLowerCase();
                card.style.display = name.includes(term) ? 'block' : 'none';
            });
        });

        // Stock Update
        async function saveStock(id) {
            const amount = document.getElementById('input-' + id).value;
            const btn = event.currentTarget;
            btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i>';

            try {
                const res = await fetch('/admin/api/update-stock', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id, amount: amount })
                });

                if(res.ok) {
                    btn.classList.add('bg-green-500');
                    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => {
                        btn.classList.remove('bg-green-500');
                        btn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    }, 2000);
                }
            } catch (err) {
                btn.classList.add('bg-red-500');
                btn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
            }
        }
    </script>
</body>
</html>

