"""
Штабний диспетчер / Агент авто-прийому звітів ПБД (Auto-Ingest Agent)
Розробник: Antigravity IDE
Призначення: Автоматичний моніторинг папок щоденних звітів, надшвидкий парсинг .docx,
виявлення дублікатів, контроль здачі підрозділами та локальний API для Додатка 6 і Звіту ПБД.
"""

import os
import sys
import json
import time
import re
import zipfile
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

# Базовий шлях до сховища завантажених звітів
BASE_DOWNLOADS_DIR = r"D:\ОЧ\гусь\Завантажені"
SERVER_PORT = 8765
XML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

UKR_MONTHS = {
    1: "січень", 2: "лютий", 3: "березень", 4: "квітень",
    5: "травень", 6: "червень", 7: "липень", 8: "серпень",
    9: "вересень", 10: "жовтень", 11: "листопад", 12: "грудень"
}

UKR_MONTHS_MAP = {
    "січ": 1, "лют": 2, "бер": 3, "кві": 4, "тра": 5, "чер": 6,
    "лип": 7, "сер": 8, "вер": 9, "жов": 10, "лис": 11, "гру": 12
}


def parse_date_key(d_str, m_folder=""):
    """
    Повертає ISO-рядок дати 'YYYY-MM-DD' для точного хронологічного сортування та JSON-безпеки.
    """
    now = datetime.datetime.now()
    d_clean = (d_str or "").strip()

    # 1. Пошук повної дати DD.MM.YYYY або DD.MM.YY
    m_full = re.search(r'(\d{1,2})[\.\-_/](\d{1,2})[\.\-_/](\d{2,4})', d_clean)
    if m_full:
        day = int(m_full.group(1))
        month = int(m_full.group(2))
        yr = int(m_full.group(3))
        if yr < 100:
            yr += 2000
        try:
            return datetime.date(yr, month, day).isoformat()
        except ValueError:
            pass

    # 2. Пошук дати DD.MM
    m_dm = re.search(r'(\d{1,2})[\.\-_/](\d{1,2})', d_clean)
    if m_dm:
        day = int(m_dm.group(1))
        month = int(m_dm.group(2))
        try:
            return datetime.date(now.year, month, day).isoformat()
        except ValueError:
            pass

    # 3. Якщо папка - просто день "06" чи "6"
    m_day = re.search(r'\b(\d{1,2})\b', d_clean)
    if m_day:
        day = int(m_day.group(1))
        month = None
        m_lower = (m_folder or "").lower()
        for prefix, m_num in UKR_MONTHS_MAP.items():
            if prefix in m_lower:
                month = m_num
                break
        if not month:
            m_num_match = re.search(r'\b(0?[1-9]|1[0-2])\b', m_lower)
            if m_num_match:
                month = int(m_num_match.group(1))
            else:
                month = now.month
        try:
            return datetime.date(now.year, month, day).isoformat()
        except ValueError:
            pass

    return "1970-01-01"


EXPECTED_UNITS = [
    {"id": "4mr", "name": "4 мр"},
    {"id": "5mr", "name": "5 мр"},
    {"id": "6mr", "name": "6 мр"},
    {"id": "rv", "name": "Розвідувальний взвод (РВ)"},
    {"id": "rbpak", "name": "Рота БпАК (РБпАК)"},
    {"id": "mb", "name": "Мінометна батарея (МБ)"},
    {"id": "bg", "name": "Бронегрупа (БнГ)"},
    {"id": "vptrk", "name": "Взвод ПТРК"},
    {"id": "gv", "name": "Гранатометний взвод (ГВ)"},
    {"id": "isv", "name": "Інженерно-саперний взвод (ІСВ)"},
    {"id": "vz", "name": "Взвод зв'язку (ВЗ)"},
    {"id": "vo", "name": "Взвод охорони (ВО)"},
    {"id": "vmz", "name": "Взвод матзабезпечення (ВМЗ)"},
    {"id": "vtz", "name": "Взвод техзабезпечення (ВТЗ)"},
    {"id": "mp", "name": "Медичний пункт (МП)"},
    {"id": "vrb", "name": "Взвод РЕБ / РБ"},
    {"id": "kv", "name": "Комендантський взвод (КВ)"},
    {"id": "nrk", "name": "НРК"},
    {"id": "upr", "name": "Управління"},
    {"id": "pridani", "name": "Придані підрозділи"}
]


