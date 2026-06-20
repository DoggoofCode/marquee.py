"""Swiss International Style 1950s — warm palette, grid-based, generous white space.

To retheme the entire app, edit COLORS and FONTS below.
Every other file imports from here — nothing is hardcoded elsewhere.
"""
from nicegui import ui

# ── Change colours here ───────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg":           "#FFFFFF",
    "surface":      "#F5F1E8",   # warm cream — sidebar + card surfaces
    "surface_2":    "#EDE8DE",   # slightly darker cream

    # Borders
    "border":       "#C8C0B4",   # warm gray-brown
    "border_light": "#DDD8CE",

    # Accent (single colour — Swiss restraint)
    "accent":       "#B38B6D",
    "accent_dark":  "#8C6B50",
    "accent_bg":    "rgba(179,139,109,0.08)",  # nav highlight fill
    "accent_fill":  "rgba(179,139,109,0.06)",  # chart area fill

    # Typography
    "text_primary":   "#000000",
    "text_secondary": "#525252",
    "text_muted":     "#808080",

    # Semantic
    "positive": "#2D6A4F",
    "negative": "#CC0000",

    # Sidebar aliases (point to core tokens — change core to move both)
    "sidebar_bg":          "#F5F1E8",
    "sidebar_border":      "#C8C0B4",
    "sidebar_text":        "#808080",
    "sidebar_text_active": "#000000",
    "sidebar_accent":      "#B38B6D",

    # Interactive states
    "btn_active_bg":   "#000000",
    "btn_active_text": "#FFFFFF",
}

# ── Change fonts here ─────────────────────────────────────────────────────────
FONTS = {
    "sans":    "'IBM Plex Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    "mono":    "'IBM Plex Mono', 'Courier New', monospace",
    "display": "'Climate Crisis', sans-serif",
}

_FONT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Climate+Crisis"
    "&display=swap"
)

# Material Icons uses a different endpoint — must be a <link> tag, not @import css2
_ICONS_URL = "https://fonts.googleapis.com/icon?family=Material+Icons"

# ── Chart palette (used by charts.py) ────────────────────────────────────────
CHART_PALETTE = [
    COLORS["accent"],        # warm brown
    COLORS["text_muted"],    # medium gray
    COLORS["text_primary"],  # black
    COLORS["border"],        # warm border
    COLORS["positive"],      # deep green
    COLORS["text_secondary"],
    COLORS["surface_2"],
    COLORS["negative"],
]

