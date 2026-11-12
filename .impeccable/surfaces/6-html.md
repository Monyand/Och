---
version: 1
slug: "6-html"
primary_target: "Додаток 6.html"
related_targets: []
---

# Surface Brief: Додаток 6.html

MODE: operate
FORM: Відомість та експлікація (Graphite Matte Dark Schedule) · seed:b7e2878a40e65bbe · reference:DESIGN.md

## 1. Job and Audience
Duty officers and unit personnel clerks collecting daily combat duty rosters (PBD/Appendix 2 reports from companies and attached units or monthly Appendix 6 archives) into Appendix 6 operational categories (ВОП 270, РОП 170, БРО 100, Заб. БД 30, Уточнення) and generating verified Excel/Word deliverables offline at 100–175% browser zoom.

## 2. Visual Direction — Графітова матова «Відомість»
- **Always-Dark Matte Palette:** Canvas `#111418`, panels `#181c22`, header/table/band surfaces `#20262f`, recessed controls/dropzone/inputs `#151920` / `#0e1218`, title block stamp `#141922` with `#0a0d12` `2px` bottom rule. Zero light-mode branch, zero OLED `#0b0b0b`, zero `backdrop-blur`, zero neon/glow shadows.
- **Hierarchy & Borders:** Sharp `1px solid #2b3340` / `#222933` borders, `rounded-[2px]` technical corners, flattened cardless sections via hairline dividers, `tabular-nums` for counts/dates/indices.
- **Accents & State:** Primary cerulean text/line accent `#4c8ed9`, primary action buttons `#2b67ab` (`hover:#245791`) with `#f4f6f8` ink (`>= 5.3:1`), muted operational statuses (`#4cc38a` on `#11261c`, `#f0b44c` on `#281f0f`, `#f27474` on `#2b1416`).
- **Ukrainian Operational Copy & Icons:** Calm official Ukrainian staff labels instead of legacy cyberpunk/gaming jargon; offline Lucide/SVG icons without UI emojis; native `'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif` + `'Cascadia Mono', 'Consolas', monospace`.

## 3. Preserved Interactive Mechanics & IDs
- All DOM IDs and handlers (`setAppMode`, `btn-mode-pbd`, `btn-mode-archive`, `dispatcherWidget`, `chkDispAutoSync`, `btnDispLoad`, `btnDispModal`, `drop-zone`, `fileInput`, `masterFileInput`, `blacklistFileInput`, `importPosFileInput`, `standardizeTasks`, `openDocxExportModal`, `downloadPivotReport`, `btn-merge-rop-units`, `downloadAllCategoriesExcel`, `downloadMonthlyDayTabsExcel`, `clearData`, `statusRibbonBar`, `alertDrawerPanel`, `tab-*`, `searchInput`, `vop-body`/`btgr-body`/`bro-body`/`zab-body`, `table-utoch-container`, `settingsModal`, `modal-settings-export-pwd`, `modal-settings-import-pwd`, `modal-docx-export`, `changelogModal`, `editRecordModal`, `dispatcherModal`, `toast-container`).
- Version badge remains `v2.1.1` and `CHANGELOG.md` stays untouched until explicit user commit command.