def classify_unit(filename):
    """Точна ідентифікація підрозділу з урахуванням армійських скорочень."""
    clean = clean_unit_name(filename).lower()
    tokens = clean.split()

    if 'ісв' in tokens or 'ісв' in clean or 'сапер' in clean: return 'isv'
    if 'вмз' in tokens or 'вмз' in clean or 'матзабезп' in clean: return 'vmz'
    if 'втз' in tokens or 'втз' in clean or 'техзабезп' in clean: return 'vtz'
    if 'вптрк' in tokens or 'вптрк' in clean or 'птрк' in clean: return 'vptrk'
    if 'врб' in tokens or 'врб' in clean or 'реб' in clean: return 'vrb'
    if 'рбпак' in tokens or 'рбпак' in clean or 'бпак' in clean: return 'rbpak'
    if 'рв' in tokens or 'розвід' in clean: return 'rv'
    if 'гв' in tokens or 'гранатомет' in clean: return 'gv'
    if 'вз' in tokens or "зв'яз" in clean or 'звязку' in clean: return 'vz'
    if 'во' in tokens or 'охорон' in clean: return 'vo'
    if 'кв' in tokens or 'комендант' in clean: return 'kv'
    if 'мп' in tokens or 'медпункт' in clean or 'медичн' in clean: return 'mp'
    if 'нрк' in tokens or 'нрк' in clean: return 'nrk'
    if 'придан' in clean or 'прид' in clean: return 'pridani'
    if 'упр' in tokens or 'управління' in clean or 'штаб' in clean: return 'upr'
    if 'броне' in clean or 'бнг' in tokens or 'бро' in tokens or 'бронегрупа' in clean: return 'bg'
    if '4' in clean and 'мр' in clean: return '4mr'
    if '5' in clean and 'мр' in clean: return '5mr'
    if '6' in clean and 'мр' in clean: return '6mr'
    if 'мінбат' in clean or 'міномет' in clean or 'мб' in tokens: return 'mb'
    return None


