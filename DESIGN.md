# SKAL Kütüphanesi (Dyotanya Editorial Sketchbook) — Style Reference
> Editorial sketchbook on warm paper — oversized serif statements, pasted-paper collage cards, and hand-drawn squiggles anchored in the Çiğli Sezai Karakoç Anadolu Lisesi emblem palette (`#282471` Kurumsal Lacivert & `#EC782B` Başak Turuncusu)

**Theme:** `light` (Strictly Light Mode only — `color-scheme: light !important`, zero dark mode)

Source measurements are normalized from the Dyotanya Editorial Sketchbook reference and calibrated directly to the **Çiğli Sezai Karakoç Anadolu Lisesi (SKAL)** school emblem (`logo.png` / `logo-lg.png`). Roles and recommendations are tailored for the public read-only library showcase (`/`) and mobile-first book catalog (`/search/` & `/books/`).

SKAL Kütüphanesi is an editorial literary sketchbook brought to life: a warm off-white paper canvas (`#f5f5f3`) scattered with hand-drawn thin dark-ink SVG lines (`#121124`), oversized serif headlines (`Playfair Display`) that mix roman and italic for emotional literary rhythm, and dusty indigo-navy borders (`#5c58a6`) that feel like archival fountain-pen wash. The interface avoids conventional blurry drop-shadows in favor of offset hard-shadow borders (`5px -5px 0px 0px #282471` on cards, `4px -4px 0px 0px #282471` on capsule controls) that make every book card, summary tile, and pill button feel pasted onto the sketchbook page like an archival library slip. Typography does the heavy lifting — `Playfair Display` (preserving Full Turkish diacritics `ğ, ü, ş, i, ö, ç, İ`) at up to `80px` whispers and declares in the same paragraph, while `Manrope` handles all functional catalog UI, search inputs, filter chips, and metadata at a tight geometric scale (`-0.02em` to `-0.036em`). The school emblem's wheat-wreath orange (`#ec782b`) and dusty navy-indigo borders (`#5c58a6`) provide the sole chromatic punctuation in a calm, sun-lit paper world.

## Tokens — Colors

Extracted directly from the SKAL school emblem (`logo.png`) and mapped onto the Dyotanya Editorial Sketchbook surface hierarchy:

| Name | Value | Token | Role |
|------|-------|-------|------|
| Warm Paper | `#f5f5f3` | `--color-warm-paper` | Base page canvas, warm analog sketchbook paper background, and text on dark inverted elements — replaces sterile pure white to give the entire library its tactile paper quality |
| Ink Black | `#121124` | `--color-ink-black` | Deep navy-black ink for primary text, `1.5px` hand-drawn SVG squiggle lines, primary functional borders, and icon strokes — carries primary typographic and structural information |
| Charcoal / Brand Navy | `#282471` | `--color-charcoal` / `--color-skal-navy` | Dominant school emblem navy used for offset hard-shadow borders (`5px -5px 0px 0px #282471` on cards, `4px -4px 0px 0px #282471` on pill buttons), primary filled actions, secondary text, and inverted surfaces/badges |
| Pure White | `#ffffff` | `--color-pure-white` | Elevated card surfaces, book showcase cards, search inputs, pill button surfaces, and text on dark navy/orange fills |
| Dusty Sky / Indigo Wash | `#5c58a6` | `--color-dusty-sky` | Muted emblem navy-indigo for decorative card borders (`1.5px solid #5c58a6`), search input borders, filter pill borders, and subtle archival accents — desaturated so it reads as ink wash |
| Cobalt Wash | `#3b368c` | `--color-cobalt-wash` | Deeper interactive focus/hover border accent and active control stroke when stronger chromatic presence is needed than the dusty indigo default |
| Coral / Emblem Orange | `#ec782b` | `--color-coral-link` / `--color-skal-orange` | Extracted directly from the school emblem's wheat wreath & outer ring — used for inline navigable links, active filter highlights, and overdue/attention accents |

## Tokens — Typography

### Times — System serif fallback at body and display size — appears as an instant safety net while web fonts load · `--font-times`
- **Substitute:** `'Times New Roman', Times, serif`
- **Weights:** 400
- **Sizes:** 16px
- **Line height:** 1.20
- **Role:** System serif fallback at body size — acts as a zero-CLS metric safety net for `Playfair Display`

