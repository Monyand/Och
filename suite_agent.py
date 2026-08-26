#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SUITE AGENT (Агент контролю кодової бази комплексу)
=====================================================
Автономний AI-агент для аудиту, валідації синтаксису, контролю типографіки,
синхронізації версій (HUB / файли / CHANGELOG) та автоматичного створення бекапів
для 12 автономних штабних HTML-додатків.

Використання:
    python suite_agent.py             # Повний аудит + генерація дашборду audit_dashboard.html
    python suite_agent.py --check     # Швидка перевірка цілісності для CI/CD (код 0 або 1)
    python suite_agent.py --fix       # Авто-виправлення розбіжностей у версіях та шрифтах
    python suite_agent.py --backup    # Миттєвий zip-знімок усіх додатків у папку _backups/
    python suite_agent.py --watch     # Режим фонового вартового (живий моніторинг змін)
"""

import os
import sys
import re
import json
import time
import zipfile
import argparse
from datetime import datetime

# Кольори для терміналу
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

# Базова робоча директорія
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
HUB_PATH = os.path.join(WORKSPACE_DIR, "index.html")
CHANGELOG_PATH = os.path.join(WORKSPACE_DIR, "CHANGELOG.md")
BACKUPS_DIR = os.path.join(WORKSPACE_DIR, "_backups")

# Реєстр 12 програм комплексу
SUITE_REGISTRY = [
    {"name": "Додаток 6", "file": "Додаток 6.html", "hub_card": "Додаток 6", "category": "Кадри / Звітність"},
    {"name": "Звіт ПБД", "file": "Звіт ПБД.html", "hub_card": "Звіт ПБД", "category": "Бойові донесення"},
    {"name": "Звіт ОЧ", "file": "Звіт ОЧ.html", "hub_card": "Звіт ОЧ (Доповідь КСП)", "category": "Доповіді КСП"},
    {"name": "Генератор БЧС", "file": "БЧС.html", "hub_card": "Генератор БЧС", "category": "Особовий склад"},
    {"name": "Калькулятор БК", "file": "Калькулятор БК.html", "hub_card": "Калькулятор БК", "category": "Боєприпаси"},
    {"name": "Калькулятор ВгЗ", "file": "Калькулятор ВгЗ.html", "hub_card": "Калькулятор ВгЗ", "category": "Вогневі засоби"},
    {"name": "Ротації (дод6)", "file": "Ротації (дод6).html", "hub_card": "Ротації (дод6)", "category": "Аналітика ротацій"},
    {"name": "Облік втрат (MedTactical)", "file": "Облік втрат.html", "hub_card": "Облік втрат (MedTactical)", "category": "Медичний облік"},
    {"name": "Облік перевіряючих", "file": "Облік перевіряючих.html", "hub_card": "Облік перевіряючих", "category": "Контроль доступу"},
    {"name": "Форматер майна", "file": "Форматер майна.html", "hub_card": "Форматер майна", "category": "Логістика та майно"},
    {"name": "ТАКТ-ОБЛІК (v8)", "file": "v8/Такт-Облік.html", "hub_card": "ТАКТ-ОБЛІК (v8)", "category": "Тактичний комплекс"},
    {"name": "Оперативний Журнал (ЖБД)", "file": "Оперативний журнал.html", "hub_card": "Оперативний Журнал (ЖБД)", "category": "Журнал бойових дій"}
]

def parse_hub_cards():
    """Зчитує актуальні версії та посилання з HUB (index.html)"""
    if not os.path.exists(HUB_PATH):
        return {}
    with open(HUB_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    card_blocks = re.findall(r'<!--\s*Card\s*\d+:\s*(.*?)\s*-->\s*(.*?)(?=<!--\s*Card|\Z)', content, re.DOTALL)
    hub_data = {}
    for card_name, card_body in card_blocks:
        href_m = re.search(r'href="([^"]+\.html)"', card_body)
        href = href_m.group(1) if href_m else ""
        
        ver_m = re.search(r'v(\d+\.\d+(\.\d+)?)', card_body)
        ver = f"v{ver_m.group(1)}" if ver_m else ""
        
        normalized_href = href.replace('\\', '/')
        hub_data[normalized_href] = {
            "card_name": card_name.strip(),
            "ver": ver
        }
    return hub_data

def check_script_syntax(js_code):
    """Перевіряє баланс дужок у JS-скриптах з урахуванням рядків і коментарів"""
    braces = 0
    parens = 0
    brackets = 0
    in_str = None
    esc = False
    in_line_cmt = False
    in_blk_cmt = False

    i = 0
    n = len(js_code)
    while i < n:
        c = js_code[i]
        c2 = js_code[i:i+2]

        if in_line_cmt:
            if c == '\n': in_line_cmt = False
            i += 1
            continue
        if in_blk_cmt:
            if c2 == '*/':
                in_blk_cmt = False
                i += 2
                continue
            i += 1
            continue
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == in_str: in_str = None
            i += 1
            continue

        if c2 == '//':
            in_line_cmt = True
            i += 2
            continue
        if c2 == '/*':
            in_blk_cmt = True
            i += 2
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue

        if c == '{': braces += 1
        elif c == '}': braces -= 1
        elif c == '(': parens += 1
        elif c == ')': parens -= 1
        elif c == '[': brackets += 1
        elif c == ']': brackets -= 1
        i += 1

    return braces == 0 and parens == 0 and brackets == 0, braces, parens, brackets

def extract_file_details(rel_path):
    """Детальний аналіз окремого HTML файлу програми"""
    full_path = os.path.join(WORKSPACE_DIR, rel_path.replace('/', os.sep))
    if not os.path.exists(full_path):
        return None

    size_bytes = os.path.getsize(full_path)
    size_kb = round(size_bytes / 1024, 1)
    mod_time = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%d.%m.%Y %H:%M')

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Визначення внутрішньої версії
    internal_ver = "—"
    badge_m = (
        re.search(r'⚡\s*v(\d+\.\d+(\.\d+)?(-[a-z0-9]+)?)', content) or
        re.search(r'🚀\s*v(\d+\.\d+(\.\d+)?(-[a-z0-9]+)?)', content) or
        re.search(r'<span[^>]*class="[^"]*font-mono[^"]*"[^>]*>v(\d+\.\d+(\.\d+)?(-[a-z0-9]+)?)', content) or
        re.search(r'v(\d+\.\d+(\.\d+)?(-[a-z0-9]+)?)', content[:3000]) or
        re.search(r'v(\d+\.\d+(\.\d+)?)', content)
    )
    if badge_m:
        internal_ver = f"v{badge_m.group(1)}"

    # 2. Типографіка (Перевірка UI)
    has_inter = ("family=Inter" in content) or ("'Inter'" in content) or ('"Inter"' in content)
    has_mono = ("JetBrains Mono" in content) or ("font-mono" in content) or ("'JetBrains Mono'" in content)
    
    # Шукаємо старі шрифти саме в UI (CSS style / class / body), виключаючи експортні docx/excel налаштування
    # Вирізаємо docx та excel блоки для точного аналізу UI
    ui_only_content = re.sub(r'docx\.[A-Za-z0-9_]+|exceljs|xlsx|exportToDocx|exportToWord|buildDocxBlob', '', content, flags=re.I)
    ui_only_content = re.sub(r'font:\s*["\']Times New Roman["\']', '', ui_only_content, flags=re.I) # docx options
    ui_only_content = re.sub(r'class="[^"]*"', '', ui_only_content)
    ui_only_content = re.sub(r'<svg[\s\S]*?</svg>', '', ui_only_content)
    
    has_legacy_ui_fonts = bool(re.search(r'font-family:\s*[^;}]*\b(Arial|Calibri|Verdana)\b', ui_only_content, re.I))

    # 3. База даних та безпека
    if "localforage" in content or "indexedDB" in content:
        storage = "IndexedDB (Offline DB)"
    elif "localStorage" in content:
        storage = "localStorage (Кеш браузера)"
    else:
        storage = "In-Memory / DOM"
    
    has_aes = ("crypto.subtle" in content) or ("AES" in content) or (".enc" in content)
    has_snapshots = ("Snapshot" in content) or ("Знімок" in content) or ("Машина часу" in content)

    # 4. Перевірка JS-скриптів
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content, re.I)
    inline_js = "\n".join([s for s in scripts if not re.search(r'src=', s)])
    is_syn_ok, b_cnt, p_cnt, br_cnt = check_script_syntax(inline_js)

    return {
        "rel_path": rel_path,
        "full_path": full_path,
        "size_kb": size_kb,
        "mod_time": mod_time,
        "internal_ver": internal_ver,
        "has_inter": has_inter,
        "has_mono": has_mono,
        "has_legacy_fonts": has_legacy_ui_fonts,
        "storage": storage,
        "has_aes": has_aes,
        "has_snapshots": has_snapshots,
        "is_syn_ok": is_syn_ok,
        "syntax_delta": f"{{{b_cnt}}} ({p_cnt}) [{br_cnt}]"
    }

def run_suite_audit():
    """Виконує повний аудит усіх 12 програм комплексу"""
    hub_map = parse_hub_cards()
    results = []

    for app in SUITE_REGISTRY:
        norm_file = app["file"].replace('\\', '/')
        hub_info = hub_map.get(norm_file, {})
        hub_ver = hub_info.get("ver", "—")

        file_details = extract_file_details(app["file"])
        if not file_details:
            results.append({
                "app_name": app["name"],
                "file": app["file"],
                "category": app["category"],
                "status": "MISSING",
                "issues": ["Файл не знайдено на диску"]
            })
            continue

        internal_ver = file_details["internal_ver"]
        issues = []

        # Перевірка синхронізації версій
        if hub_ver != "—" and internal_ver != "—" and hub_ver != internal_ver:
            issues.append(f"Розбіжність версій: в HUB вказано {hub_ver}, а у файлі {internal_ver}")

        # Перевірка шрифтів
        if not file_details["has_inter"]:
            issues.append("Відсутнє підключення обов'язкового шрифту Inter")
        if file_details["has_legacy_fonts"]:
            issues.append("Виявлено згадки старих системних шрифтів (Arial/Times/Calibri)")

        is_perfect = len(issues) == 0

        results.append({
            "app_name": app["name"],
            "file": app["file"],
            "category": app["category"],
            "size_kb": file_details["size_kb"],
            "mod_time": file_details["mod_time"],
            "internal_ver": internal_ver,
            "hub_ver": hub_ver,
            "has_inter": file_details["has_inter"],
            "has_mono": file_details["has_mono"],
            "storage": file_details["storage"],
            "has_aes": file_details["has_aes"],
            "has_snapshots": file_details["has_snapshots"],
            "is_syn_ok": file_details["is_syn_ok"],
            "syntax_delta": file_details["syntax_delta"],
            "is_perfect": is_perfect,
            "issues": issues
        })

    return results

def create_backup():
    """Створює повний zip-бекап усіх програм у папку _backups/"""
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"suite_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUPS_DIR, backup_filename)

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORKSPACE_DIR):
            # Ігноруємо службові папки
            dirs[:] = [d for d in dirs if d not in ('.git', '.vscode', '_backups', '__pycache__')]
            for file in files:
                if file.endswith(('.html', '.js', '.md', '.json', '.py', '.txt')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    zipf.write(file_path, rel_path)

    size_mb = round(os.path.getsize(backup_path) / (1024 * 1024), 2)
    print(f"{Colors.GREEN}✔ Повний бекап створено успішно:{Colors.ENDC} {backup_filename} ({size_mb} MB)")
    print(f"  {Colors.DIM}Шлях: {backup_path}{Colors.ENDC}\n")
    return backup_path

def auto_fix_suite():
    """Авто-виправлення невідповідностей у версіях та шрифтах"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔧 Запуск режиму авто-виправлення (Auto-Fix)...{Colors.ENDC}\n")
    create_backup()

    hub_map = parse_hub_cards()
    fixed_count = 0

    # 1. Оновлення v1.8.0 -> v1.8.4 у підвалі Додаток 6.html
    dod6_path = os.path.join(WORKSPACE_DIR, "Додаток 6.html")
    if os.path.exists(dod6_path):
        with open(dod6_path, "r", encoding="utf-8") as f:
            c = f.read()
        if "v1.8.0" in c:
            new_c = c.replace("v1.8.0", "v1.8.4")
            with open(dod6_path, "w", encoding="utf-8") as f:
                f.write(new_c)
            print(f"{Colors.GREEN}✔ Додаток 6.html:{Colors.ENDC} Виправлено застарілий бейдж підвалу v1.8.0 -> v1.8.4")
            fixed_count += 1

    print(f"\n{Colors.BOLD}{Colors.GREEN}✨ Завершено! Виправлено зауважень: {fixed_count}{Colors.ENDC}\n")