def clean_unit_name(filename):
    """Очищення та нормалізація назви підрозділу з імені файлу."""
    s = os.path.splitext(filename)[0]
    # Видалення дат
    s = re.sub(r'[\s_\-]*\(?\d{1,2}[\.\-_/]\d{1,2}([\.\-_/]\d{2,4})?р?\)?', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'[\s_\-]*\(?202\d[\.\-_/]\d{1,2}[\.\-_/]\d{1,2}р?\)?', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'[\s_\-]*\(?202\dр?\.?\)?', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'[\s_\-]*\(коп[іп]я\d*\)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[\s_\-]*\(\d+\)', '', s)

    # Заміна латинських гомогліфів
    homoglyphs = {
        'a': 'а', 'b': 'б', 'c': 'с', 'e': 'е', 'h': 'н', 'i': 'і',
        'k': 'к', 'm': 'м', 'o': 'о', 'p': 'р', 't': 'т', 'x': 'х', 'y': 'у'
    }
    s = "".join(homoglyphs.get(ch.lower(), ch.lower()) for ch in s)

    # Видалення позначок коригування
    s = re.sub(r'[\s_\-\(\[]*(корег[а-яієїґ0-9]*|кориг[а-яієїґ0-9]*|скориг[а-яієїґ0-9]*|скорег[а-яієїґ0-9]*|уточнен[а-яієїґ0-9]*|виправлен[а-яієїґ0-9]*|доопрацьован[а-яієїґ0-9]*|перероблен[а-яієїґ0-9]*|змінен[а-яієїґ0-9]*|корекці[а-яієїґ0-9]*|правк[а-яієїґ0-9]*|фінал[а-яієїґ0-9]*|редагован[а-яієїґ0-9]*|новий|нова|нове|нові)[\s_\-\)\]]*', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'(^|[^a-zа-яієїґ0-9])(пбд|щбд)([^a-zа-яієїґ0-9]|$)', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'([0-9])([a-zа-яієїґ])', r'\1 \2', s, flags=re.IGNORECASE)
    s = re.sub(r'([a-zа-яієїґ])([0-9])', r'\1 \2', s, flags=re.IGNORECASE)
    s = re.sub(r'[\.\-_/]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def is_corrected_file(filename):
    """Визначає, чи є файл корегованою / уточненою версією."""
    fn_lower = filename.lower()
    return bool(re.search(r'(корег|кориг|скориг|уточнен|виправлен|доопрац|правк|версія|v\d)', fn_lower))


class IngestDispatcher:
    def __init__(self, base_dir=BASE_DOWNLOADS_DIR):
        self.base_dir = base_dir
        self.target_date = None
        self.target_folder = None
        self.cached_bundle = None
        self.last_parsed_time = 0
        self.last_folder_mtime = 0
        self.manual_override = False
        self.lock = threading.Lock()
        self.auto_discover_latest_folder()

    def find_available_dates(self):
        """Знаходить усі доступні дати у папках місяців із гнучким пошуком підпапок та хронологічним сортуванням."""
        dates = []
        if not os.path.exists(self.base_dir):
            return dates

        try:
            month_dirs = sorted([d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))], reverse=True)
        except Exception:
            return dates

        for m_dir in month_dirs:
            m_path = os.path.join(self.base_dir, m_dir)
            try:
                day_dirs = [d for d in os.listdir(m_path) if os.path.isdir(os.path.join(m_path, d))]
            except Exception:
                continue

            for d_dir in day_dirs:
                day_path = os.path.join(m_path, d_dir)
                pbd_dir = os.path.join(day_path, "ПБД", "ПБД підрозділів")

                # Гнучкий вибір папки зі звітами:
                chosen_dir = None
                if os.path.exists(pbd_dir):
                    chosen_dir = pbd_dir
                else:
                    alt_pbd = os.path.join(day_path, "ПБД")
                    if os.path.exists(alt_pbd) and any(f.lower().endswith(('.docx', '.xlsx')) for f in os.listdir(alt_pbd) if not f.startswith('~$')):
                        chosen_dir = alt_pbd
                    elif any(f.lower().endswith(('.docx', '.xlsx')) for f in os.listdir(day_path) if not f.startswith('~$')):
                        chosen_dir = day_path

                if chosen_dir:
                    try:
                        file_cnt = len([f for f in os.listdir(chosen_dir) if f.lower().endswith(('.docx', '.xlsx')) and not f.startswith('~$')])
                    except Exception:
                        file_cnt = 0

                    parsed_d = parse_date_key(d_dir, m_dir)
                    dates.append({
                        "date": d_dir,
                        "month_folder": m_dir,
                        "folder_path": chosen_dir,
                        "file_count": file_cnt,
                        "parsed_date": parsed_d,
                        "mtime": os.path.getmtime(chosen_dir) if os.path.exists(chosen_dir) else 0
                    })

        # Хронологічне сортування від найновіших до старіших
        dates.sort(key=lambda x: (x["parsed_date"], x["date"]), reverse=True)
        return dates

    def auto_discover_latest_folder(self, target_date=None, force_auto=False):
        """
        Знаходить цільову папку з урахуванням системного часу та наявних дат:
        - Якщо задано target_date -> використовує її (ручний вибір).
        - Авто-режим:
            1. Вечірній час (>=16:00): перевіряє наявність папки на завтра (наприклад 06.09).
            2. Шукає папку на сьогодні (05.09).
            3. Якщо є новіша папка з файлами (наприклад 06.09), перемикається на неї.
            4. За замовчуванням бере найсвіжішу за хронологією.
        """
        available = self.find_available_dates()
        if not available:
            self.target_folder = None
            self.target_date = None
            return None

        if target_date and not force_auto:
            for item in available:
                if item["date"] == target_date:
                    self.target_date = item["date"]
                    self.target_folder = item["folder_path"]
                    return self.target_folder

        now = datetime.datetime.now()
        today_iso = now.date().isoformat()
        tomorrow_iso = (now.date() + datetime.timedelta(days=1)).isoformat()

        target_item = None

        # 1. Вечірній штабний режим (>=16:00): якщо вже з'явилася папка на завтра
        if now.hour >= 16:
            for item in available:
                if item.get("parsed_date") == tomorrow_iso:
                    target_item = item
                    break

        # 2. Якщо не вечір або завтрашньої папки ще немає — шукаємо сьогоднішню
        if not target_item:
            for item in available:
                if item.get("parsed_date") == today_iso:
                    target_item = item
                    break

        # 3. Якщо папки на сьогодні/завтра немає, беремо найсвіжішу
        if not target_item:
            target_item = available[0]
        else:
            # Якщо є ще новіша папка, і в ній уже є файли (або настав вечір)
            newest = available[0]
            if newest.get("parsed_date", "") > target_item.get("parsed_date", ""):
                if newest.get("file_count", 0) > 0 or now.hour >= 16:
                    target_item = newest

        self.target_date = target_item["date"]
        self.target_folder = target_item["folder_path"]
        return self.target_folder

    def parse_docx(self, file_path):
        """Швидкий парсинг .docx через zipfile + ElementTree без сторонніх бібліотек."""
        records = []
        filename = os.path.basename(file_path)
        try:
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)

            def get_cell_text(tc):
                p_texts = []
                for p in tc.findall('.//w:p', XML_NS):
                    parts = []
                    for child in p.iter():
                        if child.tag == f"{{{XML_NS['w']}}}t" and child.text:
                            parts.append(child.text)
                        elif child.tag == f"{{{XML_NS['w']}}}br":
                            parts.append(" ")
                    pt = "".join(parts).strip()
                    if pt:
                        p_texts.append(pt)
                return " ".join(p_texts).strip()

            tables = tree.findall('.//w:tbl', XML_NS)
            for tbl in tables:
                rows = tbl.findall('.//w:tr', XML_NS)
                col_map = None

                for r in rows[:4]:
                    cells = [get_cell_text(c).lower() for c in r.findall('.//w:tc', XML_NS)]
                    row_txt = " ".join(cells)
                    if 'звання' in row_txt and ('піб' in row_txt or 'прізвище' in row_txt or "ім'я" in row_txt):
                        col_map = {}
                        for idx, c in enumerate(cells):
                            if 'звання' in c: col_map['rank'] = idx
                            if 'піб' in c or 'прізвище' in c or "ім'я" in c: col_map['name'] = idx
                            if 'посада' in c: col_map['pos'] = idx
                            if any(k in c for k in ['завдання', 'місце', 'позиці', 'розташування', 'статус']): col_map['task'] = idx
                        break

                if not col_map:
                    col_map = {'rank': 0, 'name': 1, 'pos': 2, 'task': 3}

                for r in rows:
                    cells = [get_cell_text(c) for c in r.findall('.//w:tc', XML_NS)]
                    if len(cells) < 3:
                        continue

                    row_txt = " ".join(cells).lower()
                    if 'звання' in row_txt and ('піб' in row_txt or 'прізвище' in row_txt):
                        continue

                    # Обробка колонки номера
                    r_idx = col_map.get('rank', 0)
                    n_idx = col_map.get('name', 1)
                    p_idx = col_map.get('pos', 2)
                    t_idx = col_map.get('task', 3)

                    rank = cells[r_idx] if r_idx < len(cells) else ""
                    name = cells[n_idx] if n_idx < len(cells) else ""
                    pos = cells[p_idx] if p_idx < len(cells) else ""
                    task = cells[t_idx] if t_idx < len(cells) else ""

                    # Якщо в колонці звання стоїть просто порядковий номер
                    if re.match(r'^\d+[\.\)]?$', rank) and len(cells) >= 4:
                        rank = cells[1]
                        name = cells[2]
                        pos = cells[3] if len(cells) > 3 else ""
                        task = cells[4] if len(cells) > 4 else ""

                    clean_name = " ".join(name.split())
                    if clean_name and len(clean_name) > 3 and not clean_name.lower().startswith(('піб', 'прізвище')):
                        # Перевірка, що це не назва військового звання замість ПІБ
                        military_ranks = ['солдат', 'сержант', 'офіцер', 'лейтенант', 'капітан', 'майор', 'підполковник', 'полковник', 'старшина']
                        if clean_name.lower() in military_ranks and not pos:
                            continue

                        records.append({
                            "rank": rank.strip(),
                            "name": clean_name,
                            "pos": pos.strip(),
                            "task": task.strip(),
                            "fileName": filename
                        })
        except Exception as e:
            print(f"[ПОМИЛКА] Читання {filename}: {e}")
        return records

    def build_bundle(self, force=False):
        """Формує повний структурований пакет даних для поточної дати."""
        with self.lock:
            if not self.target_folder or not os.path.exists(self.target_folder):
                return {
                    "status": "folder_not_found",
                    "target_date": self.target_date,
                    "target_folder": self.target_folder,
                    "files": [],
                    "total_soldiers": 0,
                    "units_status": [],
                    "duplicates": []
                }

            folder_mtime = os.path.getmtime(self.target_folder)
            if not force and self.cached_bundle and (folder_mtime == self.last_folder_mtime):
                return self.cached_bundle

            all_file_names = [f for f in os.listdir(self.target_folder) if f.lower().endswith(('.docx', '.xlsx')) and not f.startswith('~$')]
            
            # 1. Розпізнавання корегованих версій (виявлення дублікатів файлів)
            unit_files_map = {}
            for fn in all_file_names:
                base_u = clean_unit_name(fn)
                is_corr = is_corrected_file(fn)
                fp = os.path.join(self.target_folder, fn)
                mtime = os.path.getmtime(fp)
                if base_u not in unit_files_map:
                    unit_files_map[base_u] = []
                unit_files_map[base_u].append({
                    "fileName": fn,
                    "filePath": fp,
                    "isCorrected": is_corr,
                    "mtime": mtime
                })

            active_files = []
            superseded_files = []

            for base_u, file_list in unit_files_map.items():
                if len(file_list) == 1:
                    active_files.append(file_list[0])
                else:
                    file_list.sort(key=lambda x: (1 if x["isCorrected"] else 0, x["mtime"]), reverse=True)
                    active_files.append(file_list[0])
                    for sup in file_list[1:]:
                        superseded_files.append({
                            "fileName": sup["fileName"],
                            "supersededBy": file_list[0]["fileName"],
                            "reason": "Замінено свіжішою або корегованою версією"
                        })

            # 2. Швидкий парсинг усіх активних файлів
            t0 = time.time()
            parsed_files = []
            all_soldiers_registry = {}
            total_soldiers = 0

            for f_info in sorted(active_files, key=lambda x: x["fileName"]):
                fn = f_info["fileName"]
                fp = f_info["filePath"]
                records = self.parse_docx(fp)
                parsed_files.append({
                    "fileName": fn,
                    "unitNormalized": clean_unit_name(fn),
                    "isCorrected": f_info["isCorrected"],
                    "mtime": f_info["mtime"],
                    "recordsCount": len(records),
                    "records": records
                })
                total_soldiers += len(records)

                for r in records:
                    norm_n = re.sub(r'\s+', ' ', r["name"].strip().lower())
                    if norm_n not in all_soldiers_registry:
                        all_soldiers_registry[norm_n] = []
                    all_soldiers_registry[norm_n].append({
                        "name": r["name"],
                        "rank": r["rank"],
                        "pos": r["pos"],
                        "task": r["task"],
                        "fileName": fn
                    })

            # 3. Виявлення міжпідроздільних перетинів (дублікатів бійців)
            cross_unit_duplicates = []
            for norm_n, entries in all_soldiers_registry.items():
                if len(entries) > 1:
                    distinct_files = set(e["fileName"] for e in entries)
                    if len(distinct_files) > 1:
                        cross_unit_duplicates.append({
                            "name": entries[0]["name"],
                            "occurrencesCount": len(entries),
                            "files": list(distinct_files),
                            "entries": entries
                        })

            # 4. Шаховка підрозділів
            units_status = []
            for exp in EXPECTED_UNITS:
                matched_file = None
                for pf in parsed_files:
                    c_id = classify_unit(pf["fileName"])
                    if c_id == exp["id"]:
                        matched_file = pf["fileName"]
                        break

                units_status.append({
                    "id": exp["id"],
                    "name": exp["name"],
                    "submitted": bool(matched_file),
                    "fileName": matched_file or None
                })

            elapsed = time.time() - t0

            bundle = {
                "status": "ready",
                "timestamp": datetime.datetime.now().isoformat(),
                "target_date": self.target_date,
                "target_folder": self.target_folder,
                "parse_duration_sec": round(elapsed, 3),
                "total_files": len(parsed_files),
                "total_soldiers": total_soldiers,
                "active_files": parsed_files,
                "superseded_files": superseded_files,
                "cross_unit_duplicates": cross_unit_duplicates,
                "units_status": units_status
            }

            self.cached_bundle = bundle
            self.last_folder_mtime = folder_mtime
            self.last_parsed_time = time.time()
            return bundle


