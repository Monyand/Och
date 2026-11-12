---
name: ТАКТ-ОБЛІК / HUB ОЧ
description: Графітова матова оперативна дизайн-система «Відомість та експлікація» (dark mode) для автономних офлайн-утиліт чергової служби та штабу.
colors:
  paper-graphite: "#111418"
  surface-slate: "#181c22"
  band-graphite: "#20262f"
  toolbar-graphite: "#151920"
  priority-tint: "#182230"
  shell-carbon: "#141922"
  shell-trim: "#0a0d12"
  shell-inset: "#0e1218"
  shell-stroke: "#343f50"
  ink-primary: "#e6e8eb"
  ink-secondary: "#a5adb8"
  ink-muted: "#8892a0"
  border-rule: "#2b3340"
  border-subtle: "#222933"
  border-input: "#394455"
  accent-cerulean: "#4c8ed9"
  accent-btn: "#2b67ab"
  accent-btn-hover: "#245791"
  accent-tint: "#182638"
  state-ok: "#4cc38a"
  state-warn: "#f0b44c"
  state-err: "#f27474"
typography:
  display:
    fontFamily: "'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.02em"
  title:
    fontFamily: "'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "normal"
  body:
    fontFamily: "'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
  label:
    fontFamily: "'Cascadia Mono', 'Consolas', ui-monospace, SFMono-Regular, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.04em"
rounded:
  sharp: "2px"
spacing:
  xs: "0.375rem"
  sm: "0.625rem"
  md: "0.875rem"
  lg: "1.25rem"
  xl: "1.75rem"
components:
  button-primary:
    backgroundColor: "{colors.accent-btn}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.sharp}"
    padding: "0.375rem 0.6875rem"
  button-primary-hover:
    backgroundColor: "{colors.accent-btn-hover}"
  button-shell:
    backgroundColor: "transparent"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.sharp}"
    padding: "0.375rem 0.75rem"
  input-field:
    backgroundColor: "{colors.shell-inset}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.sharp}"
    padding: "0.4375rem 0.75rem"
  schedule-panel:
    backgroundColor: "{colors.surface-slate}"
    rounded: "0px"
    padding: "0px"
---

# Design System: ТАКТ-ОБЛІК / HUB ОЧ

## Overview

**Creative North Star: "Графітова матова Відомість"**

Оперативна темна дизайн-система, побудована як матова конструкторська відомість для багатогодинної роботи з таблицями й документами в затемненому або змінно освітленому приміщенні при масштабі 100–175%. Замість сліпучого білого чи космічно-неонового темного шаблону використовує нейтральний вугільно-графітовий тон із чіткими лініями `1px`, нульовим розмиттям і нульовими світіннями тіней.

Свідомо відкинуто ознаки шаблонного «ШІ-інтерфейсу»: радіальні фонові градієнти (`#050811 -> #0f1c3f`), кольорові `box-shadow` glow, `backdrop-blur` шари, градієнтний текст та однакові закруглені плитки.

**Key Characteristics:**
- `color-scheme: dark` на `:root` та `<meta name="color-scheme" content="dark">` для коректних нативних елементів і скролбарів.
- Повна офлайн-автономність (`v8/tailwind.js`, `v8/lucide.js`, `v8/xlsx.js`, `v8/docx.js`, `v8/jszip.min.js`, системні кириличні шрифти).
- Плоскі графітові поверхні з розділенням `1px solid #2b3340` / `#222933` та кутами `0px` (панелі) / `2px` (контроли).
- `font-variant-numeric: tabular-nums` для всіх кодів, версій, дат, тривалості й підсумків.

## Colors

Нейтральна графітова шкала мінімізує втому очей і тримає контраст тексту `>= 4.5:1` без синьої засвітки.

### Primary
- **Cerulean Line / Accent (`#4c8ed9`)**: Коди модулів, текстові/контурні акценти на графіті, фокус-рамки та ліва видільна смуга пріоритетного рядка (`4.7:1+` контраст на `#181c22`).
- **Cerulean Fill (`#2b67ab`, hover `#245791`)**: Суцільна заливка основних кнопок дії («Відкрити →», «Розблокувати») зі світлим текстом `#f4f6f8` (`>= 5.3:1` контраст).

### Neutral
- **Paper Graphite (`#111418`)**: Основне матове тло сторінки (`--bg-paper`).
- **Work Slate (`#181c22`)**: Робоча поверхня панелей, таблиць і карток рядків (`--bg-surface`).
- **Band Graphite (`#20262f`)**: Заголовки контурів, шапки таблиць, футер та фон бейджів версій (`--bg-band`).
- **Toolbar Graphite (`#151920`)**: Фільтраційні панелі й смуги статистики (`--bg-toolbar`).
- **Shell Carbon (`#141922`, trim `#0a0d12`, inset `#0e1218`)**: Верхня панель-штамп і поля вводу.
- **Ink Primary (`#e6e8eb`) / Secondary (`#a5adb8`) / Muted (`#8892a0`)**: Читабельна текстова ієрархія з контрастом `>= 4.5:1`.
- **Hairline Rules (`#2b3340` / `#222933` / `#394455`)**: Чіткі межі секцій, рядків і полів без тіней.