### Playfair Display (Simeiz Role) — Display and heading serif — the signature editorial typeface · `--font-simeiz` / `--font-display`
- **Family:** `'Playfair Display', 'Times New Roman', Times, serif`
- **Weights:** 400 (Regular & Italic), 600 (SemiBold & Italic)
- **Sizes:** 16px, 18px, 24px, 30px, 46px, 48px, 80px (fluid `clamp(2.5rem, 6vw, 5rem)` on mobile-to-desktop hero)
- **Line height:** 1.00–1.56 (`1.05–1.12` on headlines to protect Turkish uppercase diacritics `İ, Ö, Ü, Ç, Ş, Ğ` and italic descenders `y, g, j, p, q`)
- **Letter spacing:** normal (`0px` to `-0.02em`)
- **Role:** Display and heading serif — the signature literary voice of SKAL Kütüphanesi. Used at up to `80px` for hero statements on the Vitrin (`/`), `46–48px` for section titles, `24–30px` for book and workflow sub-headings, and `16–18px` for editorial emphasis. Regular weight creates crisp calligraphic strokes; italic weight `400` or `600` highlights emotional and literary words within headlines (e.g. *'Sezai Karakoç'*, *'keşfedilmeyi'*, *'müsait'*). Full Turkish glyph coverage is mandatory.

### Manrope — Functional UI, body copy, search inputs, filter chips, status badges, and metadata captions · `--font-manrope` / `--font-sans`
- **Family:** `'Manrope', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Weights:** 400, 500, 600, 700
- **Sizes:** 12px, 13px, 14px, 16px, 18px
- **Line height:** 1.20–1.58
- **Letter spacing:** `-0.02em` to `-0.0360em`
- **Role:** Body text, UI labels, capsule button text, book author names, status badges (`Müsait` / `Ödünçte`), and return-date stamps (`İade Tarihi: GG.AA.YYYY`). Tighter letter-spacing at `-0.036em` provides a contemporary geometric counterpoint to the editorial serif headlines.

### Suisse Intl — Secondary geometric label token · `--font-suisse-intl`
- **Fallback:** `'Manrope', system-ui, sans-serif`
- **Weights:** 450 / 500
- **Sizes:** 14px
- **Line height:** 1.2
- **Role:** Compact metadata and micro-label alignment alongside `Manrope`

### Type Scale

| Role | Family | Weight | Size | Line Height | Letter Spacing | Token |
|------|--------|--------|------|-------------|----------------|-------|
| caption | `--font-manrope` | 500 / 600 | 12px | 1.2 | `-0.02em` | `--text-caption` |
| body-sm | `--font-manrope` | 400 / 500 | 14px | 1.2 | `-0.036em` | `--text-body-sm` |
| body | `--font-manrope` | 400 / 500 | 16px | 1.56 | `-0.036em` | `--text-body` |
| body-lg | `--font-manrope` | 400 / 500 | 18px | 1.55 | `-0.025em` | `--text-body-lg` |
| subheading | `--font-simeiz` | 400 / 600 | 24px | 1.35 | `0px` | `--text-subheading` |
| heading-sm | `--font-simeiz` | 400 / 600 | 30px | 1.33 | `0px` | `--text-heading-sm` |
| heading | `--font-simeiz` | 400 / 600 | 48px | 1.08 | `0px` | `--text-heading` |
| display | `--font-simeiz` | 400 | 80px (`clamp(2.5rem, 6vw, 5rem)`) | 1.05 | `0px` | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact-editorial (generous paper breathing room around vitrin statements; high-clarity scannable cards in mobile search)

### Spacing Scale

| Name | Value | Token |
|------|-------|-------|
| 5 | 5px | `--spacing-5` |
| 10 | 10px | `--spacing-10` |
| 12 | 12px | `--spacing-12` |
| 15 | 15px | `--spacing-15` |
| 20 | 20px | `--spacing-20` |
| 22 | 22px | `--spacing-22` |
| 48 | 48px | `--spacing-48` |

### Border Radius

| Element | Value | Notes |
|---------|-------|-------|
| body / strokes | `1.5px` | Hairline border width & SVG squiggle stroke width |
| cards | `24px–30px` | Book catalog cards, vitrin showcase cards, live metric cards |
| book covers | `16px–20px` | Rectangular vertical book cover thumbnails inside cards |
| pills / chips | `3000px` | Capsule CTA buttons, sticky search bar, filter chips, status badges |
| inline emblem | `120px` (`50%`) | Circular transparent school logo (`logo-lg.png`) inline in hero |
| inputs | `30px` (`3000px` for pill search) | Search inputs and sort selectors |
| buttons | `30px` (`3000px` for capsule CTAs) | Primary and secondary interactive triggers |

### Shadows

| Name | Value | Token | Usage |
|------|-------|-------|-------|
| subtle (Card Elevation) | `#282471 5px -5px 0px 0px` (`rgb(40, 36, 113) 5px -5px 0px 0px`) | `--shadow-subtle` | Pasted-paper hard offset shadow on all book cards, summary tiles, and showcase containers |
| subtle-2 (Control Elevation) | `#282471 4px -4px 0px 0px` (`rgb(40, 36, 113) 4px -4px 0px 0px`) | `--shadow-subtle-2` | Hard offset shadow on pill CTA buttons, sticky search capsule, and active filter chips |