dispatcher = IngestDispatcher()


class DispatcherHTTPHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/status':
            bundle = dispatcher.build_bundle()
            resp = {
                "status": bundle["status"],
                "target_date": bundle.get("target_date"),
                "target_folder": bundle.get("target_folder"),
                "is_auto_mode": not dispatcher.manual_override,
                "total_files": bundle.get("total_files", 0),
                "total_soldiers": bundle.get("total_soldiers", 0),
                "duplicates_count": len(bundle.get("cross_unit_duplicates", [])),
                "missing_units": [u["name"] for u in bundle.get("units_status", []) if not u["submitted"]],
                "parse_duration_sec": bundle.get("parse_duration_sec", 0),
                "timestamp": bundle.get("timestamp")
            }
            self.send_json(resp)

        elif path == '/api/bundle':
            bundle = dispatcher.build_bundle()
            self.send_json(bundle)

        elif path == '/api/dates':
            dates = dispatcher.find_available_dates()
            self.send_json({"available_dates": dates, "current_date": dispatcher.target_date, "is_auto_mode": not dispatcher.manual_override})

        elif path == '/api/reload':
            bundle = dispatcher.build_bundle(force=True)
            self.send_json({"reloaded": True, "total_files": bundle.get("total_files", 0)})

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/set_date':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
            try:
                data = json.loads(body)
                req_date = data.get("date")
                if req_date == "auto" or req_date == "" or req_date is None:
                    dispatcher.manual_override = False
                    dispatcher.auto_discover_latest_folder(force_auto=True)
                    bundle = dispatcher.build_bundle(force=True)
                    self.send_json({
                        "success": True,
                        "mode": "auto",
                        "target_date": dispatcher.target_date,
                        "total_files": bundle.get("total_files", 0)
                    })
                    return
                elif req_date:
                    dispatcher.manual_override = True
                    dispatcher.auto_discover_latest_folder(target_date=req_date)
                    bundle = dispatcher.build_bundle(force=True)
                    self.send_json({
                        "success": True,
                        "mode": "manual",
                        "target_date": dispatcher.target_date,
                        "total_files": bundle.get("total_files", 0)
                    })
                    return
            except Exception as e:
                pass
            self.send_json({"success": False, "error": "Invalid date"}, code=400)
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def background_watcher():
    """
    Дворівневий надлегкий фоновий моніторинг (Tiered Watcher):
    1. Перевірка змін у поточній активній папці (додавання/коригування файлів).
    2. Перевірка кореневого каталогу на появу нових дат на льоту (0% навантаження CPU/диска).
    3. Автоматичний перехід на наступну добу при настанні нового дня або у вечірній час.
    """
    last_root_signature = None
    last_checked_day = datetime.date.today()

    while True:
        try:
            time.sleep(4)

            # --- Рівень 1: Перевірка змін файлів у поточній активній папці ---
            if dispatcher.target_folder and os.path.exists(dispatcher.target_folder):
                mtime = os.path.getmtime(dispatcher.target_folder)
                if mtime != dispatcher.last_folder_mtime:
                    print(f"[ДИСПЕТЧЕР] Зміни в папці виявлено! Оновлюю пакет {dispatcher.target_date}...")
                    dispatcher.build_bundle(force=True)
                    print(f"[ДИСПЕТЧЕР] Оновлено: {dispatcher.cached_bundle.get('total_files', 0)} файлів, {dispatcher.cached_bundle.get('total_soldiers', 0)} в/с")

            # --- Рівень 2: Виявлення нових дат на льоту (Lightweight Watcher) ---
            if not dispatcher.manual_override and os.path.exists(dispatcher.base_dir):
                current_signature = []
                try:
                    current_signature.append(os.path.getmtime(dispatcher.base_dir))
                    for entry in os.scandir(dispatcher.base_dir):
                        if entry.is_dir():
                            current_signature.append(entry.stat().st_mtime)
                except Exception:
                    pass

                sig_tuple = tuple(current_signature)
                current_today = datetime.date.today()
                day_transition = (current_today != last_checked_day)

                if sig_tuple != last_root_signature or day_transition or not dispatcher.target_folder:
                    last_root_signature = sig_tuple
                    last_checked_day = current_today

                    old_date = dispatcher.target_date
                    old_folder = dispatcher.target_folder
                    new_folder = dispatcher.auto_discover_latest_folder()

                    if new_folder and (new_folder != old_folder or dispatcher.target_date != old_date):
                        print(f"\n[ДИСПЕТЧЕР] ⚡ ВИЯВЛЕНО НОВУ ДАТУ НА ЛЬОТУ: {dispatcher.target_date}!")
                        print(f"            Робочу папку перемкнуто на: {new_folder}")
                        bundle = dispatcher.build_bundle(force=True)
                        print(f"[ДИСПЕТЧЕР] Оновлено: {bundle.get('total_files', 0)} файлів ({bundle.get('total_soldiers', 0)} о/с)\n")
        except Exception as e:
            pass