### Semantic Status
- **Active Green (`#4cc38a`, dot `#34a86e`, bg `#11261c`, border `#265c41`)**: Виключно живий статус `:8780` або норма.
- **Warning Amber (`#f0b44c`, dot `#d99b26`, bg `#281f0f`, border `#6e4e16`)**: Пороги уваги (50–59 діб ротації), відключена служба чи попередження.
- **Critical Carmine (`#f27474`, bg `#2b1416`, border `#7c2a30`)**: Критичні пороги (60+ діб), помилки вводу чи тривога.

### Named Rules
**Правило матової чіткості.** Ніяких світінь (`glow`), градієнтів фону чи прозорого скла — лише чіткі матові графітові тони й межі `1px`.

## Typography

**Display & Body Font:** `'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif`
**Mono & Index Font:** `'Cascadia Mono', 'Consolas', ui-monospace, SFMono-Regular, monospace`

### Hierarchy
- **Display (`<h1>` `.brand-title`)** (`700`, `1.5rem`, `line-height: 1.2`): Назва модуля/HUB у верхньому штампі шапки.
- **Title (`.module-name` / `h2` діалогу)** (`700`, `0.9375rem–1.125rem`, `line-height: 1.35`): Заголовки позицій та вікон.
- **Section Header (`.contour-title`)** (`700`, `0.75rem`, `letter-spacing: 0.06em`, uppercase): Назви контурів і груп.
- **Body (`p`, таблиця)** (`400`, `0.875rem` / описи `0.75rem`, `line-height: 1.45`): Читабельний текст у `rem` одиницях.
- **Mono Index (`.mono-num`)** (`600–700`, `0.6875rem–0.75rem`, `tabular-nums`): Коди, версії, дати й лічильники.

### Named Rules
**Правило табулярних цифр.** Кожна дата, версія, код чи лічильник використовує `font-variant-numeric: tabular-nums`.

## Layout

Багаторівневий стабільний каркас (`.topbar` + 2-рядна `.toolbar` + 2-колонкова `.workspace` `repeat(2, minmax(0, 1fr))` вище `1120px` і `1fr` нижче / на високому зумі). Щільні таблиці в утилітах будуються з фіксованими/пропорційними заголовками, безпечним перенесенням тексту і без горизонтального переповнення сторінки.

## Elevation & Depth

Система **плоска без тіней (`box-shadow: none`)**. Глибина досягається п’ятьма сусідніми матовими відтінками (`#0e1218` < `#111418` < `#151920` < `#181c22` < `#20262f`) і волосними правилами `1px solid`. Нативні діалоги (`<dialog>`) відділяються затемненням `rgba(6, 9, 13, 0.72)`.

## Shapes

- **Секції, таблиці, панелі:** `border-radius: 0px`, суцільна рамка `1px solid #2b3340`.
- **Кнопки, поля, теги, бейджі:** `border-radius: 2px`.

## Components

### Buttons
- **Primary (`.btn-open`, `.btn-primary`):** Фон `#2b67ab`, текст `#f4f6f8`, hover `#245791`, `border-radius: 2px`.
- **Secondary / Shell (`.btn-shell`, `.btn-dl`):** Прозорий або `#181c22` фон з рамкою `1px solid #343f50` / `#394455`.

### Chips & Tabs
- **Filter Tabs (`.tab-btn`):** Фон `#181c22`, текст `#a5adb8`, рамка `#2b3340`; активний `[aria-pressed="true"]` — фон `#2b67ab`, рамка `#4c8ed9`, текст `#f4f6f8`.

### Inputs & Scrollbars
- **Inputs:** Фон `#0e1218`, текст `#e6e8eb`, рамка `#394455`, focus `#4c8ed9`.
- **Scrollbars:** `scrollbar-color: #4b5563 #14181f; scrollbar-width: auto;` з фолбеком `@supports not`.

## Do's and Don'ts

### Do:
- **Do** використовуй локальні файли `v8/` і системні шрифти без звернень до інтернету.
- **Do** тримай кастомний CSS поза `@layer` (або після `v8/tailwind.js`), щоб префлайт Tailwind не перезаписував поля і кнопки.
- **Do** застосовуй `right-0` для поповерів справа та `z-[200]`/`z-[210]` для модалок.

### Don't:
- **Don't** додавай `box-shadow` світіння, `backdrop-blur`, радіальні градієнти чи космічне синє тло `#0b101e`.
- **Don't** використовуй емодзі замість SVG-іконок.
- **Don't** задавай фіксований `height` на текстових елементах.