GLOBAL_CSS = f"""
@import url('{_FONT_URL}');

/* ── Hard reset — kill every Quasar/browser gap ─────── */
html, body {{
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
    overflow: hidden !important;
    background: {COLORS['bg']} !important;
}}

.q-layout {{
    min-height: 100vh;
    overflow: hidden !important;
}}

.q-page-container {{
    padding: 0 !important;
    padding-top: 0 !important;
}}

.q-page {{
    padding: 0 !important;
    min-height: unset !important;
}}

.nicegui-content {{
    padding: 0 !important;
}}

/* ── Base typography ─────────────────────────────────── */
* {{
    font-family: {FONTS['sans']} !important;
    -webkit-font-smoothing: antialiased;
    box-sizing: border-box;
}}

/* Restore Material Icons on icon elements overridden by * above */
.q-icon, .material-icons {{
    font-family: 'Material Icons' !important;
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}}

/* Monospace for financial figures */
.num, .q-table td {{
    font-family: {FONTS['mono']} !important;
    font-variant-numeric: tabular-nums;
    font-feature-settings: 'tnum';
}}

/* ── App shell — full viewport, two-column ───────────── */
.app-shell {{
    display: flex;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    background: {COLORS['bg']};
}}

/* ── Sidebar — sticky, cream ─────────────────────────── */
.sidebar {{
    background-color: {COLORS['sidebar_bg']};
    width: 220px;
    min-width: 220px;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid {COLORS['sidebar_border']};
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
}}

/* ── Content area — scrolls independently ────────────── */
.content-area {{
    flex: 1;
    height: 100vh;
    overflow-y: auto;
    padding: 40px 48px;
    background: {COLORS['bg']};
}}

/* ── Cards ───────────────────────────────────────────── */
.card {{
    background: {COLORS['bg']};
    border: 1px solid {COLORS['border']};
    border-radius: 0;
    padding: 24px;
    transition: border-color 0.2s ease;
}}

.kpi-card {{
    background: {COLORS['bg']};
    border: 1px solid {COLORS['border']};
    border-top: 2px solid {COLORS['accent']};
    border-radius: 0;
    padding: 20px 24px;
    min-width: 160px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}

.kpi-card:hover {{
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}

/* ── Semantic colours ────────────────────────────────── */
.positive {{ color: {COLORS['positive']}; font-variant-numeric: tabular-nums; }}
.negative {{ color: {COLORS['negative']}; font-variant-numeric: tabular-nums; }}

/* ── Table ───────────────────────────────────────────── */
.q-table__container {{
    border: 1px solid {COLORS['border']};
    border-radius: 0 !important;
    box-shadow: none !important;
    overflow: hidden;
}}

.q-table th {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_muted']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    border-bottom: 1px solid {COLORS['border']};
    padding: 10px 16px;
    white-space: nowrap;
}}

.q-table td {{
    color: {COLORS['text_primary']};
    font-size: 13px;
    padding: 11px 16px;
    border-bottom: 1px solid {COLORS['border_light']};
    transition: background 0.15s ease;
}}

.q-table tr:last-child td {{
    border-bottom: none;
}}

.q-table tr:hover td {{
    background-color: {COLORS['surface']};
}}

/* ── Typography scale ────────────────────────────────── */
.page-title {{
    font-size: 22px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    letter-spacing: -0.3px;
    line-height: 1.2;
}}

.page-subtitle {{
    font-size: 13px;
    color: {COLORS['text_muted']};
    margin-top: 3px;
    letter-spacing: 0;
}}

/* ── Sidebar nav ─────────────────────────────────────── */
.nav-section-label {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {COLORS['border']};
    padding: 20px 20px 6px;
}}

/* ── Button resets ───────────────────────────────────── */
.q-btn {{
    border-radius: 0 !important;
    box-shadow: none !important;
    text-transform: none !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s ease, color 0.2s ease !important;
}}

/* ── Select ──────────────────────────────────────────── */
.q-field__control {{
    border-radius: 0 !important;
}}

.q-field--outlined .q-field__control:before {{
    border-color: {COLORS['border']} !important;
    border-radius: 0 !important;
    transition: border-color 0.2s ease !important;
}}

.q-field--outlined:hover .q-field__control:before {{
    border-color: {COLORS['accent']} !important;
}}

/* ── Dropdown chevron (CSS — no Material Icons font needed) ── */
/* Quasar rotates this element 180deg when open; ::after rotates with it */
.q-select__dropdown-icon {{
    font-size: 0 !important;
    width: 20px !important;
    height: 20px !important;
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    color: {COLORS['text_muted']};
}}
.q-select__dropdown-icon::after {{
    content: '';
    display: block;
    width: 6px;
    height: 6px;
    border-right: 1.5px solid currentColor;
    border-bottom: 1.5px solid currentColor;
    transform: rotate(45deg);
    margin-top: -3px;
}}
.q-field--focused .q-select__dropdown-icon {{
    color: {COLORS['accent']};
}}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 0; }}
::-webkit-scrollbar-thumb:hover {{ background: {COLORS['accent']}; }}

/* ── Mobile block ────────────────────────────────────── */
#mobile-block .mobile-wordmark {{
    font-family: {FONTS['display']} !important;
}}

#mobile-block {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: {COLORS['surface']};
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px 32px;
}}

@media (max-width: 768px) {{
    #mobile-block {{
        display: flex;
    }}
    .app-shell {{
        display: none !important;
    }}
}}
"""


_MOBILE_BLOCK_HTML = f"""
<div id="mobile-block">
  <div class="mobile-wordmark" style="font-size:28px;color:{COLORS['text_primary']};margin-bottom:16px">Marquee</div>
  <div style="font-size:15px;font-weight:600;color:{COLORS['text_primary']};margin-bottom:8px">Desktop only</div>
  <div style="font-size:13px;color:{COLORS['text_muted']};line-height:1.7;max-width:280px">
    Marquee is not available on mobile. Please open it on a desktop or laptop browser.
  </div>
</div>
"""


def apply() -> None:
    ui.add_head_html(f'<link rel="stylesheet" href="{_ICONS_URL}">')
    ui.add_head_html(f"<style>{GLOBAL_CSS}</style>")
    ui.add_body_html(_MOBILE_BLOCK_HTML)