### Layout

- **Page max-width:** `1200px`
- **Section gap:** `80px` (`48px–56px` on mobile `< 768px`)
- **Card padding:** `48px` on editorial Vitrin showcase cards; `20px–24px` on mobile-first catalog book cards for optimal mobile viewport density
- **Element gap:** `10px–20px`
- **Minimum touch target:** `44px × 44px` (`48px` preferred for mobile search bar, clear button, and filter chips)

## Components

### 1. Editorial Vitrin (`/`)

#### Hero Serif Statement
**Role:** Landing page (`/`) literary manifesto & instant catalog gateway

Full-width warm-paper (`#f5f5f3`) section with `Playfair Display` (`--font-simeiz`) at `clamp(2.5rem, 6vw, 5rem)` (`80px` desktop), line-height `1.05`, color `#121124`. Text flows conversationally across the canvas, mixing roman and italic within the same sentence: e.g., *"Çiğli Sezai Karakoç Anadolu Lisesi Kütüphanesi — her sayfası keşfedilmeyi bekleyen yaşayan bir düşünce defteri."* Key literary phrases (*"Sezai Karakoç"*, *"keşfedilmeyi bekleyen"*, *"düşünce defteri"*) switch to italic weight `400`/`600` for emotional emphasis. Thin `1.5px` `#121124` hand-drawn SVG curved lines weave between text fragments. The transparent circular SKAL school emblem (`logo-lg.png`, cropped/framed at `120px` radius with a `1.5px solid #121124` ring and `#ffffff` paper backing) sits inline with the headline flow.

#### Pill Quick Search Bar & Capsule CTA Button
**Role:** Primary Vitrin action & direct `/search/?q=...` entry point

Massive `3000px` border-radius capsule with `1.5px solid #121124` (or `#5c58a6` on input focus), `#ffffff` background, and hard offset shadow `4px -4px 0px 0px #282471`. Allows students to type a book title or author on `/` and jump straight into `/search/`, paired with a full-pill primary CTA button (`3000px` radius, `1.5px solid #121124`, `#ffffff` or `#282471` surface, `Manrope` weight `600`, `14px`, uppercase letter-spaced, `4px -4px 0px 0px #282471` shadow) reading `'KATALOĞU KEŞFET'` or `'KİTAP ARA'`. On `:hover` and `:active`, the button translates `2px` toward the shadow (`transform: translate(2px, -2px)`) for tactile physical feedback.

#### Live Library Summary Cards
**Role:** Real-time read-only telemetry on `/` (Toplam Eser, Rafta Müsait, Ödünçte)

White (`#ffffff`) cards with `24px–30px` border-radius, `1.5px solid #5c58a6` dusty-indigo border, and `5px -5px 0px 0px #282471` hard offset shadow. Each card displays a `01 / 02 / 03` editorial index or parenthetical caption `(Canlı Kütüphane Durumu)`, an oversized `Playfair Display` numeric count derived strictly from real database queries (zero fabricated metrics), and a `Manrope` `14px` label.

