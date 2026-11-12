# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Duty officers, staff clerks, and unit coordinators working in office or headquarters rooms with variable lighting on 1080p+ desktop monitors (frequently at 125–150% browser zoom) during extended sessions with operational tables, rosters, calculations, and Excel/Word reports.

## Product Purpose

An offline-first suite of 18 standalone HTML tools coordinated through a single launcher hub (`index.html`), used to process combat duty rosters, Appendix 6 movements and rotations, personnel audits, equipment formatting, losses, and operational journals. Success means fast visual scanning, reliable legibility under zoom without layout shifts or horizontal clipping, and accurate generation/parsing of local Excel and Word deliverables without internet access.

## Positioning

Self-contained zero-backend browser utilities packaged as single `.html` files backed by local `v8/` libraries (`tailwind.js`, `lucide.js`, `xlsx.js`, `docx.js`, `jszip.min.js`) and an optional local Windows dispatcher (`127.0.0.1:8780/health`), allowing duty staff to open, filter, edit, and export sensitive operational documents strictly offline.

## Operating Context

- Primary workspace: desktop browsers in headquarters/office environments; extended table reading, filtering, verification against `.xlsx`/`.docx` schedules, and rapid switching between tools from `index.html`.
- Zoom & viewport conditions: 125–175% browser zoom is routine; right-edge popovers/dropdowns must open inward (`right-0`), modals must sit at elevated stacking contexts (`z-[200]` / `z-[210]`), and toolbars must remain structurally stable without wrapping regressions.
- Rollout scope: shared suite-level identity anchored in `PRODUCT.md` and `DESIGN.md` at repository root (`d:\ОЧ\Програми`), starting with `index.html` (HUB), followed first by `Ротації (дод6).html`, and progressively extending across the remaining standalone tools.

## Capabilities and Constraints

- **Offline runtime (hard constraint):** Every `.html` application must operate standalone without internet requests; external fonts or CDNs cannot be relied upon at runtime (`v8/` local scripts take priority).
- **Preserved HUB mechanics (`index.html`):** Session password lock (`#login-screen`, `sessionStorage.hub_unlocked`), live dispatcher status badge (`http://127.0.0.1:8780/health`), live card search (`filterApps`, `Ctrl+K`, `/`, `Escape`), direct launch and `.html` file download actions, header quick links (`audit_dashboard.html`, `Кіберзахист.html`), and explicit card metadata sync (`version`, release date, tags, Changelog modal).
- **Content & language:** Ukrainian Cyrillic UI (`uk-UA`) with tabular numerals (`tabular-nums`) for counts, dates, identifiers, and schedules; clean SVG icons only (no emoji icons).
- **Architecture & workspace hygiene:** Standalone `.html` files without build bundlers or temporary workspace helper scripts; git commits and version bumps occur only on explicit user commit request.

## Brand Commitments

Shared workspace name **ТАКТ-ОБЛІК / HUB ОЧ** (`index.html` as entry point across all modules). No binding legacy palette or font family beyond Ukrainian Cyrillic support, `tabular-nums`, and clean operational clarity.

## Evidence on Hand

- Workspace launcher: `index.html` (16 module tiles, login gate, dispatcher health check, search shortcuts).
- Prioritized first operational module after HUB: `Ротації (дод6).html` (`v1.6.0`).
- Local offline runtime bundle: `v8/` (`tailwind.js`, `lucide.js`, `xlsx.js`, `docx.js`, `jszip.min.js`).
- Suite documentation and rules: `AGENTS.md`, `CHANGELOG.md`.

## Product Principles

1. **Legibility over ornament:** Long multi-hour work with rosters and operational tables demands calm surface contrast, clear hierarchy, and zero visual fatigue from glows, gradients, or decorative motion.
2. **Offline certainty:** Every layout, font stack, icon, and script must degrade gracefully and render cleanly with zero external network access.
3. **Zoom-proof operational density:** Controls, filters, summary counters, and dropdowns keep aligned multi-row structure and strict viewport bounds up to 175% zoom.
4. **Cohesive suite grammar:** `index.html` and downstream tools (`Ротації (дод6).html` and siblings) share one unified, unmistakably non-template visual language instead of generic card-grid AI defaults.

## Accessibility & Inclusion

Full Ukrainian Cyrillic legibility, minimum WCAG AA contrast (4.5:1 body text, 3:1 UI/large text), full keyboard navigation (`Ctrl+K`, `/`, `Escape`, focus-visible rings), native scrollbar/text-selection preservation, and `rem`-based scaling compatible with 125–200% zoom.