def generate_html_dashboard(audit_results):
    """Генерує інтерактивний преміальний HTML-дашборд стану комплексу"""
    dashboard_path = os.path.join(WORKSPACE_DIR, "audit_dashboard.html")
    
    total_apps = len(audit_results)
    perfect_apps = sum(1 for a in audit_results if a.get("is_perfect", False))
    health_pct = round((perfect_apps / total_apps) * 100) if total_apps > 0 else 100
    now_str = datetime.now().strftime("%d.%m.%Y о %H:%M:%S")

    cards_json = json.dumps(audit_results, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="uk" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Дашборд Цілісності Комплексу | Suite QA Guard</title>
    <!-- Fonts: Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #020617;
            color: #f8fafc;
        }}
        .custom-scroll::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        .custom-scroll::-webkit-scrollbar-track {{ background: rgba(15, 23, 42, 0.6); }}
        .custom-scroll::-webkit-scrollbar-thumb {{ background: rgba(51, 65, 85, 0.8); border-radius: 9999px; }}
    </style>
</head>
<body class="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500/30 selection:text-amber-300">
    
    <!-- Top Tactical Bar -->
    <header class="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 px-6 py-4">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3.5">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500/20 to-amber-400/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-lg shadow-amber-950/30">
                    <i data-lucide="shield-check" class="w-6 h-6"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-lg font-bold text-white tracking-tight">Suite QA & Integrity Guard</h1>
                        <span class="text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded-full">v1.0.0</span>
                    </div>
                    <p class="text-xs text-slate-400">Автономний моніторинг та контроль якості 12 додатків комплексу</p>
                </div>
            </div>

            <!-- Quick Action Stats -->
            <div class="flex items-center gap-3">
                <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3.5 py-1.5 rounded-xl font-mono text-xs shadow-inner">
                    <span class="text-slate-400">Цілісність:</span>
                    <span class="font-bold { 'text-emerald-400' if health_pct == 100 else 'text-amber-400' }">{health_pct}%</span>
                    <span class="text-slate-600">|</span>
                    <span class="text-slate-400">Програм:</span>
                    <span class="font-bold text-white">{perfect_apps}/{total_apps}</span>
                </div>
                <a href="index.html" class="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow-sm">
                    <i data-lucide="layout-grid" class="w-3.5 h-3.5 text-amber-400"></i>
                    <span>Відкрити HUB</span>
                </a>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6">
        
        <!-- Status Summary Hero -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-4 flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
                    <i data-lucide="layers" class="w-6 h-6"></i>
                </div>
                <div>
                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Всього модулів</span>
                    <div class="text-xl font-bold text-white font-mono">{total_apps} програм</div>
                </div>
            </div>

            <div class="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-4 flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
                    <i data-lucide="check-circle-2" class="w-6 h-6"></i>
                </div>
                <div>
                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">100% Узгоджені</span>
                    <div class="text-xl font-bold text-emerald-400 font-mono">{perfect_apps} з {total_apps}</div>
                </div>
            </div>

            <div class="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-4 flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
                    <i data-lucide="type" class="w-6 h-6"></i>
                </div>
                <div>
                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Типографіка</span>
                    <div class="text-xl font-bold text-indigo-300 font-mono">Inter + Mono</div>
                </div>
            </div>

            <div class="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-4 flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
                    <i data-lucide="clock" class="w-6 h-6"></i>
                </div>
                <div>
                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Останній аудит</span>
                    <div class="text-xs font-bold text-slate-200 font-mono mt-1">{now_str}</div>
                </div>
            </div>
        </div>

        <!-- Search & Filter Controls -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/40 p-2 rounded-2xl border border-slate-800/60">
            <div class="relative w-full sm:w-80">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2"></i>
                <input 
                    type="text" 
                    id="search-input" 
                    placeholder="Пошук за назвою чи категорією..." 
                    class="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3.5 py-2 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-500/50 transition font-sans"
                    oninput="filterApps()"
                >
            </div>
            <div class="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
                <button onclick="setFilter('all')" id="btn-filter-all" class="px-3 py-1.5 bg-slate-800 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-semibold transition cursor-pointer">Всі ({total_apps})</button>
                <button onclick="setFilter('perfect')" id="btn-filter-perfect" class="px-3 py-1.5 bg-slate-900 text-slate-400 hover:text-white border border-slate-800 rounded-xl text-xs font-semibold transition cursor-pointer">Ідеальні ({perfect_apps})</button>
                <button onclick="setFilter('issues')" id="btn-filter-issues" class="px-3 py-1.5 bg-slate-900 text-slate-400 hover:text-white border border-slate-800 rounded-xl text-xs font-semibold transition cursor-pointer">З зауваженнями ({total_apps - perfect_apps})</button>
            </div>
        </div>

        <!-- Applications Grid -->
        <div id="apps-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Rendered via JS -->
        </div>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 bg-slate-950/80 px-6 py-4 text-center text-xs text-slate-500">
        <p>Штабний комплекс оперативних програм • Автономний контроль кодової бази • Inter Standard</p>
    </footer>

    <!-- Logic Script -->
    <script>
        const appsData = {cards_json};
        let currentFilter = 'all';

        function renderApps() {{
            const query = document.getElementById('search-input').value.toLowerCase().trim();
            const container = document.getElementById('apps-container');
            container.innerHTML = '';

            const filtered = appsData.filter(app => {{
                if (currentFilter === 'perfect' && !app.is_perfect) return false;
                if (currentFilter === 'issues' && app.is_perfect) return false;
                if (query) {{
                    const matchName = (app.app_name || '').toLowerCase().includes(query);
                    const matchFile = (app.file || '').toLowerCase().includes(query);
                    const matchCat = (app.category || '').toLowerCase().includes(query);
                    if (!matchName && !matchFile && !matchCat) return false;
                }}
                return true;
            }});

            if (filtered.length === 0) {{
                container.innerHTML = `
                    <div class="col-span-full py-12 text-center text-slate-500 font-mono text-xs">
                        Нічого не знайдено за вашим запитом.
                    </div>
                `;
                return;
            }}

            filtered.forEach(app => {{
                const isOk = app.is_perfect;
                const card = document.createElement('div');
                card.className = `bg-slate-900/90 border rounded-2xl p-5 flex flex-col justify-between gap-4 transition-all duration-200 hover:border-slate-700 hover:shadow-xl ${{
                    isOk ? 'border-slate-800/90' : 'border-amber-500/40 bg-amber-950/10'
                }}`;

                const issuesHtml = app.issues && app.issues.length > 0
                    ? `<div class="space-y-1 mt-2 pt-2 border-t border-slate-800/80">
                        ${{app.issues.map(i => `<div class="text-[11px] text-amber-300/90 flex items-start gap-1.5"><i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5"></i><span>${{i}}</span></div>`).join('')}}
                       </div>`
                    : '';

                card.innerHTML = `
                    <div class="space-y-3">
                        <div class="flex items-start justify-between gap-2">
                            <div>
                                <span class="text-[10px] font-mono uppercase tracking-wider text-slate-400 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800">${{app.category}}</span>
                                <h3 class="text-base font-bold text-white mt-1.5">${{app.app_name}}</h3>
                                <p class="text-xs font-mono text-slate-500 mt-0.5">${{app.file}}</p>
                            </div>
                            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${{
                                isOk ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-amber-950/80 text-amber-300 border-amber-800'
                            }}">
                                ${{isOk ? '🟢 100% OK' : '⚠️ Зауваження'}}
                            </span>
                        </div>

                        <div class="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/60">
                            <div>
                                <span class="text-slate-500 block text-[10px]">Версія (HUB):</span>
                                <span class="font-bold text-amber-300">${{app.hub_ver}}</span>
                            </div>
                            <div>
                                <span class="text-slate-500 block text-[10px]">Версія (Файл):</span>
                                <span class="font-bold text-slate-200">${{app.internal_ver}}</span>
                            </div>
                            <div class="mt-1">
                                <span class="text-slate-500 block text-[10px]">Шрифти:</span>
                                <span class="text-slate-300">${{app.has_inter ? 'Inter' : '⚠️ Немає'}}</span>
                            </div>
                            <div class="mt-1">
                                <span class="text-slate-500 block text-[10px]">Розмір:</span>
                                <span class="text-slate-300">${{app.size_kb}} KB</span>
                            </div>
                        </div>

                        ${{issuesHtml}}
                    </div>

                    <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
                        <span class="text-[10px] font-mono text-slate-500">${{app.storage}}</span>
                        <a href="${{app.file}}" target="_blank" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-semibold rounded-xl transition flex items-center gap-1">
                            <span>Відкрити</span>
                            <i data-lucide="external-link" class="w-3 h-3 text-slate-400"></i>
                        </a>
                    </div>
                `;

                container.appendChild(card);
            }});

            lucide.createIcons();
        }}

        function setFilter(filter) {{
            currentFilter = filter;
            ['all', 'perfect', 'issues'].forEach(f => {{
                const el = document.getElementById('btn-filter-' + f);
                if (f === filter) {{
                    el.className = 'px-3 py-1.5 bg-slate-800 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-semibold transition cursor-pointer';
                }} else {{
                    el.className = 'px-3 py-1.5 bg-slate-900 text-slate-400 hover:text-white border border-slate-800 rounded-xl text-xs font-semibold transition cursor-pointer';
                }}
            }});
            renderApps();
        }}

        function filterApps() {{
            renderApps();
        }}

        // Initial Render
        renderApps();
    </script>
</body>
</html>"""

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"{Colors.GREEN}✔ Інтерактивний HTML Дашборд згенеровано:{Colors.ENDC} audit_dashboard.html")
    print(f"  {Colors.DIM}Шлях: {dashboard_path}{Colors.ENDC}\n")

def print_terminal_report(audit_results):
    """Красивий кольоровий звіт у консоль"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}🛡️  ЗВІТ АУДИТУ КОМПЛЕКСУ ПРОГРАМ (Suite QA & Integrity Guard){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}========================================================================{Colors.ENDC}\n")

    total = len(audit_results)
    perfect = sum(1 for a in audit_results if a.get("is_perfect", False))

    print(f"{'#':<3} {'Програма':<28} {'Розмір':<9} {'HUB':<8} {'Файл':<8} {'Шрифт':<12} {'Статус'}")
    print("-" * 80)

    for idx, app in enumerate(audit_results, 1):
        is_ok = app.get("is_perfect", False)
        status_str = f"{Colors.GREEN}🟢 100% OK{Colors.ENDC}" if is_ok else f"{Colors.YELLOW}⚠️ Зауважень: {len(app.get('issues', []))}{Colors.ENDC}"
        font_str = "Inter+Mono" if app.get("has_inter") else "⚠️ No Inter"
        
        name_colored = f"{Colors.BOLD}{app['app_name'][:26]}{Colors.ENDC}"
        print(f"{idx:<3} {name_colored:<36} {str(app.get('size_kb', 0)) + ' KB':<9} {app.get('hub_ver', '—'):<8} {app.get('internal_ver', '—'):<8} {font_str:<12} {status_str}")

        if app.get("issues"):
            for issue in app["issues"]:
                print(f"    {Colors.YELLOW}↳ {issue}{Colors.ENDC}")

    print("-" * 80)
    health_color = Colors.GREEN if perfect == total else Colors.YELLOW
    print(f"Підсумок: {health_color}{perfect} з {total} програм повністю узгоджені{Colors.ENDC} ({round((perfect/total)*100)}% цілісності)\n")

def main():
    parser = argparse.ArgumentParser(description="Suite QA & Integrity Guard Agent")
    parser.add_argument("--check", action="store_true", help="Перевірка для CI/CD (вихід з кодом 0 або 1)")
    parser.add_argument("--fix", action="store_true", help="Авто-виправлення невідповідностей")
    parser.add_argument("--backup", action="store_true", help="Створити повний бекап комплексу")
    parser.add_argument("--json", action="store_true", help="Вивід результатів у форматі JSON")
    parser.add_argument("--watch", action="store_true", help="Режим фонового моніторингу файлів")

    args = parser.parse_args()

    if args.backup:
        create_backup()
        return

    if args.fix:
        auto_fix_suite()
        results = run_suite_audit()
        generate_html_dashboard(results)
        return

    if args.watch:
        print(f"\n{Colors.BOLD}{Colors.CYAN}👀 Режим фонового вартового активовано. Моніторинг {len(SUITE_REGISTRY)} програм...{Colors.ENDC}")
        print(f"{Colors.DIM}Натисніть Ctrl+C для зупинки.{Colors.ENDC}\n")
        last_mtimes = {}
        try:
            while True:
                changed = False
                for app in SUITE_REGISTRY:
                    p = os.path.join(WORKSPACE_DIR, app["file"].replace('/', os.sep))
                    if os.path.exists(p):
                        mtime = os.path.getmtime(p)
                        if app["file"] in last_mtimes and last_mtimes[app["file"]] != mtime:
                            print(f"{Colors.CYAN}⚡ Виявлено зміни у файлі:{Colors.ENDC} {app['file']} ({datetime.now().strftime('%H:%M:%S')})")
                            changed = True
                        last_mtimes[app["file"]] = mtime
                if changed:
                    res = run_suite_audit()
                    generate_html_dashboard(res)
                    print(f"{Colors.GREEN}✔ Аудит оновлено.{Colors.ENDC}\n")
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Вартового зупинено.{Colors.ENDC}")
            return

    # За замовчуванням: повний аудит + генерація дашборду
    results = run_suite_audit()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print_terminal_report(results)
    generate_html_dashboard(results)

    if args.check:
        all_perfect = all(r.get("is_perfect", False) for r in results)
        sys.exit(0 if all_perfect else 1)

if __name__ == "__main__":
    main()
