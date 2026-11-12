---
version: 1
slug: "index-html"
primary_target: "index.html"
related_targets: []
---

# Surface Brief: HUB (index.html)

MODE: operate
FORM: Відомість та експлікація (Technical Schedule & Title Block) · seed:b7e2878a40e65bbe · reference:.impeccable/mocks/decision/assigned.html

## 1. Job and Audience
Duty officers and staff clerks working on 1080p+ office/HQ desktop screens (frequently zoomed 125–150%, variable room light) who need immediate access to 16 operational HTML modules, rapid keyword filtering (`Ctrl+K` / `/`), live local dispatcher monitoring (`127.0.0.1:8780/health`), and session lock protection.

## 2. Selected Visual Direction & Signature Move
- **World:** Technical Drawing Schedule & Title Block (**Відомість та експлікація**), matching `.impeccable/mocks/decision/assigned.html`.
- **Palette:** Dark matte graphite ground `#111418`, schedule panels `#181c22`, table/section header band `#20262f`, recessed log/chip zone `#151920`, input `#0e1218`, title block shell `#141922` with `2px solid #0a0d12` bottom rule, hairline borders `#222933` / `#2b3340` / `#394455`, primary interactive fill `#2b67ab` (`hover:#245791`), steel-blue text accent `#4c8ed9`, body ink `#e6e8eb`, muted ink `#9ca3af`. State colors (`#4cc38a` on `#11261c`, `#f0b44c` on `#281f0f`, `#f27474` on `#2b1416`) strictly for status meaning.
- **Signature Move:** 4 grouped operational contour schedules (`01 · Додаток 6 та чергування`, `02 · Щоденні звіти та донесення`, `03 · БР, втрати та контроль`, `04 · Розрахунки та безпека`) rendered as compact hairline-ruled directory rows with fixed mono codes (`М-01`..`М-16`), format tags, clickable version badges, and direct Open/Download actions. First prioritized operational link (`М-01 Ротації (дод6)`) carries a subtle `#1d5fa7` left rail rule.
- **Typography:** Offline system Ukrainian Cyrillic sans (`'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif`) and mono (`'Cascadia Mono', 'Consolas', monospace`) with `tabular-nums`, `rem` font sizing, unitless `line-height`. Zero remote fonts.

## 3. Anti-Goals & Hard Bans
- No dark radial gradients, no glowing hover shadows, no gradient `bg-clip-text` titles, no `backdrop-blur` glass, no uniform grid of 16 identical dark icon+pill cards, no nested cards, no emoji standing in for SVG icons, no fixed text container heights clipping under 150–175% zoom.

## 4. Layout, Interactivity & Preserved Mechanics
- **Offline Runtime:** Load `v8/tailwind.js` and `v8/lucide.js` locally; gracefully guard SVG icons if needed; zero required internet requests.
- **Auth Lock Gate:** Calm, legible dark matte graphite `#login-screen` using the exact SHA-256 `CORRECT_HASH` and `sessionStorage.hub_unlocked` flow, `#password-input`, `checkPassword()`, `#error-msg`, and `lockHub()`.
- **Multi-Row Stable Chrome:** Title bar (`64px` min-block-size) + multi-row/wrap-safe search & status strip (`#appSearch`, `#clearSearchBtn`, quick contour jump/filter pills, tabular counts). Notice `.app-item` filtering hides empty contour panels automatically when searching, and reveals `#no-results` when 0 match.
- **Header & Interactive Version Badge:** Includes quick links to `audit_dashboard.html` and `Кіберзахист.html`, live `#dispatcher-status-badge` (`127.0.0.1:8780/health`), `lockHub()` button, and clickable HUB version badge (`v1.0.0` baseline until commit bump) opening an accessible `<dialog>` Changelog modal (`z-[200]`) with clean SVG icons.
- **Responsive & Zoom Adaptation:** At `1440px` desktop: 2-column contour schedule grid (`1fr 1fr`, `min-inline-size: 0`); narrows cleanly to 1-column stack under `1100px` or high browser zoom (150–175%) and single-column rows on `390px` mobile without horizontal page overflow.