#### Featured Books Showcase & Workflow Section Index Markers (`01 / 02 / 03`)
**Role:** Curated book highlights & 3-step physical library guide

- **Featured Books Showcase:** Staggered editorial cards (`#ffffff`, `30px` radius, `1.5px solid #5c58a6` border, `5px -5px 0px 0px #282471` shadow) showcasing recently added or available books from the catalog, connected by `1.5px` hand-drawn SVG squiggle paths.
- **Section Index Marker (`01 / 02 / 03`):** Small `Playfair Display` weight `400` numerals (`01`, `02`, `03`) in `#121124` positioned at the left edge of section headers and library workflow steps (*01. Katalogdan Ara ve Durumu Gör → 02. Kütüphane Görevlisine Başvur → 03. Öğrenci Numaranla Ödünç Al ve 14 Gün İçinde İade Et*).

### 2. Mobile-First Book Search & Catalog (`/search/` and `/books/`)

#### Sticky Capsule Search Bar
**Role:** Instant mobile-first query bar (`q` parameter for book title or author)

Sticky top container on warm paper (`#f5f5f3`) housing a `3000px` radius capsule input (`#ffffff` background, `1.5px solid #5c58a6` border, focused `1.5px solid #3b368c`, `4px -4px 0px 0px #282471` hard offset shadow, minimum `48px` height). Features a search icon on the left, `Manrope` `16px` input text (`#121124`, preventing iOS auto-zoom), and a `44px × 44px` instant clear (`×`) button on the right when a query is active.

#### Horizontal Scroll-Snap Filter Chips & Sort Selector
**Role:** One-thumb mobile catalog filtering (`status`) and ordering (`sort`)

- **Filter Chips (`Tümü`, `Müsait`, `Ödünçte`):** Horizontal `scroll-snap-type: x mandatory` row with hidden scrollbar, `8px–10px` gap, and `3000px` pill chips (`min-height: 44px`, `padding: 0 20px`, `Manrope` `14px` weight `600`).
  - *Inactive state:* `#ffffff` background, `#121124` text, `1.5px solid #5c58a6` border.
  - *Active state:* `#282471` background, `#ffffff` text, `1.5px solid #121124` border, `4px -4px 0px 0px #ec782b` or `#121124` hard offset accent shadow.
- **Sort Selector:** Pill-shaped (`30px` radius) `Manrope` `14px` selector (`Yeni Eklenenler`, `Kitap Adı (A-Z)`, `Yazar (A-Z)`, `İade Tarihi Yaklaşanlar`) with `1.5px solid #5c58a6` border and `#ffffff` surface.

#### Catalog Book Card
**Role:** Primary scannable book item in `/search/` and `/books/`

White (`#ffffff`) card with `24px–30px` border-radius, `1.5px solid #5c58a6` border, `20px–24px` padding, and `5px -5px 0px 0px #282471` hard offset shadow. Designed mobile-first (horizontal media-card layout on `< 640px` or 2-to-3 column responsive grid on desktop) containing:
1. **Book Cover Thumbnail:** Rectangular vertical aspect ratio (`2:3` / `3:4`) with `16px–20px` rounded corners and `1.5px solid #121124` border. If a book has no uploaded cover, renders an intentional typographic sketchbook cover placeholder on `#f5f5f3` with the book's initials and a hand-drawn SVG book motif.
2. **Typography Hierarchy:** Book title in `Playfair Display` (`22px–26px`, line-height `1.25`, `#121124`, weight `600`) and author name in `Manrope` (`14px–15px`, `#282471`, weight `500`, parenthetical or clean subtitle).
3. **Read-Only Status Badge (`Müsait` / `Ödünçte`):** Pill badge (`3000px` radius, `1.5px` border, `Manrope` `12px` weight `700` uppercase):
   - **Müsait (`status == 'returned'`):** `#f5f5f3` or soft paper fill, `#121124` text, `1.5px solid #282471` border with a crisp navy indicator dot.
   - **Ödünçte (`status == 'approved'`):** `#282471` inverted navy fill with `#ffffff` text, or `#fff5ed` warm tint with `#ec782b` border and `#121124` text.
