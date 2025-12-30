<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Somphea Reak Store</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
        .card-hover:active { transform: scale(0.98); }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-center p-6">

    <!-- Header -->
    <div class="text-center mb-10">
        <div class="inline-flex items-center gap-2 mb-3 bg-white px-4 py-1.5 rounded-full shadow-sm border border-slate-100">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span class="text-xs font-bold text-slate-500 uppercase tracking-widest">Store Open</span>
        </div>
        <h1 class="text-4xl font-black text-slate-900 tracking-tight mb-2">SOMPHEA REAK</h1>
        <p class="text-slate-500 font-medium">Select a category to enter</p>
    </div>

    <!-- Navigation Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
        
        <!-- 1. Link to custom_bracelet.html -->
        <a href="/bracelet" class="card-hover group relative overflow-hidden bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-emerald-300 transition-all">
            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <i data-lucide="gem" class="w-24 h-24 text-emerald-600 rotate-12"></i>
            </div>
            <div class="relative z-10 flex flex-col h-full justify-between min-h-[120px]">
                <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="sparkles" class="w-6 h-6"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-900 leading-tight">Custom Bracelet</h2>
                    <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider mt-1 flex items-center gap-1">
                        Open Studio <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </p>
                </div>
            </div>
        </a>

        <!-- 2. Link to LEGO.html -->
        <a href="/lego" class="card-hover group relative overflow-hidden bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-yellow-300 transition-all">
            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <i data-lucide="blocks" class="w-24 h-24 text-yellow-600 -rotate-12"></i>
            </div>
            <div class="relative z-10 flex flex-col h-full justify-between min-h-[120px]">
                <div class="w-12 h-12 bg-yellow-100 text-yellow-600 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="cuboid" class="w-6 h-6"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-900 leading-tight">LEGO World</h2>
                    <p class="text-xs font-bold text-yellow-600 uppercase tracking-wider mt-1 flex items-center gap-1">
                        View Sets <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </p>
                </div>
            </div>
        </a>

        <!-- 3. Link to Lucky_draw.html -->
        <a href="/lucky-draw" class="card-hover group relative overflow-hidden bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-purple-300 transition-all">
            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <i data-lucide="gift" class="w-24 h-24 text-purple-600 rotate-6"></i>
            </div>
            <div class="relative z-10 flex flex-col h-full justify-between min-h-[120px]">
                <div class="w-12 h-12 bg-purple-100 text-purple-600 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="party-popper" class="w-6 h-6"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-900 leading-tight">Lucky Draw</h2>
                    <p class="text-xs font-bold text-purple-600 uppercase tracking-wider mt-1 flex items-center gap-1">
                        Play Now <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </p>
                </div>
            </div>
        </a>

        <!-- 4. Link to Toy.html -->
        <a href="/toys" class="card-hover group relative overflow-hidden bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100 hover:border-blue-300 transition-all">
            <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                <i data-lucide="gamepad-2" class="w-24 h-24 text-blue-600 -rotate-6"></i>
            </div>
            <div class="relative z-10 flex flex-col h-full justify-between min-h-[120px]">
                <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="rocket" class="w-6 h-6"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-900 leading-tight">Toys</h2>
                    <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mt-1 flex items-center gap-1">
                        Shop All <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </p>
                </div>
            </div>
        </a>

    </div>

    <!-- Footer -->
    <div class="mt-12 text-center text-slate-400 text-xs font-bold tracking-widest uppercase">
        © 2024 Somphea Reak App
    </div>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>

