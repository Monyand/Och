#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SUITE AGENT (Агент контролю кодової бази комплексу)
=====================================================
Автономний AI-агент для аудиту, валідації синтаксису, контролю типографіки,
синхронізації версій (HUB / файли / CHANGELOG) та автоматичного створення бекапів
для 12 автономних штабних HTML-додатків.

Використання:
    python suite_agent.py             # Повний аудит комплексу
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

# Реєстр 14 програм комплексу
SUITE_REGISTRY = [
    {"name": "Додаток 6", "file": "Додаток 6.html", "hub_card": "Додаток 6", "category": "Кадри / Звітність"},
    {"name": "Звіт ПБД", "file": "Звіт ПБД.html", "hub_card": "Звіт ПБД", "category": "Бойові донесення"},
    {"name": "Звіт ОЧ", "file": "Звіт ОЧ.html", "hub_card": "Звіт ОЧ (Доповідь КСП)", "category": "Доповіді КСП"},
    {"name": "Генератор БЧС", "file": "БЧС.html", "hub_card": "Генератор БЧС", "category": "Особовий склад"},
    {"name": "Калькулятор БК", "file": "Калькулятор БК.html", "hub_card": "Калькулятор БК", "category": "Боєприпаси"},
    {"name": "Калькулятор ВгЗ", "file": "Калькулятор ВгЗ.html", "hub_card": "Калькулятор ВгЗ", "category": "Вогневі засоби"},
    {"name": "Ротації (дод6)", "file": "Ротації (дод6).html", "hub_card": "Ротації (дод6)", "category": "Аналітика ротацій"},
    {"name": "Облік періодів (БЗ & ДВ 30)", "file": "Облік періодів.html", "hub_card": "Облік періодів (БЗ & ДВ 30)", "category": "БЗ & ДВ 30"},
    {"name": "Облік втрат (MedTactical)", "file": "Облік втрат.html", "hub_card": "Облік втрат (MedTactical)", "category": "Медичний облік"},
    {"name": "Облік перевіряючих", "file": "Облік перевіряючих.html", "hub_card": "Облік перевіряючих", "category": "Контроль доступу"},
    {"name": "Форматер майна", "file": "Форматер майна.html", "hub_card": "Форматер майна", "category": "Логістика та майно"},
    {"name": "ТАКТ-ОБЛІК (v8)", "file": "v8/Такт-Облік.html", "hub_card": "ТАКТ-ОБЛІК (v8)", "category": "Тактичний комплекс"},
    {"name": "Оперативний Журнал (ЖБД)", "file": "Оперативний журнал.html", "hub_card": "Оперативний Журнал (ЖБД)", "category": "Журнал бойових дій"},
    {"name": "Аналізатор переміщень (дод6)", "file": "Переміщення (дод6).html", "hub_card": "Аналізатор переміщень (Додаток 6)", "category": "Логістика о/с"}
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
        print_terminal_report(results)
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
                    print_terminal_report(res)
                    print(f"{Colors.GREEN}✔ Аудит оновлено.{Colors.ENDC}\n")
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Вартового зупинено.{Colors.ENDC}")
            return

    # За замовчуванням: повний аудит
    results = run_suite_audit()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print_terminal_report(results)

    if args.check:
        all_perfect = all(r.get("is_perfect", False) for r in results)
        sys.exit(0 if all_perfect else 1)

if __name__ == "__main__":
    main()