4. **KVKK-Safe Return Date Stamp:** When `status == 'approved'` and `due_date` is present, displays `İade Tarihi: GG.AA.YYYY` in `Manrope` `13px` weight `600` (highlighted with `#ec782b` accent icon/border). **Student full name and student number are NEVER rendered in public HTML.**

### 3. Shared Sketchbook Primitives

#### Circular Emblem Badge
**Role:** School identity mark inline with hero text and navigation header

Transparent school logo (`logo-lg.png` or `logo.png`) framed in a `120px` border-radius circle with `1.5px solid #121124` border and `#ffffff` surface, sitting inline within the hero headline or anchored in the top navigation bar.

#### Navigation Header & Mobile Trigger
**Role:** Top-level site navigation (`Vitrin`, `Kitap Ara`, `Görevli Girişi`)

Single-line header (`max-height: 76px`) on `#f5f5f3` warm paper. Contains the SKAL emblem + editorial title on the left, and pill navigation triggers (`3000px` radius, `1.5px solid #121124`, `#ffffff` background, `4px -4px 0px 0px #282471` shadow) on the right. On mobile, provides immediate 1-tap access to `/search/` without hiding search behind a menu.

#### Hand-Drawn Line Decoration
**Role:** Atmospheric connective tissue

Inline SVG paths at `1.5px` stroke `#121124`, `fill="none"`, `stroke-linecap="round"`, freely curving and looping across sections. These squiggles underline italic headline words, connect summary cards, and frame empty states — giving SKAL Kütüphanesi its signature hand-drawn sketchbook character.

#### Parenthetical Caption
**Role:** Supporting descriptive metadata

Short `Manrope` `14px` weight `400` text wrapped in literal typographic parentheses `( )`, positioned adjacent to headlines or section markers — e.g., `(Çiğli Sezai Karakoç Anadolu Lisesi Kütüphane Kataloğu)` or `(Ödünç süresi 14 gündür)`.

## Do's and Don'ts

### Do
- Enforce Light Mode exclusively (`color-scheme: light !important` on `:root` and `html`) — the warm paper `#f5f5f3` canvas is non-negotiable.
- Use `Playfair Display` (`--font-simeiz`) for all display headlines and book titles at `24px–80px` — mixing roman and italic within the same headline to create literary speech rhythm.
- Apply `3000px` border-radius to pill buttons, the sticky search bar, and filter chips to create the signature organic capsule silhouette.
- Add `5px -5px 0px 0px #282471` hard offset shadows to every card and `4px -4px 0px 0px #282471` to every pill button and search bar — this pasted-paper collage effect is the sole elevation system.
- Use `#ec782b` (SKAL Başak Turuncusu) sparingly for inline links, active accents, and return-date highlights so it retains high chromatic punch.
- Set `1.5px solid #5c58a6` (Dusty Indigo) borders on cards and inputs, and `1.5px solid #121124` (Ink Black) on primary pill buttons and SVG squiggles.
- Display only book availability (`Müsait` / `Ödünçte`) and return date (`İade Tarihi: GG.AA.YYYY`) on public cards — strictly protecting student privacy (KVKK).

### Don't
- Never implement dark mode, dark sections, or `@media (prefers-color-scheme: dark)` inversions on public pages.
- Never use soft blurry drop-shadows (`box-shadow: 0 10px 25px rgba(...)`), glassmorphism (`backdrop-filter: blur`), or neon glows — the hard offset `#282471` border shadow is the only depth technique.
- Never use `Manrope` for large display headlines above `20px` — `Playfair Display` owns all editorial headings and book titles.
- Never set border-radius below `20px` on cards or interactive controls (except rectangular book cover thumbnails at `16px–20px`).
- Never use pure white (`#ffffff`) as the base page background — `#f5f5f3` warm paper grounds the entire system.
- Never expose `student.full_name` or `student.student_number` on any public template, JSON payload, or DOM attribute.
- Never render public borrow/return POST buttons — borrowing and returning are performed exclusively by library staff in `/admin/`.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 1 | Paper | `#f5f5f3` | Base page canvas — warm analog sketchbook paper that absorbs all content |
| 2 | Card | `#ffffff` | Elevated card surfaces for book items, search capsules, and summary tiles pasted onto the warm paper canvas |
| 3 | Inverted Navy | `#282471` | High-contrast school emblem navy surface for active filter chips, primary badges, and inverted callouts |

