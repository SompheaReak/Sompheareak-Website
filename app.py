<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Somphea Reak - Welcome</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
        .menu-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .menu-card:active { transform: scale(0.95); }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-6">
    <div class="max-w-md w-full text-center">
        <h1 class="text-4xl font-black uppercase italic tracking-tighter mb-2 text-slate-800">Somphea <span class="text-pink-500">Reak</span></h1>
        <p class="text-slate-400 text-[10px] font-bold uppercase tracking-[0.3em] mb-12">Select Department</p>

        <div class="grid gap-4">
            <!-- Bracelet Dept -->
            <a href="custom-bracelet.html" class="menu-card bg-white p-6 rounded-[2.5rem] shadow-xl shadow-pink-100/50 border border-pink-50 flex items-center gap-6">
                <div class="w-16 h-16 bg-pink-500 text-white rounded-2xl flex items-center justify-center text-2xl shadow-lg shadow-pink-200"><i class="fa-solid fa-gem"></i></div>
                <div class="text-left">
                    <h3 class="font-black text-lg text-slate-800">Italy Bracelet</h3>
                    <p class="text-slate-400 text-[10px] font-bold uppercase">Custom Studio</p>
                </div>
            </a>

            <!-- LEGO Dept -->
            <div class="menu-card bg-white p-6 rounded-[2.5rem] shadow-xl shadow-orange-100/50 border border-orange-50 flex items-center gap-6 opacity-60">
                <div class="w-16 h-16 bg-orange-500 text-white rounded-2xl flex items-center justify-center text-2xl shadow-lg shadow-orange-200"><i class="fa-solid fa-cubes"></i></div>
                <div class="text-left">
                    <h3 class="font-black text-lg text-slate-800">LEGO World</h3>
                    <p class="text-slate-400 text-[10px] font-bold uppercase">Coming Soon</p>
                </div>
            </div>
        </div>

        <div class="mt-12">
            <a href="admin-panel.html" class="text-slate-200 hover:text-orange-500 transition-colors"><i class="fa-solid fa-screwdriver-wrench"></i> Admin Panel</a>
        </div>
    </div>
</body>
</html>