from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional
from nicegui import ui
from marquee.dashboard.theme import COLORS
from marquee.dashboard.components.sidebar import sidebar


def _section_label(text: str) -> None:
    ui.label(text).style(
        f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
        f"text-transform:uppercase; color:{COLORS['text_muted']}; "
        f"margin-bottom:16px; display:block"
    )


def settings_page(
    connectors: list[dict],           # [{name, type, enabled, accounts}]
    on_toggle: Callable[[str, bool], None],
    synced_at: Optional[datetime] = None,
    on_sync: Optional[Callable] = None,
) -> None:
    with ui.element("div").classes("app-shell"):
        sidebar("settings", synced_at=synced_at, on_sync=on_sync)

        with ui.element("div").classes("content-area"):

            # ── Page header ────────────────────────────────────
            with ui.element("div").style("margin-bottom:36px"):
                ui.label("Settings").classes("page-title")
                ui.label("Manage data sources and connections").classes("page-subtitle")

            # ── Data sources ───────────────────────────────────
            _section_label("Data Sources")

            for conn in connectors:
                dot_refs: dict = {}
                label_refs: dict = {}

                with ui.element("div").style(
                    f"border:1px solid {COLORS['border']}; padding:24px; margin-bottom:1px; "
                    f"transition:border-color 0.2s ease"
                ):
                    with ui.element("div").style(
                        "display:flex; align-items:center; justify-content:space-between; gap:24px"
                    ):
                        # ── Left: identity ──────────────────────
                        with ui.element("div").style("flex:1; min-width:0"):
                            with ui.element("div").style(
                                "display:flex; align-items:center; gap:10px; margin-bottom:6px; flex-wrap:wrap"
                            ):
                                dot_color = COLORS["positive"] if conn["enabled"] else COLORS["border"]
                                dot = ui.element("div").style(
                                    f"width:7px; height:7px; border-radius:50%; "
                                    f"flex-shrink:0; background:{dot_color}; "
                                    f"transition:background 0.2s ease"
                                )
                                dot_refs["dot"] = dot

                                ui.label(conn["name"]).style(
                                    f"font-size:15px; font-weight:600; "
                                    f"color:{COLORS['text_primary']}"
                                )
                                ui.label(conn["type"]).style(
                                    f"font-size:9px; font-weight:700; letter-spacing:0.1em; "
                                    f"text-transform:uppercase; color:{COLORS['accent']}; "
                                    f"background:{COLORS['surface']}; padding:2px 8px; "
                                    f"border:1px solid {COLORS['border_light']}"
                                )

                            ui.label(", ".join(conn["accounts"])).style(
                                f"font-size:12px; color:{COLORS['text_muted']}; margin-bottom:2px"
                            )

                            status_text = "Active — will be included in next sync" if conn["enabled"] \
                                else "Inactive — excluded from sync"
                            status_color = COLORS["text_muted"] if conn["enabled"] else COLORS["border"]
                            status_lbl = ui.label(status_text).style(
                                f"font-size:11px; color:{status_color}"
                            )
                            label_refs["status"] = status_lbl

                        # ── Right: toggle ───────────────────────
                        with ui.element("div").style(
                            "display:flex; flex-direction:column; align-items:center; gap:4px; flex-shrink:0"
                        ):
                            sw = ui.switch(value=conn["enabled"]).props("color=positive keep-color")
                            sw.style("margin:0")

                            enabled_lbl = ui.label("ON" if conn["enabled"] else "OFF").style(
                                f"font-size:9px; font-weight:700; letter-spacing:0.1em; "
                                f"color:{COLORS['positive'] if conn['enabled'] else COLORS['text_muted']}"
                            )
                            label_refs["enabled"] = enabled_lbl

                    def _on_change(
                        e,
                        name=conn["name"],
                        d=dot_refs,
                        l=label_refs,
                    ):
                        on_toggle(name, e.value)
                        active = e.value
                        d["dot"].style(
                            f"width:7px; height:7px; border-radius:50%; flex-shrink:0; "
                            f"background:{COLORS['positive'] if active else COLORS['border']}; "
                            f"transition:background 0.2s ease"
                        )
                        l["status"].set_text(
                            "Active — will be included in next sync" if active
                            else "Inactive — excluded from sync"
                        )
                        l["status"].style(
                            f"font-size:11px; color:{COLORS['text_muted'] if active else COLORS['border']}"
                        )
                        l["enabled"].set_text("ON" if active else "OFF")
                        l["enabled"].style(
                            f"font-size:9px; font-weight:700; letter-spacing:0.1em; "
                            f"color:{COLORS['positive'] if active else COLORS['text_muted']}"
                        )
                        ui.notify(
                            f"{'Enabled' if active else 'Disabled'} {name}. Sync to apply.",
                            type="positive" if active else "warning",
                            timeout=2500,
                        )

                    sw.on_value_change(_on_change)

            # ── Future connections ──────────────────────────────
            with ui.element("div").style("margin-top:40px"):
                _section_label("Add Connection")

                with ui.element("div").style(
                    f"border:1px dashed {COLORS['border']}; padding:28px 24px; "
                    f"display:flex; align-items:center; justify-content:space-between"
                ):
                    with ui.element("div"):
                        ui.label("Connect a real bank or broker").style(
                            f"font-size:14px; font-weight:500; color:{COLORS['text_secondary']}"
                        )
                        ui.label(
                            "Real connectors require API credentials from your financial institution. "
                            "Implement a BankConnector subclass and register it in app.py."
                        ).style(
                            f"font-size:12px; color:{COLORS['text_muted']}; "
                            f"margin-top:4px; max-width:520px; line-height:1.6"
                        )

                    ui.button("Coming Soon").props("unelevated flat dense").style(
                        f"color:{COLORS['border']} !important; background:transparent !important; "
                        f"border:1px solid {COLORS['border_light']}; border-radius:0; "
                        f"font-size:10px; letter-spacing:0.06em; height:28px; padding:0 14px; "
                        f"cursor:default; flex-shrink:0"
                    )
