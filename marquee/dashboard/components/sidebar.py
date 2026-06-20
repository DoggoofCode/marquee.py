from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional
from nicegui import ui
from marquee.dashboard.theme import COLORS, FONTS


def _format_synced_at(synced_at: Optional[datetime]) -> str:
    if synced_at is None:
        return "never"
    delta = datetime.utcnow() - synced_at
    mins = int(delta.total_seconds() / 60)
    if mins < 1:
        return "just now"
    if mins == 1:
        return "1 min ago"
    if mins < 60:
        return f"{mins} mins ago"
    hours = mins // 60
    return f"{hours}h ago"


_NAV_ICONS = {
    "overview":  "dashboard",
    "positions": "account_balance_wallet",
    "history":   "show_chart",
    "settings":  "tune",
}


def _nav_item(current_page: str, page_id: str, label: str) -> None:
    is_active = current_page == page_id
    left_border = f"border-left:2px solid {COLORS['sidebar_accent']}" if is_active else "border-left:2px solid transparent"
    bg = f"background:{COLORS['accent_bg']}" if is_active else "background:transparent"
    text_color = COLORS["text_primary"] if is_active else COLORS["sidebar_text"]
    icon_color = COLORS["accent"] if is_active else COLORS["border"]
    weight = "600" if is_active else "400"

    with ui.element("div").style(
        f"display:flex; align-items:center; gap:10px; padding:9px 20px; "
        f"cursor:pointer; {left_border}; {bg}; margin:1px 0; "
        f"transition:background 0.2s ease, border-color 0.2s ease"
    ).on("click", lambda p=page_id: ui.navigate.to(f"/{p}")):
        ui.icon(_NAV_ICONS.get(page_id, "circle")).style(
            f"font-size:16px; color:{icon_color}; flex-shrink:0; "
            f"transition:color 0.2s ease"
        )
        ui.label(label).style(
            f"font-size:13px; font-weight:{weight}; color:{text_color}; "
            f"letter-spacing:0.01em; transition:color 0.2s ease"
        )


def sidebar(
    current_page: str,
    synced_at: Optional[datetime] = None,
    on_sync: Optional[Callable] = None,
) -> None:
    with ui.element("div").classes("sidebar"):
        # Brand
        with ui.element("div").style(
            f"padding:28px 20px 24px; border-bottom:1px solid {COLORS['sidebar_border']}"
        ):
            ui.label("Marquee").style(
                f"font-family:{FONTS['display']} !important; "
                f"font-size:22px; color:{COLORS['text_primary']}; line-height:1"
            )
            ui.label("Portfolio Analytics").style(
                f"font-size:11px; color:{COLORS['text_muted']}; margin-top:3px"
            )

        # Main nav
        ui.label("NAVIGATE").classes("nav-section-label")
        _nav_item(current_page, "overview",  "Overview")
        _nav_item(current_page, "positions", "Positions")
        _nav_item(current_page, "history",   "History")

        # Spacer pushes everything below to the bottom
        ui.element("div").style("flex:1")

        # Settings pinned above footer
        with ui.element("div").style(f"border-top:1px solid {COLORS['sidebar_border']}"):
            _nav_item(current_page, "settings", "Settings")

        # Footer — sync status
        with ui.element("div").style(
            f"padding:16px 20px; border-top:1px solid {COLORS['sidebar_border']}"
        ):
            ui.label("DATA SOURCE").style(
                f"font-size:9px; font-weight:700; letter-spacing:0.14em; "
                f"color:{COLORS['border']}; display:block"
            )
            ui.label(f"Synced {_format_synced_at(synced_at)}").style(
                f"font-size:11px; color:{COLORS['text_muted']}; margin-top:2px; display:block"
            )

            if on_sync is not None:
                ui.button("Sync Now").props("unelevated flat dense").style(
                    f"font-size:10px; font-weight:600; letter-spacing:0.06em; "
                    f"color:{COLORS['accent']} !important; background:transparent !important; "
                    f"border:1px solid {COLORS['border']}; border-radius:0; "
                    f"height:26px; padding:0 10px; margin-top:8px; width:100%; "
                    f"transition:border-color 0.2s ease, color 0.2s ease"
                ).on("click", on_sync)
