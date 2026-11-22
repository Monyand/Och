#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SUITE AGENT (Агент контролю кодової бази комплексу)
=====================================================
Автономний QA-агент для аудиту цілісності, синхронізації версій (HUB / файли),
перевірки офлайн-ресурсів, OPSEC-чистоти та резервного копіювання модулів HUB.

Використання:
    python suite_agent.py             # Повний аудит комплексу
    python suite_agent.py --check     # Перевірка цілісності для CI/CD (код 0 або 1)
    python suite_agent.py --backup    # Миттєвий zip-знімок усіх додатків у папку _backups/
    python suite_agent.py --json      # Вивід результатів у JSON
    python suite_agent.py --watch     # Режим фонового вартового
"""

import os
import sys
import re
import json
import time
import zipfile
import argparse
from datetime import datetime

# UTF-8 у консолі Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
HUB_PATH = os.path.join(WORKSPACE_DIR, "index.html")
BACKUPS_DIR = os.path.join(WORKSPACE_DIR, "_backups")

OPSEC_PATTERNS = [
    ("Номер бригади / в/ч", re.compile(r'125\s*(?:овмбр|обр|омбр|тро|овтбр)|120\s*обр|в/ч\s*[АA]\d{4}', re.I)),
    ("Локальний IP 10.16.x.x", re.compile(r'\b10\.16\.\d+\.\d+\b')),
    ("MGRS-координати", re.compile(r'\b3[567][TU]\s*[A-Z]{2}\s*\d{4,}')),
]


def parse_hub_modules():
    """Динамічно зчитує актуальні картки модулів з HUB (index.html)."""
    if not os.path.exists(HUB_PATH):
        return []
    with open(HUB_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = re.compile(
        r'<div\s+class="module-row\s+app-item[^"]*"[^>]*>(.*?)</div>\s*</div>',
        re.DOTALL
    )
    # Безпечне розбиття за початком кожної картки module-row app-item
    chunks = re.split(r'(?=<div\s+class="module-row\s+app-item)', content)
    modules = []
    for chunk in chunks[1:]:
        code_m = re.search(r'<span\s+class="module-code">([^<]+)</span>', chunk)
        name_m = re.search(r'<span\s+class="module-name">([^<]+)</span>', chunk)
        ver_m = re.search(r'<span\s+class="module-ver">(v\d+\.\d+(?:\.\d+)?)</span>', chunk)
        date_m = re.search(r'<span\s+class="module-date">([^<]+)</span>', chunk)
        href_m = re.search(r'<a\s+href="([^"]+\.html)"', chunk)

        if not href_m:
            continue

        modules.append({
            "code": code_m.group(1).strip() if code_m else "—",
            "name": name_m.group(1).strip() if name_m else href_m.group(1),
            "file": href_m.group(1).replace("\\", "/").strip(),
            "hub_ver": ver_m.group(1).strip() if ver_m else "—",
            "hub_date": date_m.group(1).strip() if date_m else "—",
        })
    return modules


def extract_internal_version(content, expected_hub_ver="—"):
    """Визначає версію UI-бейджа всередині HTML-файлу (відсіюючи мініфіковані vendor-скрипти)."""
    clean_lines = [l for l in content.splitlines() if len(l) < 3000]
    search_part = "\n".join(clean_lines[:2500])

    if expected_hub_ver != "—" and re.search(r'(?<![0-9A-Za-z])' + re.escape(expected_hub_ver) + r'(?![0-9.])', search_part):
        return expected_hub_ver

    patterns = [
        r'openChangelogModal\(\)[\s\S]{0,400}?(v\d+\.\d+(?:\.\d+)?)',
        r'changelog-modal[\s\S]{0,400}?(v\d+\.\d+(?:\.\d+)?)',
        r'btn-version[\s\S]{0,300}?(v\d+\.\d+(?:\.\d+)?)',
        r'<span[^>]*>\s*(v\d+\.\d+(?:\.\d+)?)\s*</span>',
        r'(?:⚡|🚀)\s*(v\d+\.\d+(?:\.\d+)?)',
        r'\b(v\d+\.\d+\.\d+)\b',
    ]
    for pat in patterns:
        m = re.search(pat, search_part, re.I)
        if m:
            return m.group(1)
    return "—"


def scan_opsec(content):
    """Перевіряє немінімізовані рядки HTML на OPSEC-витоки."""
    hits = []
    for idx, line in enumerate(content.splitlines(), 1):
        if len(line) > 2000:
            continue  # пропускаємо мініфіковані вбудовані бібліотеки
        for label, rx in OPSEC_PATTERNS:
            if rx.search(line):
                hits.append(f"OPSEC ({label}) на рядку {idx}")
                break
    return hits


def extract_file_details(rel_path, expected_hub_ver="—"):
    """Аналіз окремого HTML-файлу модуля."""
    full_path = os.path.join(WORKSPACE_DIR, rel_path.replace("/", os.sep))
    if not os.path.exists(full_path):
        return None

    size_kb = round(os.path.getsize(full_path) / 1024, 1)
    mod_time = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%d.%m.%Y %H:%M')

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    internal_ver = extract_internal_version(content, expected_hub_ver)
    opsec_hits = scan_opsec(content)

    has_local_v8 = ("v8/" in content) or ("#vendor-" in content) or ("xlsx.js" in content) or ("docx.js" in content)
    has_google_fonts = "fonts.googleapis.com" in content
    runtime_mode = "Offline" if (has_local_v8 and not has_google_fonts) else ("Offline*" if has_local_v8 else "Standalone")

    return {
        "rel_path": rel_path,
        "full_path": full_path,
        "size_kb": size_kb,
        "mod_time": mod_time,
        "internal_ver": internal_ver,
        "runtime_mode": runtime_mode,
        "opsec_hits": opsec_hits,
    }


def run_suite_audit():
    """Повний аудит усіх модулів, зареєстрованих у HUB (index.html)."""
    modules = parse_hub_modules()
    results = []

    for mod in modules:
        details = extract_file_details(mod["file"], mod["hub_ver"])
        if not details:
            results.append({
                "code": mod["code"],
                "app_name": mod["name"],
                "file": mod["file"],
                "size_kb": 0,
                "hub_ver": mod["hub_ver"],
                "internal_ver": "—",
                "runtime_mode": "—",
                "is_perfect": False,
                "issues": [f"Файл не знайдено на диску: {mod['file']}"],
            })
            continue

        issues = []
        if mod["hub_ver"] != "—" and details["internal_ver"] != "—" and mod["hub_ver"] != details["internal_ver"]:
            issues.append(f"Розбіжність версій: HUB={mod['hub_ver']}, файл={details['internal_ver']}")
        if details["opsec_hits"]:
            issues.extend(details["opsec_hits"][:3])

        results.append({
            "code": mod["code"],
            "app_name": mod["name"],
            "file": mod["file"],
            "size_kb": details["size_kb"],
            "mod_time": details["mod_time"],
            "hub_ver": mod["hub_ver"],
            "internal_ver": details["internal_ver"],
            "runtime_mode": details["runtime_mode"],
            "is_perfect": len(issues) == 0,
            "issues": issues,
        })

    return results


def create_backup():
    """Створює повний zip-бекап усіх програм у папку _backups/."""
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"suite_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUPS_DIR, backup_filename)

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORKSPACE_DIR):
            dirs[:] = [d for d in dirs if d not in ('.git', '.vscode', '_backups', '__pycache__', 'sys_utils', 'android_app')]
            for file in files:
                if file.endswith(('.html', '.js', '.md', '.json', '.py', '.txt')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    zipf.write(file_path, rel_path)

    size_mb = round(os.path.getsize(backup_path) / (1024 * 1024), 2)
    print(f"{Colors.GREEN}✔ Повний бекап створено:{Colors.ENDC} {backup_filename} ({size_mb} MB)")
    return backup_path


def print_terminal_report(audit_results):
    print(f"\n{Colors.BOLD}{Colors.HEADER}================================================================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}🛡️  ЗВІТ АУДИТУ КОМПЛЕКСУ ПРОГРАМ (Suite QA & Integrity Guard){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}================================================================================{Colors.ENDC}\n")

    total = len(audit_results)
    perfect = sum(1 for a in audit_results if a.get("is_perfect", False))

    print(f"{'Код':<6} {'Програма':<24} {'Розмір':<10} {'HUB':<8} {'Файл':<8} {'Режим':<11} {'Статус'}")
    print("-" * 82)

    for app in audit_results:
        is_ok = app.get("is_perfect", False)
        status_str = f"{Colors.GREEN}🟢 100% OK{Colors.ENDC}" if is_ok else f"{Colors.RED}❌ Проблем: {len(app.get('issues', []))}{Colors.ENDC}"
        size_str = f"{app.get('size_kb', 0)} KB"
        print(f"{app['code']:<6} {app['app_name'][:23]:<24} {size_str:<10} {app.get('hub_ver', '—'):<8} {app.get('internal_ver', '—'):<8} {app.get('runtime_mode', '—'):<11} {status_str}")
        for issue in app.get("issues", []):
            print(f"       {Colors.YELLOW}↳ {issue}{Colors.ENDC}")

    print("-" * 82)
    pct = round((perfect / total) * 100) if total else 0
    health_color = Colors.GREEN if perfect == total and total > 0 else Colors.YELLOW
    print(f"Підсумок: {health_color}{perfect} з {total} програм повністю узгоджені ({pct}% цілісності){Colors.ENDC}\n")


def main():
    parser = argparse.ArgumentParser(description="Suite QA & Integrity Guard Agent")
    parser.add_argument("--check", action="store_true", help="Перевірка для CI/CD (вихід з кодом 0 або 1)")
    parser.add_argument("--backup", action="store_true", help="Створити повний бекап комплексу")
    parser.add_argument("--json", action="store_true", help="Вивід результатів у форматі JSON")
    parser.add_argument("--watch", action="store_true", help="Режим фонового моніторингу файлів")
    args = parser.parse_args()

    if args.backup:
        create_backup()
        return

    if args.watch:
        modules = parse_hub_modules()
        print(f"\n{Colors.BOLD}{Colors.CYAN}👀 Режим вартового активовано ({len(modules)} модулів). Ctrl+C для зупинки.{Colors.ENDC}\n")
        last_mtimes = {}
        try:
            while True:
                changed = False
                for mod in parse_hub_modules():
                    p = os.path.join(WORKSPACE_DIR, mod["file"].replace('/', os.sep))
                    if os.path.exists(p):
                        mtime = os.path.getmtime(p)
                        if mod["file"] in last_mtimes and last_mtimes[mod["file"]] != mtime:
                            print(f"{Colors.CYAN}⚡ Змінено:{Colors.ENDC} {mod['file']} ({datetime.now().strftime('%H:%M:%S')})")
                            changed = True
                        last_mtimes[mod["file"]] = mtime
                if changed:
                    print_terminal_report(run_suite_audit())
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Вартового зупинено.{Colors.ENDC}")
            return

    results = run_suite_audit()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print_terminal_report(results)

    if args.check:
        all_perfect = len(results) > 0 and all(r.get("is_perfect", False) for r in results)
        sys.exit(0 if all_perfect else 1)


if __name__ == "__main__":
    main()