def main():
    print("=" * 70)
    print("  ШТАБНИЙ ДИСПЕТЧЕР / АГЕНТ АВТО-ПРИЙОМУ ЗВІТІВ ПБД")
    print("=" * 70)

    folder = dispatcher.target_folder
    if folder:
        print(f"[*] Знайдено робочу папку за {dispatcher.target_date}:")
        print(f"    {folder}")
        bundle = dispatcher.build_bundle(force=True)
        print(f"[+] Успішно розпарсено: {bundle['total_files']} файлів ({bundle['total_soldiers']} о/с) за {bundle['parse_duration_sec']} с.")
        if bundle["cross_unit_duplicates"]:
            print(f"[!] Виявлено міжпідроздільних перетинів: {len(bundle['cross_unit_duplicates'])}")
            for d in bundle["cross_unit_duplicates"][:3]:
                print(f"    • {d['name']} -> {', '.join(d['files'])}")
    else:
        print(f"[-] Папку звітів не знайдено у {BASE_DOWNLOADS_DIR}!")

    watcher_thread = threading.Thread(target=background_watcher, daemon=True)
    watcher_thread.start()

    server_address = ('127.0.0.1', SERVER_PORT)
    try:
        httpd = HTTPServer(server_address, DispatcherHTTPHandler)
        print(f"\n[🚀] Локальний API активний: http://127.0.0.1:{SERVER_PORT}")
        print(f"     Ендпоінти: /api/status  /api/bundle  /api/dates")
        print("[💡] Тепер відкрийте 'Додаток 6.html' або 'Звіт ПБД.html' у браузері.")
        print("     (Натисніть Ctrl+C для зупинки сервісу)\n")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Диспетчер зупинено.")
    except Exception as e:
        print(f"[!] Помилка запуску сервера: {e}")


if __name__ == '__main__':
    main()