## Elevation

- **Cards & Book Tiles:** `5px -5px 0px 0px #282471` (`--shadow-subtle`)
- **Pill Buttons, Search Capsule & Active Chips:** `4px -4px 0px 0px #282471` (`--shadow-subtle-2`)
- **Interactive Press State (`:active`):** `2px -2px 0px 0px #282471` with `transform: translate(2px, -2px)`

## Imagery

Imagery combines two intentional forms:
1. **Circular School Emblem (`logo-lg.png` / `logo.png`):** Transparent PNG framed inside a `120px` radius circle with a `1.5px solid #121124` stroke and `#ffffff` background, sitting inline within the Vitrin hero statement and in the top bar.
2. **Book Cover Thumbnails:** Unlike portfolio avatars, book covers carry essential catalog recognition and therefore use a vertical book-cover aspect ratio (`2:3` / `3:4`) with soft `16px–20px` rounded corners and a `1.5px solid #121124` ink border inside the `24px–30px` white card. When a book lacks an uploaded cover image, a custom sketchbook paper placeholder (`#f5f5f3` background, `1.5px dashed #5c58a6` inner frame, `Playfair Display` italic book title monogram, and an inline SVG open-book doodle) is rendered.
3. **Hand-Drawn 1.5px SVG Line Illustrations:** Inline SVG squiggles (`stroke="#121124"`, `stroke-width="1.5"`, `fill="none"`) weave across the hero, underline key italic words, and connect workflow steps like pen marks on tracing paper.

## Layout

The layout pairs **asymmetric editorial storytelling on the Vitrin (`/`)** with **high-clarity mobile-first ergonomics on the Catalog (`/search/` and `/books/`)**:
- **Vitrin (`/`):** A full-bleed warm-paper (`#f5f5f3`) canvas with a flowing `Playfair Display` hero statement wrapping around the inline circular SKAL emblem and hand-drawn SVG squiggles, followed immediately by a prominent `3000px` pill quick-search bar, staggered live library summary cards, a curated showcase of featured books, and the `01 / 02 / 03` physical library workflow guide.
- **Mobile-First Catalog (`/search/` and `/books/`):** Engineered from `360px` viewports upward (`min-h-[100dvh]`, `overflow-x: hidden`). A sticky search capsule and horizontal scroll-snap filter chip bar sit at the top for effortless one-thumb operation. Book cards stack cleanly on mobile and expand into a balanced 2-column (`md`) and 3-column (`lg`) grid on larger viewports within the `1200px` max-width container.

## Agent Prompt Guide

**Quick Color Reference**
- text (primary ink): `#121124`
- background (warm paper): `#f5f5f3`
- card surface: `#ffffff`
- border (decorative indigo): `#5c58a6`
- border (interactive focus): `#3b368c`
- border (functional ink): `#121124`
- link & warm emblem accent: `#ec782b`
- offset hard shadow & brand navy: `#282471`

**3 Example Component Prompts**

1. **Vitrin Hero Section (`/`)**: Warm paper `#f5f5f3` background. Display headline `'Çiğli Sezai Karakoç Anadolu Lisesi Kütüphanesi — her sayfası keşfedilmeyi bekleyen yaşayan bir düşünce defteri'` in `Playfair Display` weight 400, `clamp(2.5rem, 6vw, 5rem)`, line-height `1.05`, `#121124`. Set `'Sezai Karakoç'` and `'keşfedilmeyi bekleyen'` in italic `Playfair Display`. A `120px`-radius circular frame containing the transparent school emblem (`logo-lg.png`) sits inline with the headline text. Thin `1.5px` `#121124` SVG squiggle lines weave beneath the headline into a `3000px`-radius pill search bar with `4px -4px 0px 0px #282471` offset shadow.

2. **Mobile-First Book Catalog Card (`/search/`)**: White `#ffffff` background, `28px` border-radius, `1.5px solid #5c58a6` border, `24px` padding. Hard offset shadow `5px -5px 0px 0px #282471`. Rectangular `2:3` book cover image with `16px` border-radius and `1.5px solid #121124` border. `Playfair Display` `24px` weight 600 book title in `#121124`, `Manrope` `14px` author name in `#282471`. Bottom metadata row with a `3000px` pill badge (`Müsait` in paper/navy or `Ödünçte` in `#282471` white text) and, if borrowed, `İade Tarihi: 12.11.2026` in `Manrope` `13px` with `#ec782b` accent. Zero student personal data.

3. **Pill Navigation / Filter Button**: `3000px` border-radius capsule, `1.5px solid #121124` border, `#ffffff` background, `14px 28px` padding (`min-height: 48px`). `Manrope` `14px` weight 600, uppercase, letter-spaced, `#121124` text reading `'KATALOĞU KEŞFET'`. Hard offset shadow `4px -4px 0px 0px #282471`.

## Signature Decorative Motif

The single most recognizable visual motif of SKAL Kütüphanesi is the hand-drawn `1.5px` dark-ink (`#121124`) SVG line that weaves across sections — underlining italic literary words in the hero, looping between live library stat cards, and framing empty search states. These are structural connective tissue, never raster images. Render them as inline `<svg>` with `stroke="#121124"`, `stroke-width="1.5"`, `stroke-linecap="round"`, `fill="none"`, using organic cubic-bezier paths (`M... C...`) that feel drawn by a steady human hand on sketchbook paper.

## Typography Voice Rules

Headlines in `Playfair Display` (`--font-simeiz`) are literary conversations, not rigid banners. Every major headline alternates roman and italic within the same sentence to create natural speech rhythm: institutional or declarative statements in roman, emotional or literary emphasis in italic. For example, in *"Aradığın kitabı saniyeler içinde bul, kütüphanemizde hemen ödünç al"*, set *"saniyeler içinde"* and *"hemen ödünç al"* in italic while keeping the rest in roman. Never set an entire headline in italic; never set an entire multi-word display headline in plain roman without an italic focal phrase. Always preserve full Turkish character rendering (`ğ, ü, ş, i, ö, ç, İ`) and maintain at least `1.05–1.12` line-height so uppercase diacritics and italic descenders never clip.

## Similar Brands & Aesthetic Lineage

- **Dyotanya (dyotanya.com)** — Direct structural foundation: warm `#f5f5f3` paper canvas, pasted-paper hard offset shadows (`5px -5px 0px 0px`), `3000px` capsule pills, mixed roman/italic serif headlines, and `1.5px` hand-drawn SVG squiggles.
- **Locomotive (locomotive.ca)** — Editorial-sketchbook rhythm combining oversized mixed-roman-and-italic serif typography with hand-drawn SVG line work and muted indigo-blue strokes.
- **Rauno Freiberg (raunofreiberg.com)** — Literary display serif scale paired with tactile paper surfaces and a single warm orange-coral chromatic note.
- **Pentagram (pentagram.com)** — Hard-edge editorial card hierarchy where typography and book covers carry the visual weight with minimal UI chrome.

## Quick Start

### CSS Custom Properties

```css
:root {
  color-scheme: light !important;

  /* Colors — SKAL Emblem & Dyotanya Warm Paper Palette */
  --color-warm-paper: #f5f5f3;
  --color-ink-black: #121124;
  --color-charcoal: #282471;
  --color-skal-navy: #282471;
  --color-pure-white: #ffffff;
  --color-dusty-sky: #5c58a6;
  --color-cobalt-wash: #3b368c;
  --color-coral-link: #ec782b;
  --color-skal-orange: #ec782b;

  /* Typography — Font Families */
  --font-times: 'Times New Roman', Times, serif;
  --font-simeiz: 'Playfair Display', 'Times New Roman', Times, serif;
  --font-display: 'Playfair Display', 'Times New Roman', Times, serif;
  --font-manrope: 'Manrope', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-sans: 'Manrope', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-suisse-intl: 'Manrope', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  /* Typography — Scale */
  --text-caption: 12px;
  --leading-caption: 1.2;
  --text-body-sm: 14px;
  --leading-body-sm: 1.2;
  --text-body: 16px;
  --leading-body: 1.56;
  --text-body-lg: 18px;
  --leading-body-lg: 1.55;
  --text-subheading: 24px;
  --leading-subheading: 1.35;
  --text-heading-sm: 30px;
  --leading-heading-sm: 1.33;
  --text-heading: 48px;
  --leading-heading: 1.08;
  --text-display: clamp(2.5rem, 6vw, 5rem);
  --leading-display: 1.05;
  --tracking-display: 0px;
  --tracking-manrope: -0.036em;

  /* Typography — Weights */
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-w450: 450;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Spacing */
  --spacing-5: 5px;
  --spacing-10: 10px;
  --spacing-12: 12px;
  --spacing-15: 15px;
  --spacing-20: 20px;
  --spacing-22: 22px;
  --spacing-48: 48px;

  /* Layout */
  --page-max-width: 1200px;
  --section-gap: 80px;
  --card-padding: 48px;
  --card-padding-compact: 24px;
  --element-gap: 16px;

  /* Border Radius */
  --radius-sm: 1.5px;
  --radius-cover: 16px;
  --radius-2xl: 20px;
  --radius-card: 28px;
  --radius-3xl: 30px;
  --radius-full: 50px;
  --radius-full-2: 91px;
  --radius-full-3: 100px;
  --radius-full-4: 120px;
  --radius-full-5: 1000px;
  --radius-full-6: 3000px;
  --radius-full-7: 9999px;

  /* Named Radii */
  --radius-body: 1.5px;
  --radius-cards: 28px;
  --radius-pills: 3000px;
  --radius-images: 120px;
  --radius-inputs: 30px;
  --radius-buttons: 30px;

  /* Shadows — Pasted-Paper SKAL Navy Hard Offset */
  --shadow-subtle: rgb(40, 36, 113) 5px -5px 0px 0px;
  --shadow-subtle-2: rgb(40, 36, 113) 4px -4px 0px 0px;
  --shadow-active: rgb(40, 36, 113) 2px -2px 0px 0px;

  /* Surfaces */
  --surface-paper: #f5f5f3;
  --surface-card: #ffffff;
  --surface-inverted: #282471;
}
```

### Tailwind v4

```css
@theme {
  /* Colors */
  --color-warm-paper: #f5f5f3;
  --color-ink-black: #121124;
  --color-charcoal: #282471;
  --color-skal-navy: #282471;
  --color-pure-white: #ffffff;
  --color-dusty-sky: #5c58a6;
  --color-cobalt-wash: #3b368c;
  --color-coral-link: #ec782b;
  --color-skal-orange: #ec782b;

  /* Typography */
  --font-times: 'Times New Roman', Times, serif;
  --font-simeiz: 'Playfair Display', 'Times New Roman', Times, serif;
  --font-display: 'Playfair Display', 'Times New Roman', Times, serif;
  --font-manrope: 'Manrope', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-suisse-intl: 'Manrope', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  /* Typography — Scale */
  --text-caption: 12px;
  --leading-caption: 1.2;
  --text-body-sm: 14px;
  --leading-body-sm: 1.2;
  --text-body: 16px;
  --leading-body: 1.56;
  --text-body-lg: 18px;
  --leading-body-lg: 1.55;
  --text-subheading: 24px;
  --leading-subheading: 1.35;
  --text-heading-sm: 30px;
  --leading-heading-sm: 1.33;
  --text-heading: 48px;
  --leading-heading: 1.08;
  --text-display: 80px;
  --leading-display: 1.05;
  --tracking-display: 0px;

  /* Spacing */
  --spacing-5: 5px;
  --spacing-10: 10px;
  --spacing-12: 12px;
  --spacing-15: 15px;
  --spacing-20: 20px;
  --spacing-22: 22px;
  --spacing-48: 48px;

  /* Border Radius */
  --radius-sm: 1.5px;
  --radius-cover: 16px;
  --radius-2xl: 20px;
  --radius-card: 28px;
  --radius-3xl: 30px;
  --radius-full: 50px;
  --radius-full-2: 91px;
  --radius-full-3: 100px;
  --radius-full-4: 120px;
  --radius-full-5: 1000px;
  --radius-full-6: 3000px;
  --radius-full-7: 9999px;

  /* Shadows */
  --shadow-subtle: rgb(40, 36, 113) 5px -5px 0px 0px;
  --shadow-subtle-2: rgb(40, 36, 113) 4px -4px 0px 0px;
}
```
